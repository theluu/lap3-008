# Báo Cáo Cá Nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Nguyễn Đức Minh
- **MSSV**: 2A202600604
- **Lớp**: C401
- **Ngày**: 01/06/2026
- **Nhánh thực hiện**: minhnd-2A202600604

---

# I. Đóng Góp Kỹ Thuật (15 Điểm)

## Các Module Đã Triển Khai

### 1. Module Thu Thập Dữ Liệu (Scraper)

**File thực hiện:**

* `src/tools/vinuni_scraper.py`

Tôi đã xây dựng module scraper để thu thập thông tin tuyển sinh từ website VinUni. Module này có nhiệm vụ:

* Truy cập các trang tuyển sinh của VinUni.
* Trích xuất nội dung văn bản từ HTML.
* Làm sạch dữ liệu.
* Lưu dữ liệu dưới dạng JSON để phục vụ cho quá trình tìm kiếm và truy xuất thông tin.

Kết quả đầu ra là bộ dữ liệu:

```text
data/vinuni_admissions.json
```

được sử dụng làm nguồn tri thức cho Agent.

---

### 2. Module Tìm Kiếm (Search Tool)

**File thực hiện:**

* `src/tools/vinuni_search.py`

Tôi đã xây dựng công cụ tìm kiếm dựa trên dữ liệu đã scrape.

Các chức năng chính:

* Đọc dữ liệu JSON.
* Chuẩn hóa truy vấn người dùng.
* So khớp từ khóa.
* Tính điểm liên quan giữa truy vấn và tài liệu.
* Trả về các kết quả phù hợp nhất.

Các tool được Agent sử dụng:

* `search_vinuni_info()`
* `get_scholarship_info()`

## Điểm Nổi Bật Trong Phần Cài Đặt

### Hệ Thống Search Dựa Trên Keyword Scoring

Tôi xây dựng cơ chế chấm điểm để xác định tài liệu liên quan nhất với truy vấn người dùng.

Ý tưởng:

* Tách từ khóa từ câu hỏi.
* So khớp với nội dung đã scrape.
* Tính điểm dựa trên số lượng từ khóa trùng khớp.
* Trả về các kết quả có điểm cao nhất.

---

### Cơ Chế Tool Calling

Agent có khả năng xác định tool cần sử dụng và thực thi động thông qua tên tool.

Ví dụ:

```text
Action: get_scholarship_info()
```

Agent sẽ tìm tool tương ứng và thực hiện truy vấn dữ liệu.

---

## Tài Liệu Hóa Luồng Hoạt Động

Kiến trúc tổng thể:

```text
VinUni Website
        ↓
     Scraper
        ↓
 vinuni_admissions.json
        ↓
   Search Tool
        ↓
    ReAct Agent
        ↓
  Final Answer
```

Trong hệ thống này:

* Scraper đóng vai trò thu thập tri thức.
* Search Tool đóng vai trò truy xuất tri thức.
* ReAct Agent đóng vai trò suy luận và điều phối công cụ.

---

# II. Phân Tích Một Trường Hợp Debugging (10 Điểm)

## Mô Tả Vấn Đề

Trong quá trình xây dựng hệ thống, tôi gặp lỗi dữ liệu tiếng Việt bị mã hóa sai sau khi scrape.

Ví dụ dữ liệu trả về:

```text
Há»™i tá»¥ nhá»¯ng sáº¯c mÃ u...
```

thay vì:

```text
Hội tụ những sắc màu...
```

Vấn đề này khiến cho Search Tool không thể hoạt động chính xác vì các từ khóa tiếng Việt bị biến dạng.

---

## Nguồn Phát Hiện

Lỗi được phát hiện khi kiểm tra dữ liệu đầu ra của scraper sau khi crawl dữ liệu từ website VinUni.

Khi kiểm tra file:

```text
data/vinuni_admissions.json
```

nội dung văn bản tiếng Việt xuất hiện dưới dạng ký tự lỗi encoding.

Đồng thời khi chạy thử Search Tool, các truy vấn như:

```text
học bổng
tuyển sinh
ngành học
```

không trả về kết quả phù hợp mặc dù dữ liệu thực tế có tồn tại trong dataset.

---

## Chẩn Đoán Nguyên Nhân

Sau khi kiểm tra pipeline scrape dữ liệu, tôi xác định nguyên nhân đến từ việc xử lý encoding chưa chính xác. Dữ liệu gốc từ website sử dụng UTF-8 nhưng trong quá trình đọc nội dung HTML đã xảy ra hiện tượng decode sai encoding, dẫn đến việc ký tự tiếng Việt bị lỗi. Do Search Tool hoạt động dựa trên so khớp từ khóa nên dữ liệu lỗi encoding làm giảm đáng kể độ chính xác của hệ thống truy xuất.

---

## Giải Pháp

Tôi đã cập nhật lại scraper bằng cách:

1. Ép kiểu encoding UTF-8 trước khi xử lý dữ liệu.
2. Kiểm tra encoding của response trước khi parse HTML.
3. Lưu file JSON bằng chuẩn UTF-8.
4. Kiểm tra lại dữ liệu sau khi scrape.

Sau khi sửa lỗi:

```text
Hội tụ những sắc màu độc bản...
```

được lưu đúng định dạng.

Kết quả:

* Search Tool hoạt động ổn định hơn.
* Truy vấn tiếng Việt trả về kết quả chính xác.
* Chất lượng câu trả lời của Agent được cải thiện rõ rệt.

---

# III. Cảm Nhận Cá Nhân: Chatbot và ReAct Agent (10 Điểm)

## 1. Thought Giúp Agent Tốt Hơn Chatbot Như Thế Nào?

Chatbot truyền thống thường trả lời trực tiếp dựa trên kiến thức đã được huấn luyện trong mô hình.

Trong khi đó ReAct Agent có bước:

```text
Thought
```

giúp mô hình xác định:

* Có cần sử dụng công cụ hay không.
* Cần lấy thông tin từ đâu.
* Bước tiếp theo nên thực hiện là gì.

Nhờ đó Agent có khả năng đưa ra các quyết định hợp lý hơn trước khi trả lời.

---

## 2. Khi Nào Agent Hoạt Động Kém Hơn Chatbot?

Agent có thể hoạt động kém hơn trong các trường hợp:

* Search Tool trả về dữ liệu không liên quan.
* Action bị parse sai.
* Tool không tìm thấy dữ liệu phù hợp.
* Truy vấn quá ngắn hoặc mơ hồ.

Trong những trường hợp này Chatbot đôi khi vẫn tạo được câu trả lời trôi chảy hơn vì không phụ thuộc vào hệ thống công cụ.

---

## 3. Observation Ảnh Hưởng Thế Nào Đến Quá Trình Suy Luận?

Observation đóng vai trò là nguồn thông tin thực tế cho Agent.

Sau khi thực hiện Action, Agent nhận được Observation và sử dụng nó để:

* Kiểm chứng giả định ban đầu.
* Điều chỉnh hướng suy luận.
* Tạo câu trả lời dựa trên dữ liệu thực tế.

Điều này giúp giảm hiện tượng hallucination so với Chatbot thông thường.

---

# IV. Hướng Phát Triển Trong Tương Lai (5 Điểm)

## Khả Năng Mở Rộng

Để triển khai ở quy mô lớn hơn, tôi đề xuất:

* Chuyển sang kiến trúc bất đồng bộ (Async).
* Hỗ trợ nhiều công cụ hơn.
* Xây dựng hệ thống quản lý tool tập trung.

---

## An Toàn

Các cải tiến cần thiết:

* Kiểm tra đầu vào trước khi gọi tool.
* Giới hạn số vòng lặp Agent.
* Xây dựng cơ chế Supervisor Agent để giám sát hành vi của Agent.

---

## Hiệu Năng

Một số hướng cải tiến:

* Thay thế keyword search bằng semantic search.
* Sử dụng Embedding Models.
* Tích hợp Vector Database (FAISS hoặc ChromaDB).
* Áp dụng Reranking để tăng độ chính xác truy xuất.

---

# Kết Luận

Qua Lab 3, tôi đã cơ bản xây dựng được hệ thống ReAct Agent có khả năng sử dụng công cụ để truy xuất thông tin tuyển sinh từ dữ liệu web của VinUni. So với Chatbot truyền thống, ReAct Agent cho thấy khả năng suy luận có cấu trúc hơn, tận dụng được nguồn dữ liệu bên ngoài và giảm đáng kể hiện tượng trả lời dựa trên suy đoán. Đây là bước nền tảng quan trọng để phát triển các hệ thống AI Agent thực tế trong tương lai.
