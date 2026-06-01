import os
import json
import requests
from bs4 import BeautifulSoup

DATA_PATH = "data/vinuni_admissions.json"

VINUNI_PAGES = [
    "https://vinuni.edu.vn/admissions/",
    "https://vinuni.edu.vn/tuition-financial-aid/",
    "https://vinuni.edu.vn/programs/",
    "https://vinuni.edu.vn/about/",
    "https://vinuni.edu.vn/undergraduate/",
    "https://vinuni.edu.vn/scholarship/",
    "https://vinuni.edu.vn/student-life/",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _extract_chunks(url: str) -> list:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    # Force UTF-8 để tránh lỗi encoding tiếng Việt
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in raw_text.split("\n") if len(l.strip()) > 30]

    chunks = []
    window = 4
    for i in range(0, len(lines), window):
        content = " ".join(lines[i: i + window])
        chunks.append({"source": url, "content": content})
    return chunks


def scrape_vinuni_admissions(args: str = "") -> str:
    """Scrape trang tuyển sinh VinUni và cache dữ liệu vào JSON. Dùng 'refresh' để scrape lại."""
    force = "refresh" in str(args).lower()

    if not force and os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return f"Cache đã có {len(data)} chunks tại {DATA_PATH}. Dùng 'refresh' để scrape lại."

    os.makedirs("data", exist_ok=True)
    all_chunks = []

    for url in VINUNI_PAGES:
        try:
            chunks = _extract_chunks(url)
            all_chunks.extend(chunks)
            print(f"  Scraped {len(chunks)} chunks from {url}")
        except Exception as e:
            all_chunks.append(
                {"source": url, "content": f"Lỗi scrape {url}: {str(e)}"})

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    return f"Đã scrape {len(all_chunks)} chunks từ {len(VINUNI_PAGES)} trang VinUni. Lưu tại {DATA_PATH}."
