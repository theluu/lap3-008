import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ReActAgent:
    """ReAct-style Agent: Thought → Action → Observation loop."""

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []
        self.last_run_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "cost": 0.0, "steps": 0}

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        return f"""Bạn là trợ lý tư vấn tuyển sinh của Đại học VinUni (Vingroup University).
Nhiệm vụ: trả lời câu hỏi về tuyển sinh khóa đầu tiên dựa trên dữ liệu thực tế.

Tools có sẵn:
{tool_descriptions}

Định dạng BẮT BUỘC (phải tuân thủ nghiêm):
Thought: [suy nghĩ của bạn]
Action: tool_name(argument)
Observation: [kết quả tool — do hệ thống điền]
... (lặp lại nếu cần)
Final Answer: [câu trả lời cuối cùng bằng tiếng Việt]

Ví dụ:
Thought: Người dùng hỏi về học bổng. Tôi cần tìm thông tin học bổng.
Action: search_vinuni_info(học bổng VinUni)
Observation: [hệ thống trả về]
Final Answer: VinUni cung cấp các loại học bổng sau...

Quy tắc:
- Luôn dùng tool trước khi trả lời.
- Final Answer phải bằng tiếng Việt.
- Nếu không tìm được thông tin, nói thật thay vì bịa.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        # Reset per-run usage
        self.last_run_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "cost": 0.0, "steps": 0}

        current_prompt = user_input
        steps = 0
        parse_retries = 0
        MAX_PARSE_RETRIES = 2
        valid_tools = [t["name"] for t in self.tools]

        while steps < self.max_steps:
            try:
                result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
                response = result["content"]

                # Track token usage mỗi LLM call
                usage = result.get("usage", {})
                cost = tracker._calculate_cost(self.llm.model_name, usage)
                tracker.track_request(
                    provider=result.get("provider", "openai"),
                    model=self.llm.model_name,
                    usage=usage,
                    latency_ms=result.get("latency_ms", 0),
                )
                self.last_run_usage["prompt_tokens"]     += usage.get("prompt_tokens", 0)
                self.last_run_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                self.last_run_usage["total_tokens"]      += usage.get("total_tokens", 0)
                self.last_run_usage["cost"]              += cost
                self.last_run_usage["steps"]              = steps + 1

                logger.log_event("LLM_RESPONSE", {"step": steps, "response": response[:300], "tokens": usage.get("total_tokens", 0)})

                # Final Answer found → done
                if "Final Answer:" in response:
                    answer = response.split("Final Answer:")[-1].strip()
                    logger.log_event("AGENT_END", {"steps": steps, "result": "success"})
                    return answer

                # Parse Action
                action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response, re.DOTALL)
                if action_match:
                    tool_name = action_match.group(1).strip()
                    tool_args = action_match.group(2).strip().strip("\"'")

                    # GUARDRAIL: validate tool name trước khi gọi
                    if tool_name not in valid_tools:
                        logger.log_event("HALLUCINATION_ERROR", {
                            "requested_tool": tool_name,
                            "valid_tools": valid_tools,
                        })
                        observation = (
                            f"Tool '{tool_name}' không tồn tại. "
                            f"Chỉ được dùng: {valid_tools}"
                        )
                    else:
                        observation = self._execute_tool(tool_name, tool_args)

                    current_prompt = f"{current_prompt}\n{response}\nObservation: {observation}"
                    parse_retries = 0

                else:
                    parse_retries += 1
                    logger.log_event("PARSE_ERROR", {"step": steps, "retry": parse_retries})

                    if parse_retries >= MAX_PARSE_RETRIES:
                        logger.log_event("AGENT_END", {"steps": steps, "result": "parse_fail"})
                        return response  # best-effort: trả raw output

                    current_prompt = (
                        f"{current_prompt}\n{response}\n"
                        "Observation: Format sai. Bắt buộc dùng:\n"
                        "  Action: tool_name(argument)\n"
                        "hoặc:\n"
                        "  Final Answer: câu trả lời"
                    )

            except Exception as e:
                logger.error(f"Agent error at step {steps}: {e}")
                logger.log_event("AGENT_ERROR", {"step": steps, "error": str(e)})
                return f"Lỗi hệ thống: {str(e)}"

            steps += 1

        logger.log_event("AGENT_END", {"steps": steps, "result": "max_steps_reached"})
        return "Xin lỗi, tôi không tìm được câu trả lời trong số bước cho phép."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    return tool["func"](args)
                except Exception as e:
                    logger.error(f"Tool '{tool_name}' error: {e}", exc_info=True)
                    return f"Lỗi khi chạy tool '{tool_name}': {str(e)}"
        valid = [t["name"] for t in self.tools]
        logger.log_event("TOOL_NOT_FOUND", {"requested": tool_name, "available": valid})
        return f"Tool '{tool_name}' không tồn tại. Các tool hợp lệ: {valid}"
