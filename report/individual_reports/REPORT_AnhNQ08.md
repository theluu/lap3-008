# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Nguyễn Quang Anh
- **MSSV**: 2A202600608
- **Lớp**: C401
- **Ngày**: 6/1/2026
- **Nhánh thực hiện**: AnhNQ-2A202600608

---

## I. ĐÓNG GÓP KỸ THUẬT (Technical Contribution - 15 Điểm)

Với vai trò là thành viên xây dưng UI/UX & Evaluation Engineer, tôi đã chịu trách nhiệm thiết kế toàn bộ giao diện tương tác và bộ kiểm thử đánh giá hệ thống. Dưới đây là các phần việc cụ thể đã hoàn thành:

### 1. Các Module đã triển khai
*   **[src/ui/app.py](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/src/ui/app.py)**: Xây dựng giao diện Chatbot bằng thư viện Streamlit, tích hợp bộ đo lường hiệu năng thời gian thực và tab Kiến trúc hệ thống trực quan.
*   **[tests/test_vinuni_agent.py](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/tests/test_vinuni_agent.py)**: Thiết lập bộ 23 kịch bản kiểm thử tự động toàn diện để kiểm tra chất lượng kết quả tìm kiếm thông tin tuyển sinh.
*   **[docs/evaluation_results.md](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/docs/evaluation_results.md)**: Viết báo cáo phân tích đối chiếu hiệu năng chi tiết giữa Chatbot thường và ReAct Agent (v1 và v2).

---

### 2. Điểm sáng trong mã nguồn (Code Highlights)

#### A. Thiết kế Giao diện Đẹp và Theo dõi Hiệu năng Thời gian thực (Real-time Metrics)
Tôi đã tùy chỉnh mã nguồn của ứng dụng Streamlit để đo đạc và hiển thị chi tiết lượng Token, Chi phí ($) tích lũy, số bước chạy (Steps) và Độ trễ (Latency) ngay dưới mỗi câu trả lời của trợ lý ảo:
```python
# Đo đạc hiệu năng và cộng dồn vào Session State của Streamlit
with st.chat_message("assistant"):
    with st.spinner("Đang tìm kiếm..."):
        t0 = time.time()
        agent = get_agent(prov, mod, api_key=key)
        response = agent.run(prompt)
        elapsed_ms = int((time.time() - t0) * 1000)
        usage = agent.last_run_usage
        
        # Cộng dồn số liệu để hiển thị trên Sidebar thống kê toàn bộ phiên
        st.session_state.latencies.append(elapsed_ms)
        st.session_state.total_tokens += usage["total_tokens"]
        st.session_state.total_cost   += usage["cost"]
    
    st.write(response)
    # Hiển thị caption chi tiết công nghiệp dưới mỗi câu chat
    st.caption(
        f"⏱ {elapsed_ms} ms · "
        f"🔢 {usage['total_tokens']:,} tokens "
        f"({usage['prompt_tokens']:,} in / {usage['completion_tokens']:,} out) · "
        f"💰 ${usage['cost']:.4f} · "
        f"🔄 {usage['steps']} steps"
    )
```

#### B. Tùy chỉnh Giao diện Premium (CSS & JS Injection)
Để ứng dụng có giao diện sạch sẽ, chuyên nghiệp, tôi sử dụng script Javascript chèn ngầm để ẩn nút "Deploy" mặc định của Streamlit và ẩn các menu cấu hình không liên quan:
```python
# Ẩn nút Deploy thừa của Streamlit
import streamlit.components.v1 as components
components.html(
    """
    <script>
    const hide = () => {
        const doc = window.parent.document;
        doc.querySelectorAll('header button').forEach(b => {
            if (b.innerText.trim() === 'Deploy') b.style.display = 'none';
        });
    };
    hide();
    new MutationObserver(hide).observe(
        window.parent.document.body,
        { childList: true, subtree: true }
    );
    </script>
    """,
    height=0,
)
```

#### C. Viết bộ kiểm thử chuẩn hóa Tiếng Việt (Unicode Normalization)
Trong bộ test case tự động, để tránh việc test bị lỗi khi người dùng nhập câu hỏi không dấu hoặc sai chuẩn gõ dấu tiếng Việt (ví dụ: `Hòa` vs `Hoà`), tôi đã triển khai hàm chuẩn hóa đưa toàn bộ văn bản về dạng không dấu trước khi so khớp từ khóa:
```python
def _normalize_result(text: str) -> str:
    """Bỏ dấu tiếng Việt và chuẩn hóa chữ thường để tăng độ chính xác khi đối chiếu."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def result_contains_any(result: str, keywords: list) -> bool:
    result_norm = _normalize_result(result)
    return any(kw.lower() in result_norm for kw in keywords)
```

---

### 3. Tương tác với ReAct Loop
Giao diện UI do tôi xây dựng đóng vai trò là "lớp vỏ" bao bọc và điều phối. Mỗi khi người dùng chọn một **LLM Provider** mới (OpenAI/Gemini/Local) hoặc thay đổi **Model** hay nhập **API Key** mới tại sidebar, Streamlit sẽ nhận diện sự thay đổi này qua Session State và tự động khởi tạo lại một đối tượng `ReActAgent` tương ứng. Việc này giúp quá trình kiểm thử của nhóm diễn ra vô cùng nhanh chóng mà không cần mở code sửa file `.env`.

---

## II. PHÂN TÍCH LỖI & SỬA LỖI (Debugging Case Study - 10 Điểm)

### 1. Mô tả lỗi hệ thống
Trong quá trình chạy thử nghiệm số lượng lớn (kiểm thử 20 câu hỏi tự động liên tục), hệ thống đột ngột bị dừng hoạt động hoặc Agent phản hồi các thông điệp báo lỗi hệ thống chung chung (`Lỗi hệ thống: Error code: 429...`).

---

### 2. Vết lỗi trích xuất từ Log
Khi mở file log hệ thống [logs/2026-06-01.log](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/logs/2026-06-01.log#L21-L22), tôi phát hiện ra vết lỗi sau:
```json
{"timestamp": "2026-06-01T06:57:01.529831", "event": "AGENT_ERROR", "data": {"step": 0, "error": "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details...', 'type': 'insufficient_quota', 'code': 'insufficient_quota'}}"}}
```
Sau đó, log ghi nhận thêm lỗi:
```json
{"timestamp": "2026-06-01T07:23:20.619488", "event": "AGENT_ERROR", "data": {"step": 0, "error": "Error code: 401 - {'error': {'message': 'Incorrect API key provided...', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}}}}
```

---

### 3. Chẩn đoán nguyên nhân (Diagnosis)
1.  **Lỗi 429**: Khóa API mặc định của OpenAI đặt trong file `.env` đã vượt quá hạn mức sử dụng (hết tiền/hết dung lượng thử nghiệm).
2.  **Lỗi 401**: Do API Key bị sai hoặc không hợp lệ.
3.  **Hệ quả**: Do mã nguồn cũ thiết lập cứng (hardcode) chỉ dùng `OpenAIProvider`, nên khi khóa OpenAI bị khóa/hết hạn, toàn bộ chatbot bị tê liệt và crash, không thể chuyển sang dùng mô hình khác để test tiếp.

---

### 4. Giải pháp khắc phục (Solution)
Để khắc phục triệt để lỗi này và tăng tính bền vững của dự án, tôi đã:
1.  Đồng thiết kế và triển khai một hàm **Provider Factory** (`get_provider()`) nằm trong file `src/core/llm_provider.py` để khởi tạo linh hoạt các Provider dựa trên lựa chọn.
2.  Tích hợp các **hộp nhập khóa API trực tiếp (API Key Inputs) tại sidebar** cho cả OpenAI và Gemini.
3.  Khi người dùng nhập khóa API mới trực tiếp trên màn hình, ứng dụng sẽ ghi đè khóa cũ trong `.env` và truyền thẳng vào constructor của `OpenAIProvider` hoặc `GeminiProvider`. Nhờ đó, người dùng có thể dễ dàng chuyển sang dùng **Gemini** khi khóa OpenAI bị lỗi 429 mà không cần khởi động lại máy hay chỉnh sửa mã nguồn.

---

## III. NHẬN XÉT CÁ NHÂN: CHATBOT VS REACT AGENT (10 Điểm)

### 1. Vai trò của khối suy nghĩ (Thought)
Khối suy nghĩ `Thought` hoạt động như một "phân vùng nháp" (scratchpad) cho LLM. So với việc Chatbot thường phải đưa ra câu trả lời ngay lập tức bằng trực giác (dễ gây ra ảo tưởng số liệu), `Thought` giúp Agent phân tích yêu cầu, tự lên kế hoạch (ví dụ: *"Tôi cần tìm kiếm học phí của khối ngành kỹ thuật trước"*), chọn công cụ phù hợp, rồi mới đưa ra câu trả lời. Điều này cải thiện đáng kể tính chính xác và logic của câu trả lời cuối cùng.

---

### 2. Sự đánh đổi về độ tin cậy và hiệu năng (Reliability vs Performance)
Mặc dù Agent thông minh hơn và đáng tin cậy hơn, hiệu năng của nó có sự đánh đổi lớn:
*   **Tốc độ**: Chatbot Baseline phản hồi cực nhanh (chỉ mất ~1.2 giây do chỉ gọi LLM đúng 1 lần). Agent mất trung bình ~4.8 giây do phải lặp qua nhiều bước (Thought -> Action -> Observation).
*   **Chi phí**: Chatbot tiêu tốn trung bình ~650 tokens mỗi câu hỏi. Agent tiêu tốn trung bình ~4,100 tokens (gấp hơn 6 lần) do lịch sử hội thoại bị phình to qua mỗi lượt gọi tool.
*   **Nhận xét**: Đối với các câu hỏi xã giao thông thường ("Xin chào", "Bạn khỏe không"), Agent chạy tệ hơn Chatbot vì lãng phí tài nguyên và thời gian không cần thiết. Agent chỉ thực sự phát huy tác dụng với các câu hỏi phức tạp, cần tra cứu dữ liệu động.

---

### 3. Tác động từ phản hồi môi trường (Observation)
Phản hồi môi trường `Observation` chính là nhân tố quyết định các bước đi tiếp theo của Agent. Nếu kết quả tìm kiếm trả về thông tin hữu ích, Agent sẽ tổng hợp và kết thúc bằng `Final Answer`. Ngược lại, nếu `Observation` trả về trống hoặc thông báo lỗi, Agent sẽ nhận biết được thông tin đó sai/thiếu và tự động đổi từ khóa tìm kiếm ở bước tiếp theo để thử lại, thay vì bịa đặt câu trả lời.

---

## IV. ĐỀ XUẤT CẢI TIẾN TƯƠNG LAI (Future Improvements - 5 Điểm)

Để đưa hệ thống Agent này lên mức độ thương mại (Production-ready), tôi đề xuất 3 cải tiến sau:

1.  **Hiệu năng (Performance - Vector DB)**: Hiện tại công cụ tìm kiếm đang tách từ đơn giản bằng `split()` và so khớp từ khóa thô. Cần chuyển sang công nghệ **Tìm kiếm ngữ nghĩa (Semantic Search)** sử dụng mô hình Embedding và Cơ sở dữ liệu Vector (như Pinecone hoặc ChromaDB) để Agent có thể hiểu được ý định sâu xa của câu hỏi ngay cả khi người dùng dùng từ đồng nghĩa.
2.  **Độ an toàn (Safety - Guardrails & Supervisor)**: Bổ sung thêm một lớp **Supervisor Agent** (LLM thứ hai) làm nhiệm vụ kiểm duyệt và lọc đầu ra của Agent trước khi hiển thị cho người dùng, giúp ngăn chặn các cuộc tấn công tiêm mã độc (prompt injection) hoặc lọc các câu trả lời nhạy cảm.
3.  **Khả năng mở rộng (Scalability - Async Queue)**: Chuyển đổi cơ chế gọi tool sang xử lý bất đồng bộ sử dụng hàng đợi (ví dụ: Celery + Redis). Điều này giúp hệ thống phục vụ được hàng ngàn người dùng truy vấn đồng thời mà không bị nghẽn luồng xử lý của hệ thống.
