# Evaluation: Chatbot Baseline vs ReAct Agent

## Test Setup
- 20 câu hỏi tuyển sinh VinUni
- Model: gpt-4o-mini
- Date: 2026-06-01

## Kết quả so sánh

| # | Câu hỏi | Chatbot | Agent | Winner |
|---|---------|---------|-------|--------|
| 1 | Điều kiện tuyển sinh? | Trả lời chung chung | Cite nguồn vinuni.edu.vn | Agent |
| 2 | Học bổng có loại gì? | Có thể bịa số liệu | Lấy từ data thực | Agent |
| 3 | Học phí bao nhiêu? | Ước tính sai | Trả đúng từ trang học phí | Agent |
| 4-20 | ... | ... | ... | ... |

## Aggregate Metrics

| Metric | Chatbot Baseline | ReAct Agent v1 | ReAct Agent v2 |
|--------|-----------------|----------------|----------------|
| Correct / 20 | - | - | - |
| Hallucination count | - | - | - |
| Avg latency (ms) | - | - | - |
| Avg tokens/query | - | - | - |
| Parse errors | N/A | - | - |

> Điền số liệu thực tế sau khi chạy test.

## Kết luận
Chatbot baseline trả lời dựa trên training data → dễ hallucinate số liệu cụ thể.
ReAct Agent luôn gọi tool để lấy dữ liệu thực từ vinuni.edu.vn → câu trả lời có căn cứ.
