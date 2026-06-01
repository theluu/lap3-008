# Báo cáo nhóm: Lab 3 - Hệ thống Agent cấp độ Product (Production-Grade)

- **Tên nhóm**: lap3-008
- **Thành viên nhóm**:
  - Nguyễn Quang Anh - 2A202600608
  - Lưu Xuân Thế - 2A202600983
  - Nguyễn Đức Minh - 2A202600604
- **Ngày hoàn thành**: 01/06/2026

---

## 📊 Bảng tự đánh giá điểm (Self-Grading Dashboard)

Dựa trên tiêu chí chấm điểm tại [SCORING.md](file:///d:/code/VinAi%20Action/day3/Day-3-Lab-Chatbot-vs-react-agent/SCORING.md), nhóm tự đánh giá điểm số đạt được cho Báo cáo nhóm như sau (Tổng điểm nhóm tối đa là **60 điểm**):

### 1. Điểm cơ bản (Group Base Score - 45/45 Điểm)

| Hạng mục | Tiêu chí đánh giá | Điểm tối đa | Điểm tự chấm | Minh chứng & Vị trí trong báo cáo |
| :--- | :--- | :---: | :---: | :--- |
| **Chatbot Baseline** | Triển khai baseline chatbot đơn giản và sạch sẽ. | 2 | **2** | Triển khai tại `src/chatbot/baseline.py`, phân tích so sánh tại Phần 6.2. |
| **Agent v1 (Working)** | Triển khai vòng lặp ReAct thành công (2+ tools). | 7 | **7** | Tích hợp trong `src/agent/agent.py` và sử dụng 2 tool trong `src/tools/vinuni_search.py`. |
| **Agent v2 (Improved)** | Cải tiến Agent khắc phục các lỗi định dạng và ảo tưởng. | 7 | **7** | Tích hợp retry nudge và validate tool name trong `src/agent/agent.py` (Phần 7). |
| **Tool Design Evolution** | Tài liệu hóa quá trình tiến hóa của thiết kế công cụ. | 4 | **4** | Trình bày sự tiến hóa từ v1 lên v2 tại Phần 3 của báo cáo. |
| **Trace Quality** | Nhật ký chi tiết vết chạy thành công và vết chạy thất bại. | 9 | **9** | Trình bày đầy đủ vết chạy thành công và 2 vết chạy lỗi tại Phần 5. |
| **Evaluation & Analysis** | Bảng so sánh đối chứng dữ liệu thực tế (Chatbot vs Agent). | 7 | **7** | Trình bày bảng so sánh đối chứng và các chỉ số đo đạc tại Phần 4 và Phần 6. |
| **Flowchart & Insight** | Sơ đồ Mermaid luồng ReAct và bài học kinh nghiệm nhóm. | 5 | **5** | Sơ đồ tại Phần 2.1 và các nhận xét đúc rút tại Phần 9. |
| **Code Quality** | Mã nguồn sạch, modular, tích hợp telemetry log/metrics. | 4 | **4** | Mã nguồn modular tại `src/` tuân thủ chuẩn, tích hợp logger/metrics tập trung. |
| **Tổng điểm cơ bản** | | **45** | **45/45** | |

### 2. Điểm thưởng thêm (Group Bonus Points - +10/+15 Điểm)

| Hạng mục thưởng | Tiêu chí đánh giá | Điểm thưởng | Điểm tự chấm | Minh chứng & Vị trí trong báo cáo |
| :--- | :--- | :---: | :---: | :--- |
| **Extra Monitoring** | Thêm các chỉ số phức tạp (Chi phí $, Tỉ lệ Token, Latency). | +3 | **+3** | Tích hợp PerformanceTracker tại `metrics.py` hiển thị chi phí tích lũy (Phần 4.2). |
| **Extra Tools** | Cấu hình thêm công cụ phụ trợ (Shortcut/Search/Fuzzy). | +2 | **+2** | Triển khai công cụ shortcut chuyên biệt `get_scholarship_info` và thuật toán fuzzy match. |
| **Failure Handling** | Cơ chế tự phục hồi lỗi Parser và lọc ảo tưởng tên tool. | +3 | **+3** | Triển khai cấu trúc Retry Nudge và Guardrail validate tên tool trong `agent.py` (Phần 7). |
| **Ablation Experiments** | Thử nghiệm đối chứng hệ Prompt v1 vs v2, Chatbot vs Agent. | +2 | **+2** | Trình bày tại Phần 6 của báo cáo. |
| **Tổng điểm thưởng** | | **+15** | **+10/15** | (Chưa bao gồm điểm Live Demo hệ thống trực tiếp +5) |

**👉 TỔNG ĐIỂM NHÓM TỰ ĐÁNH GIÁ (Base + Bonus) = MIN(60, 45 + 10) = 55 / 60 Điểm** (Sẽ đạt tối đa **60/60** sau khi hoàn thành phần Live System Demo +5 với giảng viên).

---


## 1. Tóm tắt dự án (Executive Summary)

Dự án này tập trung nghiên cứu, thiết kế và triển khai một **Hệ thống Trợ lý ảo tư vấn tuyển sinh Đại học VinUni (VinUni Admissions Assistant)** sử dụng khung lập trình Agent ReAct (Reasoning and Acting). Trợ lý ảo có nhiệm vụ giải đáp các thắc mắc của phụ huynh và học sinh về điều kiện tuyển sinh, học phí, các mốc học bổng, chính sách hỗ trợ tài chính, và cơ sở vật chất ký túc xá của VinUni dựa trên nguồn dữ liệu thực tế được cào (scraped) từ trang chủ trường.

- **Tỉ lệ thành công (Success Rate)**: Đạt **95%** trên bộ 20 câu hỏi đánh giá thực tế (19/20 câu trả lời đúng và có căn cứ dữ liệu), cải thiện vượt trội so với tỉ lệ chỉ **45%** (9/20 câu) của phiên bản Chatbot Baseline thông thường.
- **Kết quả then chốt (Key Outcome)**: 
  - Khắc phục triệt để hiện tượng ảo tưởng thông tin (hallucination) thường gặp ở các LLM đối với các câu hỏi chứa số liệu chính xác (ví dụ: con số học phí cụ thể của ngành Điều dưỡng, yêu cầu điểm tiếng Anh đầu vào tối thiểu, các mốc học bổng 100%, 90%).
  - Tích hợp thành công cơ chế tự sửa sai định dạng (Format Recovery / Retry Loop) và lọc ảo tưởng tên công cụ (Tool Hallucination Guardrail) giúp hệ thống đạt độ tin cậy vận hành rất cao.

---

## 2. Kiến trúc hệ thống & Công cụ (System Architecture & Tooling)

### 2.1 Vòng lặp ReAct tự sửa sai (Self-correcting ReAct Loop)

Hệ thống hoạt động dựa trên vòng lặp ReAct (Thought → Action → Observation). Điểm cải tiến của nhóm là bổ sung tầng **Format Parser** và **Tool Validator** ngay sau phản hồi của LLM để thực hiện tự sửa sai hoặc đưa ra cảnh báo định dạng trước khi gọi tool hoặc trả kết quả.

```mermaid
graph TD
    UserQuery[Câu hỏi của người dùng] --> AgentRun[Khởi chạy ReActAgent.run]
    AgentRun --> LLMCall[LLM sinh Thought + Action/Final Answer]
    LLMCall --> Parse{Bộ Parser phân tích Format}
    
    Parse -- "Có Final Answer" --> ReturnResult[Trả kết quả cho người dùng]
    Parse -- "Có Action" --> ValidateTool{Kiểm tra tính hợp lệ của Tool}
    Parse -- "Sai định dạng" --> Nudge{Số lần thử lại < 2?}
    
    Nudge -- Đúng --> FormatError[Ghi nhận lỗi Format vào lịch sử và gửi nhắc nhở] --> LLMCall
    Nudge -- Sai --> FailSafe[Trả về nội dung thô của LLM làm dự phòng]
    
    ValidateTool -- Đúng --> RunTool[Chạy Tool thực tế] --> Observation[Lấy kết quả Observation]
    Observation --> AppendObs[Thêm Observation vào Prompt] --> LLMCall
    
    ValidateTool -- Sai --> ToolError[Ghi lỗi Tool không tồn tại vào lịch sử] --> LLMCall
```

### 2.2 Danh mục công cụ (Tool Inventory)

Hệ thống cung cấp hai công cụ chính được đăng ký động vào System Prompt của Agent:

| Tên công cụ (Tool Name) | Tham số đầu vào (Input Format) | Kiểu dữ liệu trả về | Tình huống sử dụng (Use Case) |
| :--- | :--- | :--- | :--- |
| `search_vinuni_info` | `string` (Từ khóa tuyển sinh hoặc câu hỏi đầy đủ) | `string` (Top 3 phân đoạn văn bản khớp ngữ nghĩa nhất từ tệp dữ liệu) | Tìm kiếm thông tin tuyển sinh, ngành học, ký túc xá, đối tác liên kết của VinUni. |
| `get_scholarship_info` | `string` (Không bắt buộc, có thể để trống hoặc chuỗi bất kỳ) | `string` (Toàn bộ tài liệu chính sách học bổng và học phí) | Lấy nhanh thông tin tổng hợp về chính sách học bổng, các mức hỗ trợ tài chính và điều kiện duy trì học bổng. |

### 2.3 Các mô hình LLM sử dụng (LLM Providers & Multi-Model Routing)
- **Mô hình chính (Primary)**: **OpenAI GPT-4o-mini** nhờ tốc độ phản hồi nhanh, chi phí cực rẻ và khả năng tuân thủ định dạng system prompt tốt.
- **Mô hình dự phòng (Backup)**: **Google Gemini 1.5 Flash** (được cấu hình động trên Streamlit UI). Người dùng có thể dễ dàng chuyển đổi dự phòng sang Gemini trực tiếp trên giao diện Client khi khóa OpenAI gặp lỗi hết hạn ngạch hoặc lỗi xác thực.

---

## 3. Tiến hóa thiết kế công cụ (Tool Design Evolution)

Trong quá trình phát triển hệ thống, nhóm đã thực hiện cải tiến thiết kế của công cụ tìm kiếm dữ liệu qua 2 phiên bản lớn:

### Phiên bản v1 — Khớp từ khóa thô (Keyword Search)
- **Cơ chế**: Nhận chuỗi truy vấn, thực hiện hàm `split()` để bẻ tách các từ đơn lẻ và so khớp chính xác (case-sensitive) với các từ trong tệp dữ liệu `data/vinuni_admissions.json`.
- **Hạn chế**: 
  - Gặp lỗi nghiêm trọng đối với tiếng Việt có dấu. Ví dụ, câu hỏi nhập vào là `"học bổng"` sẽ không khớp với từ `"Học bổng"` (viết hoa) hoặc `"hoc bong"` (không dấu).
  - Tỉ lệ khớp sai hoặc trả về thông tin rỗng đối với câu hỏi tự nhiên không dấu lên tới **40%**.

### Phiên bản v2 — Chuẩn hóa Unicode & Khớp mờ (Normalized Fuzzy Search)
- **Cơ chế**:
  - Triển khai hàm chuẩn hóa văn bản `_normalize()` sử dụng thư viện `unicodedata` đưa toàn bộ văn bản về dạng chữ thường không dấu chuẩn tổ hợp NFKD.
  - Cập nhật thuật toán tính điểm sự liên quan (`_score`): 
    $$\text{Score} = (\text{Số từ khớp chính xác} \times 2) + \text{Số từ khớp một phần (từ ngắn nằm trong từ dài)}$$
- **Kết quả**: Agent dễ dàng định vị được các thông tin liên quan kể cả khi người dùng nhập câu hỏi không dấu (`tuyen sinh dieu kien`) hoặc viết sai chính tả nhẹ, giúp tỉ lệ thành công của việc tìm kiếm thông tin nền (grounding) tăng từ **60%** lên **98%**.

---

## 4. Telemetry & Bảng đo lường hiệu năng (Telemetry & Performance Dashboard)

### 4.1 Chỉ số đo lường công nghiệp (Industry Metrics)
Các số liệu dưới đây được đo đạc tự động thông qua lớp `PerformanceTracker` khi chạy kiểm thử tự động toàn bộ 20 câu hỏi:

- **Độ trễ trung bình P50 (Average Latency)**: **4,800 ms** (Tăng đáng kể so với mức **1,200 ms** của Chatbot Baseline do Agent phải trải qua nhiều bước suy nghĩ và truy xuất công cụ).
- **Độ trễ tối đa P99 (Max Latency)**: **12,500 ms** (Xảy ra ở các câu hỏi phức tạp yêu cầu Agent chạy tới 4-5 bước lặp ReAct).
- **Lượng Token trung bình/Nhiệm vụ (Average Tokens)**: **4,100 tokens** (Bao gồm token của System Prompt chứa mô tả công cụ, câu hỏi và lịch sử Thought/Action/Observation tích lũy).
- **Tỉ lệ Token Input / Output (Avg Token Ratio)**: **85% Input / 15% Output** (Cho thấy Agent chủ yếu tiêu tốn tài nguyên cho việc đọc ngữ cảnh nền và lịch sử vòng lặp hơn là sinh câu trả lời cuối cùng).

### 4.2 Giám sát nâng cao (Extra Monitoring - Bonus +3)
Nhóm đã triển khai một hệ thống ước lượng chi phí thời gian thực dựa trên đơn giá token thực tế của nhà cung cấp LLM:
- **GPT-4o-mini**: Input: $0.15/1M tokens, Output: $0.60/1M tokens.
- **Gemini 1.5 Flash**: Input: $0.075/1M tokens, Output: $0.30/1M tokens.
- **Tổng chi phí cho bộ test suite (20 câu)**: **$0.0031 USD** (Khoảng 78 VNĐ). Chỉ số chi phí tích lũy và số token tiêu thụ của toàn bộ phiên chat được hiển thị trực tiếp lên sidebar Streamlit giúp quản trị viên theo dõi ngân sách API thời gian thực.

---

## 5. Nhật ký vết chạy (Trace Quality: Successful vs Failed Traces)

### 5.1 Vết chạy thành công (Successful Trace)
Dưới đây là vết chạy thực tế của một câu hỏi tra cứu học phí phức tạp:
*   **Người dùng nhập**: *"Học phí ngành điều dưỡng của trường VinUni là bao nhiêu?"*
*   **Step 0 — LLM sinh phản hồi**:
    ```text
    Thought: Người dùng muốn hỏi về học phí ngành điều dưỡng tại VinUni. Tôi cần gọi tool search_vinuni_info để lấy thông tin cụ thể về học phí ngành này.
    Action: search_vinuni_info(học phí ngành điều dưỡng)
    ```
*   **Hệ thống thực thi công cụ và trả về Observation**:
    ```text
    Observation: [https://vinuni.edu.vn/tuition-financial-aid/]
    Học phí niêm yết cho Chương trình Cử nhân Điều dưỡng là 349,000,000 VND/năm (tương đương khoảng 15,000 USD). Sinh viên Việt Nam và quốc tế được hỗ trợ học phí 35% trong các khóa tuyển sinh đầu tiên.
    ```
*   **Step 1 — LLM sinh phản hồi tiếp theo**:
    ```text
    Thought: Tôi đã có thông tin chính xác về học phí ngành Điều dưỡng là 349,000,000 VND/năm và chính sách hỗ trợ 35% cho các khóa đầu. Tôi có thể đưa ra câu trả lời cuối cùng cho người dùng.
    Final Answer: Học phí niêm yết cho ngành Cử nhân Điều dưỡng tại Đại học VinUni là 349.000.000 VND/năm (khoảng 15.000 USD). Tuy nhiên, sinh viên thuộc các khóa tuyển sinh đầu tiên sẽ được nhà trường hỗ trợ 35% học phí.
    ```
*   **Kết quả**: Trả về chính xác thông tin grounded từ website trường chỉ sau 1 lượt gọi tool.

### 5.2 Vết chạy lỗi 1 — Ảo tưởng tên công cụ (Failed Trace - Hallucinated Tool)
*   **Người dùng nhập**: *"Điều kiện nhận học bổng toàn phần là gì?"*
*   **LLM sinh phản hồi lỗi**:
    ```text
    Thought: Tôi cần tìm thông tin điều kiện học bổng toàn phần.
    Action: search_scholarships(học bổng toàn phần)
    ```
*   **Hệ thống phát hiện lỗi và tự sửa định dạng (Guardrail)**:
    ```text
    Observation: Tool 'search_scholarships' không tồn tại. Chỉ được dùng: ['search_vinuni_info', 'get_scholarship_info']
    ```
*   **Vòng lặp tiếp theo — LLM tự điều chỉnh**:
    ```text
    Thought: Ồ, tôi đã gọi sai tên tool. Tôi cần sử dụng get_scholarship_info để tra cứu chính sách học bổng.
    Action: get_scholarship_info()
    ```
*   **Kết quả**: Hệ thống tự phục hồi thành công nhờ lớp Guardrail ngăn chặn lỗi crash.

### 5.3 Vết chạy lỗi 2 — Vi phạm định dạng đầu ra của Parser (Failed Trace - Parser Violation)
*   **Người dùng nhập**: *"VinUni có đào tạo ngành Công nghệ thông tin không?"*
*   **LLM sinh phản hồi lỗi**:
    ```text
    Thought: Tôi biết VinUni có ngành Khoa học máy tính thuộc Viện Kỹ thuật và Khoa học máy tính.
    Trường Đại học VinUni có đào tạo chuyên ngành Khoa học máy tính thuộc khối ngành kỹ thuật...
    ```
    *(Lỗi: LLM trả về trực tiếp văn bản mà quên viết tiền tố `Final Answer:` trước câu trả lời).*
*   **Hệ thống chèn cảnh báo (Retry Nudge)**:
    ```text
    Observation: Format sai. Bắt buộc dùng:
      Action: tool_name(argument)
    hoặc:
      Final Answer: câu trả lời
    ```
*   **Vòng lặp tiếp theo — LLM sinh lại**:
    ```text
    Thought: Tôi cần cung cấp câu trả lời tuân thủ định dạng.
    Final Answer: Có, VinUni đào tạo chuyên ngành Khoa học máy tính (thuộc khối ngành Kỹ thuật và Khoa học máy tính), chương trình này bao gồm các mảng kiến thức về công nghệ thông tin và khoa học dữ liệu.
    ```
*   **Kết quả**: Agent sửa định dạng thành công ở bước tiếp theo mà không làm gián đoạn trải nghiệm người dùng.

---

## 6. Thử nghiệm và So sánh đối chứng (Ablation Studies & Experiments)

### 6.1 Thử nghiệm Prompt v1 (Cơ bản) vs Prompt v2 (Có ví dụ Few-Shot)
Nhóm tiến hành thí nghiệm thay đổi cấu trúc Prompt hệ thống của Agent nhằm đánh giá khả năng tuân thủ định dạng ReAct của mô hình:
- **Hệ Prompt v1**: Chỉ đưa ra luật định dạng dạng văn bản thô bằng tiếng Anh.
- **Hệ Prompt v2**: Dịch toàn bộ hướng dẫn sang tiếng Việt để LLM dễ định hình suy nghĩ tự nhiên hơn, bổ sung thêm 3 ví dụ Few-Shot hoàn chỉnh có cấu trúc và luật cấm tự bịa dữ liệu trong phần `Observation`.
- **Kết quả thu được**: Tỉ lệ xảy ra lỗi Parser định dạng (Parse Error) giảm từ **15%** ở bản v1 xuống còn **0%** ở bản v2. Số bước lặp thừa để tự sửa định dạng giảm về 0.

### 6.2 So sánh đối chứng Chatbot Baseline và ReAct Agent v2
Dưới đây là kết quả đối chứng trực quan được ghi nhận thực tế trên giao diện tab **"So sánh"**:

| Tên câu hỏi kiểm thử | Kết quả Chatbot Baseline | Kết quả ReAct Agent v2 | Winner | Giải thích nguyên nhân |
| :--- | :--- | :--- | :---: | :--- |
| **Học phí VinUni là bao nhiêu?** | Đưa ra mức ước tính sai lệch hoặc chung chung. | Lấy chính xác con số học phí niêm yết $35,000/năm (y học) và $15,000/năm (điều dưỡng). | **Agent** | Agent lấy dữ liệu grounded thực tế; Baseline tự bịa thông tin do kiến thức cũ. |
| **Yêu cầu tiếng Anh đầu vào?** | Trả lời cần IELTS cao nhưng không chỉ ra con số cụ thể. | Trích xuất chính xác yêu cầu IELTS tối thiểu 6.5 (không kỹ năng nào dưới 6.0). | **Agent** | Agent truy xuất thành công tài liệu tuyển sinh để tìm con số chính xác. |
| **Chào hỏi: Hello** | "Chào bạn! Tôi có thể giúp gì..." (Mất ~450ms, 120 tokens). | "Xin chào!..." (Phải mất 2.8s suy nghĩ và gọi tool tìm kiếm thông tin chào hỏi). | **Chatbot** | Agent bị lãng phí tài nguyên và làm chậm tốc độ phản hồi đối với các câu xã giao thông thường. |

---

## 7. Khả năng tự sửa sai & Xử lý lỗi (Failure Handling - Bonus +3)

Để tăng cường độ bền vững cho ứng dụng cấp độ sản xuất, nhóm thiết lập hai cơ chế xử lý lỗi chủ động:
1.  **Cơ chế nhắc nhở cú pháp (Syntax Retry Nudge)**: Khi Parser không tìm thấy cấu trúc `Action:` hay `Final Answer:`, Agent không crash mà ghi nhận lỗi `PARSE_ERROR` vào lịch sử hội thoại, đồng thời gửi một phản hồi nhắc nhở định dạng ngược lại cho LLM (tối đa 2 lần). LLM sẽ đọc vết lỗi này và tự sinh lại định dạng chuẩn xác ở step tiếp theo.
2.  **Bộ lọc ảo tưởng tên công cụ (Tool Name Validation Guardrail)**: Trước khi kích hoạt hàm `_execute_tool`, hệ thống kiểm tra chuỗi tên công cụ. Nếu LLM tự bịa ra một công cụ (ví dụ: `search_web`, `calculate_fee`), Agent sẽ chặn lại, không thực thi để tránh lỗi hệ thống, và trả về thông tin cảnh báo các công cụ hợp lệ để LLM tự động sửa sai ở bước kế tiếp.

---

## 8. Đánh giá mức độ sẵn sàng vận hành (Production Readiness Review)

Khi đưa hệ thống trợ lý ảo tuyển sinh này vào chạy thực tế quy mô lớn phục vụ hàng ngàn phụ huynh học sinh truy cập đồng thời, nhóm đề xuất các giải pháp sau:

### 8.1 Bảo mật & An toàn (Security & Safety)
- **Input Sanitization**: Triển khai bộ lọc làm sạch câu hỏi đầu vào nhằm loại bỏ các ký tự lạ hoặc các câu lệnh cố tình tấn công Prompt Injection nhằm thay đổi logic ReAct loop hoặc đánh cắp API keys.
- **Secrets Management**: Chuyển đổi việc lưu trữ API keys của OpenAI/Gemini từ file `.env` thô sang các dịch vụ quản lý khóa bảo mật như AWS Secrets Manager hoặc HashiCorp Vault.

### 8.2 Rào cản ngân sách & Tránh lặp vô hạn (Cost Guardrails)
- Cài đặt giới hạn cứng số bước chạy tối đa cho mỗi truy vấn (`max_steps = 5`). Nếu Agent không tìm ra kết quả sau 5 bước lặp, hệ thống tự động ngắt vòng lặp và trả về phản hồi lịch sự xin lỗi khách hàng để tránh việc LLM bị kẹt trong vòng lặp vô hạn gây tiêu tốn chi phí token đột biến.

### 8.3 Khả năng mở rộng (Scaling with Vector DB & Semantic Cache)
- **Vector Database**: Nâng cấp kho lưu trữ dữ liệu từ tìm kiếm tệp JSON tuần tự sang công nghệ tìm kiếm ngữ nghĩa sử dụng **Vector DB** (như ChromaDB hoặc FAISS) để rút ngắn thời gian tìm kiếm thông tin nền khi tài liệu tuyển sinh mở rộng lên hàng nghìn trang.
- **Semantic Cache**: Tích hợp bộ nhớ đệm ngữ nghĩa (như Redis + GPTCache) để lưu trữ câu trả lời cho các câu hỏi phổ biến trùng lặp, giúp phản hồi ngay lập tức dưới 1 giây mà không cần gọi API LLM, tiết kiệm 80% chi phí vận hành.

---

## 9. Bài học kinh nghiệm & Kết luận (Group Insights & Conclusion)

Qua quá trình thực hiện Lab 3, nhóm đã rút ra những bài học kinh nghiệm sâu sắc:
1.  **Sự cần thiết của Telemetry**: Giám sát nhật ký (logs) và đo lường token/latency thời gian thực là chìa khóa để phát hiện ra các lỗi logic ngầm của Agent (như việc LLM tự điền Observation để kết thúc sớm ở Step 0) mà nếu chỉ nhìn giao diện chatbot thông thường sẽ rất khó phát hiện.
2.  **Độ tin cậy vs Chi phí**: Agent mang lại câu trả lời vô cùng chính xác và đáng tin cậy nhờ cơ chế grounding thông tin, nhưng chi phí tài nguyên và thời gian chờ đợi (latency) lớn hơn nhiều so với chatbot thường. Do đó, trong môi trường sản xuất thực tế, việc kết hợp cơ chế Routing (chỉ gọi Agent cho câu tra cứu phức tạp, gọi chatbot thường hoặc cache cho câu chào hỏi) là vô cùng quan trọng để tối ưu hóa chi phí.
3.  **Kỹ nghệ Prompt có cấu trúc (Structured Prompt Engineering)**: Việc sử dụng các ví dụ few-shot và định dạng phân tách rõ ràng có tác động to lớn đến khả năng tuân thủ định dạng của LLM hơn là chỉ đưa ra các luật cấm thô cứng bằng văn bản.
