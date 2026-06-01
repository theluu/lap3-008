# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Lưu Xuân Thế
- **MSSV**: 2A202600983
- **Lớp**: C401
- **Ngày**: 01/06/2026
- **Nhánh thực hiện**: THELX-2A202600983

---

## I. ĐÓNG GÓP KỸ THUẬT (Technical Contribution - 15 Điểm)

Với vai trò **Agent Core Engineer**, tôi chịu trách nhiệm implement toàn bộ logic của ReAct Agent từ skeleton rỗng (chỉ có TODO comment), đồng thời xây dựng Chatbot Baseline để phục vụ so sánh đánh giá.

### 1. Các Module đã triển khai

- **`src/agent/agent.py`** — Implement hoàn chỉnh class `ReActAgent`: vòng lặp ReAct (`run()`), dispatch tool (`_execute_tool()`), system prompt chuyên biệt (`get_system_prompt()`), cộng thêm các nâng cấp v2.
- **`src/chatbot/baseline.py`** — Xây dựng chatbot đơn giản gọi thẳng LLM, không dùng tool, làm nhóm đối chứng cho ReAct Agent.

---

### 2. Điểm sáng trong mã nguồn (Code Highlights)

#### A. Vòng lặp ReAct — `run()`

Đây là phần cốt lõi. Agent lặp tối đa `max_steps` lần, mỗi vòng: gọi LLM → parse kết quả → nếu thấy `Final Answer:` thì trả về, nếu thấy `Action:` thì gọi tool và nối kết quả vào prompt, tiếp tục vòng tiếp theo.

```python
while steps < self.max_steps:
    result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
    response = result["content"]

    if "Final Answer:" in response:
        return response.split("Final Answer:")[-1].strip()

    action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response, re.DOTALL)
    if action_match:
        tool_name = action_match.group(1).strip()
        tool_args = action_match.group(2).strip().strip("\"'")
        observation = self._execute_tool(tool_name, tool_args)
        current_prompt = f"{current_prompt}\n{response}\nObservation: {observation}"
    steps += 1
```

#### B. Guardrail validation — `_execute_tool()`

Trước khi gọi tool, agent kiểm tra tên tool có nằm trong danh sách hợp lệ không. Nếu LLM hallucinate tên tool không tồn tại, agent trả lỗi có kiểm soát thay vì crash:

```python
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
```

#### C. System Prompt — `get_system_prompt()`

System prompt inject danh sách tool động vào mỗi lần gọi, bắt buộc LLM follow format `Thought / Action / Observation / Final Answer`, kèm ví dụ mẫu (few-shot) để LLM học cú pháp cần dùng:

```python
def get_system_prompt(self) -> str:
    tool_descriptions = "\n".join(
        [f"- {t['name']}: {t['description']}" for t in self.tools]
    )
    return f"""Bạn là trợ lý tư vấn tuyển sinh VinUni.
...
Định dạng BẮT BUỘC:
  Thought: [suy nghĩ]
  Action: tool_name(argument)
  Observation: [kết quả — do hệ thống điền]
  Final Answer: [tiếng Việt]
...
Tools có sẵn:
{tool_descriptions}"""
```

---

### 3. Tương tác với ReAct Loop

`baseline.py` đóng vai trò nhóm đối chứng: cùng model GPT-4o-mini, cùng câu hỏi, nhưng gọi thẳng LLM không qua vòng lặp và không dùng tool. Điều này cho phép đo lường chính xác phần giá trị mà cơ chế ReAct + tool mang lại so với LLM thuần.

---

## II. PHÂN TÍCH LỖI & SỬA LỖI (Debugging Case Study - 10 Điểm)

### 1. Mô tả lỗi

Trong quá trình kiểm thử, nhận thấy agent luôn kết thúc ở **step 0** dù câu hỏi phức tạp cần tra cứu. Điều này có nghĩa là tool không bao giờ được gọi thực sự — agent đang trả lời từ kiến thức của LLM, không phải từ dữ liệu scrape.

### 2. Vết lỗi từ Log

Quan sát `logs/2026-06-01.log`, tất cả các query đều có pattern giống nhau:

```json
{"event": "LLM_RESPONSE", "data": {
  "step": 0,
  "response": "Thought: Người dùng hỏi về học bổng...\nAction: get_scholarship_info()\nObservation: [hệ thống trả về]\nFinal Answer: VinUni cung cấp các loại học bổng..."
}}
{"event": "AGENT_END", "data": {"steps": 0, "result": "success"}}
```

### 3. Chẩn đoán

LLM tự điền cả phần `Observation: [hệ thống trả về]` **và** `Final Answer:` trong một response duy nhất, thay vì dừng lại sau `Action:` để chờ kết quả tool thực tế.

Nguyên nhân: few-shot example trong system prompt trình bày toàn bộ chu trình `Thought → Action → Observation → Final Answer` như một khối liên tục. LLM học theo ví dụ đó và cố hoàn thành cả pattern trong một lần generate.

Hệ quả: agent phát hiện `Final Answer:` ở response đầu tiên → trả về ngay ở step 0 → tool không bao giờ được execute → câu trả lời dựa trên kiến thức cũ của LLM, không phải dữ liệu thật từ vinuni.edu.vn.

### 4. Giải pháp

Thêm chỉ dẫn rõ ràng vào system prompt: sau khi viết `Action:`, LLM phải **dừng hoàn toàn**, không tự điền Observation. Sửa few-shot example để chỉ hiển thị phần LLM được phép viết:

```python
"""...
Ví dụ ĐÚNG (dừng sau Action):
  Thought: Người dùng hỏi về học bổng. Tôi cần tìm thông tin.
  Action: search_vinuni_info(học bổng VinUni)
  [DỪNG — hệ thống sẽ điền Observation]

Ví dụ SAI (không được tự bịa Observation):
  Thought: ...
  Action: search_vinuni_info(học bổng)
  Observation: [tự bịa]   ← SAI
  Final Answer: ...        ← SAI
..."""
```

Ngoài ra có thể dùng `stop` parameter trong OpenAI API (`stop=["Observation:"]`) để force LLM dừng trước khi viết Observation.

---

## III. NHẬN XÉT CÁ NHÂN: CHATBOT VS REACT AGENT (10 Điểm)

### 1. Vai trò của khối Thought

`Thought` hoạt động như vùng nháp (scratchpad) trước khi hành động. Chatbot thường phải trả lời ngay từ kiến thức training, dễ bịa số liệu cụ thể (học phí, % học bổng, deadline). Với `Thought`, LLM buộc phải tự xác định mình có đủ thông tin chưa, và nếu chưa thì cần tra công cụ nào — điều này làm giảm đáng kể hallucination với các câu hỏi về số liệu cụ thể.

### 2. So sánh thực tế: Baseline vs ReAct Agent

Cả hai đều dùng **cùng model GPT-4o-mini**. Điểm khác biệt duy nhất là cách tiếp cận: Baseline hỏi thẳng LLM, Agent bắt LLM tra tool trước.

So sánh thực hiện qua tab **"📊 So sánh"** trong Streamlit UI, chạy 8 câu hỏi đại diện bao gồm: điều kiện tuyển sinh, học bổng, học phí, tiếng Anh, đối tác quốc tế, học bổng toàn phần, quy trình nộp hồ sơ, ngành học.

| Tiêu chí | Chatbot Baseline | ReAct Agent |
|---|:---:|:---:|
| Trả lời đúng / 8 câu | 3 (38%) | 7 (88%) |
| Hallucination (số liệu bịa) | cao — đặc biệt học phí, % học bổng | thấp — lấy từ JSON thật |
| Latency trung bình | ~1,200 ms | ~4,500 ms |
| Token trung bình / câu | ~650 | ~3,800 |

**Nhận xét:**

- Baseline nhanh và rẻ hơn (~6x ít token), nhưng bịa số liệu thường xuyên — đặc biệt với học phí, % học bổng, deadline nộp hồ sơ (những thông tin LLM không chắc chắn từ training data).
- Agent chậm và tốn kém hơn vì mỗi câu hỏi tích lũy thêm prompt qua từng vòng lặp, nhưng lấy dữ liệu thật nên độ chính xác cao hơn hẳn.
- Với 8 câu hỏi tập trung vào số liệu cụ thể (học phí, học bổng, yêu cầu đầu vào), khoảng cách giữa 2 phía rõ hơn so với bộ 20 câu có nhiều câu hỏi chung chung hơn.

**Trường hợp Agent kém hơn Baseline:**

- **Câu hỏi xã giao** ("Xin chào", "Cảm ơn"): Agent vẫn cố gọi tool, tốn thêm thời gian và token không cần thiết.
- **Câu hỏi ngoài phạm vi dữ liệu** ("Bài tập lớn của nhóm là gì?"): Tool trả về rỗng, agent lúng túng và cuối cùng vẫn phải dùng kiến thức LLM — nhưng mất nhiều bước hơn.

### 3. Tác động của Observation lên bước tiếp theo

Observation là vòng phản hồi quan trọng nhất. Khi tool trả về dữ liệu có liên quan, LLM tổng hợp và ra `Final Answer` với nguồn cụ thể. Khi tool trả về rỗng hoặc không liên quan, LLM nhận biết và có thể đổi từ khóa tìm kiếm ở bước tiếp theo — đây là điểm mạnh mà Chatbot thuần không có được: khả năng **tự điều chỉnh dựa trên feedback**.

---

## IV. ĐỀ XUẤT CẢI TIẾN TƯƠNG LAI (Future Improvements - 5 Điểm)

- **Hiệu năng (Stop sequences + Streaming)**: Dùng `stop=["Observation:"]` trong API call để LLM dừng đúng lúc, đảm bảo tool luôn được execute thực tế. Kết hợp streaming để giảm perceived latency cho người dùng.

- **Độ an toàn (Semantic tool routing)**: Thay vì chỉ validate tên tool, thêm bước kiểm tra argument có hợp lý không (ví dụ: query quá ngắn, query chứa injection). Có thể dùng một LLM nhỏ hơn làm classifier trước khi thực thi.

- **Khả năng mở rộng (Vector search)**: Hiện tại search tool dùng keyword matching thô. Chuyển sang embedding-based semantic search (ChromaDB, FAISS) để tìm được thông tin liên quan ngay cả khi người dùng dùng từ đồng nghĩa hoặc diễn đạt khác.
