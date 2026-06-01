import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.vinuni_search import search_vinuni_info, get_scholarship_info

# 20 test cases: (câu hỏi, từ khóa kỳ vọng ít nhất 1 từ xuất hiện trong kết quả)
TEST_CASES = [
    ("Điều kiện tuyển sinh VinUni là gì?",          ["tuyen sinh", "admission", "vinuni"]),
    ("VinUni có những ngành học nào?",               ["program", "nganh", "engineering", "business"]),
    ("Học bổng VinUni có những loại nào?",           ["hoc bong", "scholarship"]),
    ("Học phí VinUni là bao nhiêu?",                 ["phi", "hoc phi", "tuition", "fee", "chi phi", "le phi"]),
    ("Quy trình nộp hồ sơ tuyển sinh?",              ["ho so", "apply", "application", "nop"]),
    ("VinUni thành lập năm nào?",                    ["vinuni", "university", "founded"]),
    ("Trường VinUni ở đâu?",                         ["ha noi", "hanoi", "campus", "vinuni"]),
    ("Có hỗ trợ tài chính không?",                   ["tai chinh", "financial", "ho tro", "support", "hoc bong"]),
    ("Yêu cầu tiếng Anh như thế nào?",              ["english", "ielts", "tieng anh", "language", "ngoai ngu", "ngon ngu"]),
    ("VinUni có ký túc xá không?",                   ["dormitory", "ky tuc xa", "housing", "campus", "sinh vien", "co so"]),
    ("Đối tác quốc tế của VinUni là gì?",            ["quoc te", "international", "partner", "cornell"]),
    ("Chuyên ngành kỹ thuật có những gì?",           ["ky thuat", "engineering", "khoa hoc", "technology", "may tinh", "cong nghe"]),
    ("Xét học bổng dựa trên tiêu chí gì?",           ["hoc bong", "scholarship", "tieu chi", "criteria"]),
    ("Chương trình giảng dạy bằng ngôn ngữ gì?",    ["english", "tieng anh", "language", "instruction", "giang day", "chuong trinh"]),
    ("VinUni khác gì các trường đại học khác?",      ["vinuni", "university", "unique", "different"]),
    ("Cần bao nhiêu điểm để vào VinUni?",            ["diem", "score", "admission", "requirement"]),
    ("Có chương trình học bổng toàn phần không?",    ["hoc bong", "scholarship", "full", "toan phan"]),
    ("Liên hệ tư vấn tuyển sinh ở đâu?",            ["contact", "lien he", "email", "tuyen sinh"]),
    ("VinUni có chương trình thạc sĩ không?",        ["master", "thac si", "graduate", "postgraduate"]),
    ("Thời hạn nộp hồ sơ là khi nào?",              ["deadline", "thoi han", "nop", "application"]),
]


def _normalize_result(text: str) -> str:
    """Bỏ dấu để so sánh không phân biệt dấu."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def result_contains_any(result: str, keywords: list) -> bool:
    result_norm = _normalize_result(result)
    return any(kw.lower() in result_norm for kw in keywords)


@pytest.mark.parametrize("question,keywords", TEST_CASES)
def test_search_returns_relevant_result(question, keywords):
    result = search_vinuni_info(question)
    # Phải trả về gì đó (không rỗng, không phải thông báo lỗi)
    assert len(result) > 30, f"Result too short for: {question}"
    assert result_contains_any(result, keywords), (
        f"Result for '{question}' không chứa bất kỳ keyword nào trong {keywords}.\n"
        f"Got: {result[:300]}"
    )


def test_scholarship_info_not_empty():
    result = get_scholarship_info()
    assert len(result) > 50, "Scholarship info phải trả về nội dung có ý nghĩa"


def test_search_no_diacritic_query():
    """Tool v2: query không dấu vẫn phải tìm được."""
    result = search_vinuni_info("tuyen sinh dieu kien")
    assert len(result) > 30, "Fuzzy match phải hoạt động với query không dấu"


def test_search_unknown_topic_returns_gracefully():
    """Query hoàn toàn không liên quan không được raise exception."""
    result = search_vinuni_info("công thức nấu phở Hà Nội")
    assert isinstance(result, str), "Phải trả về string dù không tìm thấy"
