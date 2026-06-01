import os
from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger

BASELINE_PROMPT = """Bạn là trợ lý tư vấn tuyển sinh của Đại học VinUni (Vingroup University).
Trả lời câu hỏi về tuyển sinh khóa đầu tiên dựa trên kiến thức của bạn.
Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
Nếu không chắc chắn, hãy nói rõ thay vì bịa đặt."""


def run_baseline(question: str) -> str:
    """Chatbot cơ bản: gọi LLM trực tiếp, không dùng tool."""
    provider = OpenAIProvider(
        model_name="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    logger.log_event("CHATBOT_START", {"input": question})
    result = provider.generate(question, system_prompt=BASELINE_PROMPT)
    logger.log_event("CHATBOT_END", {
        "latency_ms": result["latency_ms"],
        "tokens": result["usage"].get("total_tokens", 0),
    })
    return result["content"]
