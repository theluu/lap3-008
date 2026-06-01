import json
import os
import unicodedata

DATA_PATH = "data/vinuni_admissions.json"


def _load_chunks() -> list:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    """Bỏ dấu tiếng Việt để tăng khả năng match không dấu."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _score(query: str, content: str) -> int:
    """v2: exact match (x2) + partial word match — hỗ trợ query không dấu."""
    q_norm = _normalize(query)
    c_norm = _normalize(content)
    query_words = set(q_norm.split())
    content_words = set(c_norm.split())
    exact = len(query_words & content_words)
    partial = sum(
        1 for qw in query_words for cw in content_words
        if len(qw) > 2 and (qw in cw or cw in qw)
    )
    return exact * 2 + partial


def search_vinuni_info(query: str) -> str:
    """Tìm kiếm thông tin tuyển sinh VinUni theo từ khóa. Input: câu hỏi hoặc từ khóa."""
    chunks = _load_chunks()
    if not chunks:
        return "Chưa có dữ liệu. Hãy chạy scrape_vinuni_admissions() trước."

    scored = sorted(chunks, key=lambda c: _score(query, c["content"]), reverse=True)
    top3 = scored[:3]

    if _score(query, top3[0]["content"]) == 0:
        return "Không tìm thấy thông tin liên quan đến câu hỏi này trong dữ liệu VinUni."

    results = [f"[{c['source']}]\n{c['content']}" for c in top3]
    return "\n\n---\n\n".join(results)


def get_scholarship_info(args: str = "") -> str:
    """Lấy thông tin học bổng và học phí VinUni. Không cần argument."""
    return search_vinuni_info("học bổng scholarship học phí tài chính hỗ trợ financial aid")
