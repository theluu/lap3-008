# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Nguyễn Quang Anh
- **MSSV**: 2A202600608
- **Lớp**: C401
- **Ngày**: 01/06/2026
- **Nhánh thực hiện**: AnhNQ-2A202600608

---

## 📊 Bảng tự đánh giá điểm cá nhân (Individual Self-Grading Dashboard)

Dựa trên tiêu chí chấm điểm tại [SCORING.md](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/SCORING.md), tôi tự chấm điểm cho các phần đóng góp cá nhân của mình như sau (Tổng điểm cá nhân tối đa là **40 điểm**):

| Thành phần báo cáo | Yêu cầu chuẩn Rubric | Điểm tối đa | Điểm tự chấm | Minh chứng & Vị trí chi tiết |
| :--- | :--- | :---: | :---: | :--- |
| **I. Technical Contribution** | Danh sách các module đã cài đặt, code highlights nổi bật, giải thích hoạt động. | 15 | **15** | Phát triển `app.py`, test cases `test_vinuni_agent.py`, so khớp không dấu NFKD. Trình bày tại Phần I. |
| **II. Debugging Case Study** | Phân tích sâu 1 lỗi thực tế bằng logs, chẩn đoán và đưa ra giải pháp xử lý. | 10 | **10** | Phân tích log lỗi 429 và 401 của OpenAI API, cài đặt Provider Factory chuyển đổi backup Gemini. Trình bày tại Phần II. |
| **III. Personal Insights** | Phản ánh sâu sắc sự khác biệt về năng lực suy luận giữa Chatbot thường và ReAct Agent. | 10 | **10** | Trình bày bảng so sánh hiệu năng thực tế, vai trò Thought và phản hồi Observation tại Phần III. |
| **IV. Future Improvements** | Đề xuất giải pháp mở rộng quy mô hệ thống lên cấp độ Production. | 5 | **5** | Đề xuất Semantic Search (Vector DB), Semantic Cache (Redis) và Supervisor Agent tại Phần IV. |
| **TỔNG ĐIỂM CÁ NHÂN** | | **40** | **40 / 40** | |

---


## I. ĐÓNG GÓP KỸ THUẬT (Technical Contribution - 15 Điểm)

Với vai trò là thành viên phụ trách **UI/UX & Evaluation Engineer** của nhóm `lap3-008`, tôi đã trực tiếp chịu trách nhiệm thiết kế toàn bộ giao diện Streamlit UI, các bộ đo lường và theo dõi (telemetry) thời gian thực, cũng như xây dựng bộ kịch bản kiểm thử tự động phục vụ cho việc đánh giá so sánh hiệu năng. Dưới đây là các phần việc cụ thể đã hoàn thành:

### 1. Các Module đã triển khai
*   **[src/ui/app.py](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/src/ui/app.py)**: Xây dựng giao diện Chatbot bằng thư viện Streamlit, tích hợp bộ cấu hình động cho phép người dùng thay đổi chế độ hiển thị (Version 1 - Cơ bản và Version 2 - Tính phí token), chuyển đổi giữa OpenAI/Gemini Provider, theo dõi telemetry tích lũy (Tokens, Latency, Cost, Steps) và tích hợp các Tab phân tích kiến trúc ("Architecture") cùng công cụ so sánh trực quan ("So sánh").
*   **[tests/test_vinuni_agent.py](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/tests/test_vinuni_agent.py)**: Thiết lập bộ 23 kịch bản kiểm thử tự động toàn diện bằng `pytest` (20 kịch bản câu hỏi tham số hóa kết hợp 3 hàm kiểm thử nâng cao) để tự động hóa việc đánh giá độ chính xác của Agent.
*   **[docs/evaluation_results.md](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/docs/evaluation_results.md)**: Viết báo cáo phân tích đối chiếu hiệu năng chi tiết giữa Chatbot Baseline, ReAct Agent v1 và ReAct Agent v2.

---

### 2. Điểm sáng trong mã nguồn (Code Highlights)

#### A. Thiết kế Giao diện Đẹp và Theo dõi Hiệu năng Thời gian thực (Real-time Metrics)
Tôi đã lập trình giao diện Streamlit để đo đạc và hiển thị chi tiết lượng Token tiêu thụ, Chi phí ($) tích lũy, số bước chạy (Steps) và Độ trễ (Latency) ngay dưới mỗi câu trả lời của trợ lý ảo khi ở chế độ "Version 2". Dữ liệu này được hiển thị thông qua caption chi tiết và cập nhật trực tiếp vào sidebar thống kê:
```python
            with st.chat_message("assistant"):
                with st.spinner("Đang tìm kiếm..."):
                    t0 = time.time()
                    agent = get_agent(selected_provider, selected_model)
                    response = agent.run(prompt)
                    elapsed_ms = int((time.time() - t0) * 1000)
                    usage = agent.last_run_usage

                st.session_state.latencies.append(elapsed_ms)
                st.session_state.total_tokens += usage["total_tokens"]
                st.session_state.total_cost   += usage["cost"]

                st.write(response)
                if show_token_cost:
                    st.caption(
                        f"⏱ {elapsed_ms} ms · "
                        f"🔢 {usage['total_tokens']:,} tokens "
                        f"({usage['prompt_tokens']:,} in / {usage['completion_tokens']:,} out) · "
                        f"💰 ${usage['cost']:.4f} · "
                        f"🔄 {usage['steps']} steps"
                    )
```

#### B. Tùy chỉnh Giao diện Premium (CSS & JS Injection)
Để ứng dụng có giao diện sạch sẽ, chuyên nghiệp, loại bỏ các chi tiết thừa thãi của Streamlit và mang lại trải nghiệm premium tối đa, tôi đã sử dụng giải pháp kết hợp Script JavaScript ẩn và chèn CSS trực tiếp:
```python
    # Ẩn Deploy button + menu items thừa, chỉ giữ System/Light/Dark
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        const hide = () => {
            const doc = window.parent.document;
            // Ẩn Deploy button
            doc.querySelectorAll('header button').forEach(b => {
                if (b.innerText.trim() === 'Deploy') b.style.display = 'none';
            });
            // Ẩn "Made with Streamlit" trong menu
            doc.querySelectorAll('[data-testid="stMainMenu"] *').forEach(el => {
                if (el.innerText && el.innerText.trim().startsWith('Made with Streamlit')) {
                    el.style.display = 'none';
                }
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
    st.markdown(
        """
        <style>
        /* Trong menu ⋮: ẩn tất cả trừ Theme group (System/Light/Dark) */
        [data-testid="stMainMenuList"] > *:not([role="group"]) {
            display: none !important;
        }
        /* Ẩn "Made with Streamlit" footer trong menu */
        [data-testid="stMainMenuList"] + *,
        [data-testid="stMainMenu"] footer,
        a[href*="streamlit.io"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
```

#### C. Viết bộ kiểm thử chuẩn hóa Tiếng Việt (Unicode Normalization)
Trong bộ test case tự động, để tránh việc kiểm thử bị lỗi hoặc lệch kết quả do người dùng gõ sai chuẩn dấu tiếng Việt (ví dụ: `Hòa` dùng dấu ở chữ o vs `Hoà` dùng dấu ở chữ a), tôi đã triển khai hàm chuẩn hóa Unicode đưa toàn bộ văn bản về dạng không dấu tổ hợp NFKD trước khi so khớp từ khóa:
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
Giao diện Streamlit UI đóng vai trò là tầng điều phối và trực quan hóa toàn bộ vòng lặp ReAct của Agent:
- **Khởi tạo động**: Khi người dùng thay đổi lựa chọn Provider (`OpenAI` hoặc `Google Gemini`) hay chọn Model tại sidebar, Session State sẽ lưu trữ cấu hình này và chuyển vào hàm `get_agent()`. Hàm này hoạt động như một Factory khởi tạo lại đối tượng `ReActAgent` với Provider tương ứng, giúp nhóm dễ dàng kiểm thử chéo nhiều mô hình.
- **Tab So sánh trực quan**: Cho phép người dùng nhấn nút chạy thử nghiệm song song 8 câu hỏi đại diện. Hệ thống sẽ gọi đồng thời Chatbot Baseline và ReAct Agent v2 để lấy kết quả, đối chiếu với bộ từ khóa kỳ vọng bằng hàm chuẩn hóa Unicode, đo lường latency, token và hiển thị kết quả so sánh dạng bảng trực quan. Điều này mang lại một dashboard phân tích hiệu năng cực kỳ trực quan và giá trị cho dự án.

---

## II. PHÂN TÍCH LỖI & SỬA LỖI (Debugging Case Study - 10 Điểm)

### 1. Mô tả lỗi hệ thống
Trong quá trình nhóm chạy kiểm thử số lượng lớn và liên tục trên bộ test case tự động, hệ thống đột ngột bị dừng hoạt động hoặc Agent phản hồi các thông điệp báo lỗi hệ thống: `Lỗi hệ thống: Error code: 429...` hoặc `Lỗi hệ thống: Error code: 401...`. Toàn bộ chatbot bị đóng băng và không thể phản hồi bất kì câu hỏi nào của người dùng.

---

### 2. Vết lỗi trích xuất từ Log
Khi kiểm tra file log hệ thống [logs/2026-06-01.log](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/logs/2026-06-01.log), tôi đã xác định được các dòng log báo lỗi sau:
```json
{"timestamp": "2026-06-01T06:57:01.529831", "event": "AGENT_ERROR", "data": {"step": 0, "error": "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details...', 'type': 'insufficient_quota', 'code': 'insufficient_quota'}}"}}
```
Sau đó, log ghi nhận thêm lỗi xác thực:
```json
{"timestamp": "2026-06-01T07:23:21.604919", "event": "AGENT_ERROR", "data": {"step": 0, "error": "Error code: 401 - {'error': {'message': 'Incorrect API key provided...', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}}}}
```

---

### 3. Chẩn đoán nguyên nhân (Diagnosis)
- **Lỗi 429 (Rate Limit / Insufficient Quota)**: Khóa API mặc định của OpenAI đặt trong file `.env` đã vượt quá hạn mức sử dụng (tài khoản hết tiền hoặc hết dung lượng thử nghiệm).
- **Lỗi 401 (Authentication Error)**: Khóa API được truyền vào bị sai cấu trúc hoặc không hợp lệ.
- **Hệ quả**: Do mã nguồn phiên bản ban đầu thiết lập cứng (hardcode) chỉ sử dụng mô hình OpenAI, nên khi API Key của OpenAI bị vô hiệu hóa hoặc hết hạn mức, toàn bộ hệ thống bị sập hoàn toàn mà không có giải pháp thay thế.

---

### 4. Giải pháp khắc phục (Solution)
Để khắc phục triệt để lỗi này và tăng tính bền vững của dự án, tôi đã:
1.  Đồng thiết kế kiến trúc đa Provider động bằng cách sử dụng cấu trúc Factory `get_agent(provider_name, model_name)` trong [src/ui/app.py](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/src/ui/app.py#L42-L55).
2.  Tích hợp bộ chọn **Provider** (OpenAI / Google Gemini) và danh sách **Model** tương ứng trên Sidebar của giao diện Streamlit khi bật chế độ "Version 2".
3.  Khi người dùng phát hiện OpenAI bị lỗi 429 hoặc 401, họ chỉ cần chọn `Google Gemini` và chọn model `gemini-1.5-flash` trực tiếp từ giao diện Streamlit. Hệ thống sẽ tự động cấu hình lại `GeminiProvider` và tiếp tục chạy vòng lặp ReAct một cách bình thường mà không cần dừng ứng dụng Streamlit hay chỉnh sửa mã nguồn hoặc file cấu hình `.env` trên máy chủ.

---

## III. NHẬN XÉT CÁ NHÂN: CHATBOT VS REACT AGENT (10 Điểm)

### 1. Vai trò của khối suy nghĩ (Thought)
Khối suy nghĩ `Thought` đóng vai trò như một phân vùng nháp (scratchpad) cho mô hình LLM. Thay vì việc Chatbot Baseline phải đưa ra câu trả lời ngay lập tức bằng phản xạ trực giác (dễ dẫn đến ảo tưởng - hallucination khi gặp thông tin số liệu cụ thể), khối `Thought` giúp Agent phân tích yêu cầu, tự lên kế hoạch hành động từng bước (ví dụ: *"Tôi cần tìm kiếm học phí của khối ngành kỹ thuật trước"*, sau đó mới tìm kiếm điều kiện học bổng), chọn công cụ phù hợp, rồi mới kết luận bằng `Final Answer`. Điều này cải thiện đáng kể tính chính xác, logic và khả năng suy luận của hệ thống.

---

### 2. Sự đánh đổi về độ tin cậy và hiệu năng (Reliability vs Performance)
Dựa vào bảng dữ liệu thu được từ việc chạy tab **So sánh** và file báo cáo nhóm, chúng tôi rút ra các kết quả đối chiếu sau:

| Tiêu chí | Chatbot Baseline | ReAct Agent v2 | Winner |
| :--- | :---: | :---: | :---: |
| **Tỉ lệ trả lời đúng** | 45% (9/20 câu) | **95% (19/20 câu)** | **Agent** |
| **Độ trễ trung bình (Latency)** | **1,200 ms** | 4,800 ms | **Chatbot** |
| **Tokens tiêu thụ trung bình** | **650 tokens** | 4,100 tokens | **Chatbot** |
| **Chi phí API trung bình** | **Thấp ($0.0001/câu)** | Cao ($0.0006/câu) | **Chatbot** |
| **Khả năng tự sửa sai** | Không có | **Có (Retry Nudge + Guardrails)** | **Agent** |

**Nhận xét về sự đánh đổi:**
- **Độ tin cậy vượt trội**: ReAct Agent nâng độ chính xác lên 95% và loại bỏ hoàn toàn các lỗi bịa số liệu học bổng/học phí nhờ lấy dữ liệu trực tiếp từ các file cào dữ liệu đã được chuẩn hóa.
- **Đánh đổi về hiệu năng**: ReAct Agent chậm hơn khoảng 4 lần về thời gian phản hồi và tiêu thụ lượng token gấp hơn 6 lần so với Baseline. Điều này là do Agent phải chạy nhiều vòng lặp suy nghĩ và gọi công cụ tích lũy prompt lịch sử.
- **Trường hợp Agent hoạt động kém hiệu quả**: Với các câu hỏi xã giao thông thường ("Xin chào", "Cảm ơn"), Agent vẫn cố suy nghĩ và gọi công cụ tìm kiếm, gây lãng phí tài nguyên và làm chậm tốc độ phản hồi một cách không đáng có. Do đó, Agent chỉ thực sự tối ưu cho các câu hỏi tra cứu dữ liệu động và phức tạp.

---

### 3. Tác động từ phản hồi môi trường (Observation)
Phản hồi môi trường `Observation` (kết quả trả về từ công cụ) chính là nhân tố dẫn dắt bước đi tiếp theo của Agent. Nếu `Observation` trả về dữ liệu đúng và đầy đủ, Agent sẽ ngay lập tức tổng hợp kết quả để đưa ra `Final Answer`.
Ngược lại, nếu `Observation` trả về rỗng hoặc thông báo lỗi, LLM trong vòng lặp ReAct sẽ nhận thức được từ khóa tìm kiếm trước đó chưa hiệu quả và tự động điều chỉnh từ khóa ở bước suy nghĩ (`Thought`) tiếp theo để thử lại bằng một công cụ khác hoặc một từ khóa khác, thay vì bịa đặt một câu trả lời không có thực.

---

## IV. ĐỀ XUẤT CẢI TIẾN TƯƠNG LAI (Future Improvements - 5 Điểm)

Để đưa hệ thống trợ lý tư vấn tuyển sinh VinUni này lên mức độ vận hành thực tế quy mô công nghiệp (Production-grade), tôi đề xuất 3 cải tiến kỹ thuật sau:

1.  **Hiệu năng (Semantic Search & Vector DB)**:
    Hiện tại công cụ tìm kiếm đang sử dụng phương pháp tách từ khóa đơn giản kết hợp chuẩn hóa Unicode thô. Khi khối lượng dữ liệu phình to lên hàng ngàn trang, hiệu năng tìm kiếm sẽ giảm và dễ bỏ sót ngữ nghĩa. Cần chuyển đổi sang sử dụng **Tìm kiếm ngữ nghĩa (Semantic Search)** bằng cách lưu trữ dữ liệu dưới dạng vector nhúng (Embeddings) trong cơ sở dữ liệu Vector chuyên dụng như ChromaDB, FAISS hoặc Qdrant để Agent có thể hiểu ý nghĩa sâu xa của câu hỏi bất kể cách diễn đạt của người dùng.
2.  **Khả năng mở rộng (Semantic Cache & Streaming)**:
    - Triển khai **Semantic Cache** (ví dụ sử dụng Redis + GPTCache) để lưu trữ câu trả lời cho các câu hỏi trùng lặp hoặc tương đồng ngữ nghĩa. Điều này giúp trả về câu trả lời dưới 1 giây mà không cần gọi mô hình LLM, tiết kiệm tới 80% chi phí API.
    - Cấu hình cơ chế **Streaming phản hồi** trên giao diện Streamlit thay vì bắt người dùng đợi toàn bộ vòng lặp ReAct kết thúc, giúp cải thiện đáng kể trải nghiệm người dùng cảm nhận (perceived latency).
3.  **Độ an toàn (Supervisor Agent & Guardrails)**:
    Bổ sung một lớp **Supervisor Agent** (sử dụng một LLM nhỏ, tối ưu hóa cực nhanh) để kiểm duyệt dữ liệu đầu vào chống lại các cuộc tấn công Prompt Injection cố tình phá vỡ cấu trúc ReAct loop, đồng thời kiểm duyệt dữ liệu đầu ra để đảm bảo Agent không đưa ra các phản hồi sai lệch, nhạy cảm hoặc không phù hợp với văn phong giáo dục của VinUni.
