"""
So sánh Chatbot Baseline vs ReAct Agent trên 20 câu hỏi tuyển sinh VinUni.
Chạy: python tests/compare_baseline_vs_agent.py
"""

import os
import sys
import time
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.chatbot.baseline import run_baseline
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.vinuni_search import search_vinuni_info, get_scholarship_info

# ── TEST CASES (tái dùng từ test_vinuni_agent.py) ──────────────────────────
TEST_CASES = [
    ("Điều kiện tuyển sinh VinUni là gì?",         ["tuyen sinh", "admission", "vinuni"]),
    ("VinUni có những ngành học nào?",              ["program", "nganh", "engineering", "business"]),
    ("Học bổng VinUni có những loại nào?",          ["hoc bong", "scholarship"]),
    ("Học phí VinUni là bao nhiêu?",                ["phi", "hoc phi", "tuition", "fee", "chi phi", "le phi"]),
    ("Quy trình nộp hồ sơ tuyển sinh?",             ["ho so", "apply", "application", "nop"]),
    ("VinUni thành lập năm nào?",                   ["vinuni", "university", "founded"]),
    ("Trường VinUni ở đâu?",                        ["ha noi", "hanoi", "campus", "vinuni"]),
    ("Có hỗ trợ tài chính không?",                  ["tai chinh", "financial", "ho tro", "support", "hoc bong"]),
    ("Yêu cầu tiếng Anh như thế nào?",             ["english", "ielts", "tieng anh", "language", "ngoai ngu"]),
    ("VinUni có ký túc xá không?",                  ["dormitory", "ky tuc xa", "housing", "campus", "sinh vien"]),
    ("Đối tác quốc tế của VinUni là gì?",           ["quoc te", "international", "partner", "cornell"]),
    ("Chuyên ngành kỹ thuật có những gì?",          ["ky thuat", "engineering", "khoa hoc", "technology"]),
    ("Xét học bổng dựa trên tiêu chí gì?",          ["hoc bong", "scholarship", "tieu chi", "criteria"]),
    ("Chương trình giảng dạy bằng ngôn ngữ gì?",   ["english", "tieng anh", "language", "instruction"]),
    ("VinUni khác gì các trường đại học khác?",     ["vinuni", "university", "unique", "different"]),
    ("Cần bao nhiêu điểm để vào VinUni?",           ["diem", "score", "admission", "requirement"]),
    ("Có chương trình học bổng toàn phần không?",   ["hoc bong", "scholarship", "full", "toan phan"]),
    ("Liên hệ tư vấn tuyển sinh ở đâu?",           ["contact", "lien he", "email", "tuyen sinh"]),
    ("VinUni có chương trình thạc sĩ không?",       ["master", "thac si", "graduate", "postgraduate"]),
    ("Thời hạn nộp hồ sơ là khi nào?",             ["deadline", "thoi han", "nop", "application"]),
]


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def contains_any(text: str, keywords: list) -> bool:
    norm = _normalize(text)
    return any(kw.lower() in norm for kw in keywords)


def build_tools():
    return [
        {
            "name": "search_vinuni_info",
            "description": "Tìm kiếm thông tin tuyển sinh VinUni theo từ khóa.",
            "func": search_vinuni_info,
        },
        {
            "name": "get_scholarship_info",
            "description": "Lấy thông tin học bổng và học phí VinUni.",
            "func": lambda _: get_scholarship_info(),
        },
    ]


def build_agent() -> ReActAgent:
    llm = OpenAIProvider(
        model_name="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return ReActAgent(llm=llm, tools=build_tools(), max_steps=5)


# ── CHẠY SO SÁNH ───────────────────────────────────────────────────────────

def run_comparison():
    print("\n" + "="*70)
    print("  SO SÁNH: Chatbot Baseline vs ReAct Agent")
    print("  Model: gpt-4o-mini  |  Số câu: 20")
    print("="*70)

    agent = build_agent()
    results = []

    for i, (question, keywords) in enumerate(TEST_CASES, 1):
        print(f"\n[{i:02d}/20] {question}")

        # ── Baseline ──
        t0 = time.time()
        try:
            b_ans = run_baseline(question)
            b_latency = int((time.time() - t0) * 1000)
            b_correct = contains_any(b_ans, keywords)
            b_error = None
        except Exception as e:
            b_ans, b_latency, b_correct, b_error = "", 0, False, str(e)

        # ── Agent ──
        t0 = time.time()
        try:
            a_ans = agent.run(question)
            a_latency = int((time.time() - t0) * 1000)
            a_correct = contains_any(a_ans, keywords)
            a_tokens = agent.last_run_usage.get("total_tokens", 0)
            a_steps = agent.last_run_usage.get("steps", 0)
            a_error = None
        except Exception as e:
            a_ans, a_latency, a_correct, a_tokens, a_steps, a_error = "", 0, False, 0, 0, str(e)

        results.append({
            "question":  question,
            "keywords":  keywords,
            "b_correct": b_correct,
            "b_latency": b_latency,
            "b_error":   b_error,
            "b_ans":     b_ans,
            "a_correct": a_correct,
            "a_latency": a_latency,
            "a_tokens":  a_tokens,
            "a_steps":   a_steps,
            "a_error":   a_error,
            "a_ans":     a_ans,
        })

        b_icon = "✅" if b_correct else "❌"
        a_icon = "✅" if a_correct else "❌"
        print(f"  Baseline: {b_icon}  {b_latency}ms")
        print(f"  Agent:    {a_icon}  {a_latency}ms  {a_tokens} tokens  {a_steps} steps")

    _print_summary(results)
    _save_markdown(results)


def _print_summary(results):
    b_correct  = sum(r["b_correct"] for r in results)
    a_correct  = sum(r["a_correct"] for r in results)
    b_lat_avg  = sum(r["b_latency"] for r in results) // len(results)
    a_lat_avg  = sum(r["a_latency"] for r in results) // len(results)
    a_tok_avg  = sum(r["a_tokens"]  for r in results) // len(results)
    a_step_avg = sum(r["a_steps"]   for r in results) / len(results)

    total = len(results)
    print("\n" + "="*70)
    print("  KẾT QUẢ TỔNG HỢP")
    print("="*70)
    print(f"  {'Tiêu chí':<35} {'Baseline':>12} {'Agent':>12}")
    print(f"  {'-'*59}")
    print(f"  {'Trả lời đúng':<35} {b_correct}/{total} ({b_correct/total:.0%}){'':<2} {a_correct}/{total} ({a_correct/total:.0%})")
    print(f"  {'Latency trung bình (ms)':<35} {b_lat_avg:>12,} {a_lat_avg:>12,}")
    print(f"  {'Tokens trung bình / câu':<35} {'N/A':>12} {a_tok_avg:>12,}")
    print(f"  {'Số bước trung bình':<35} {'1.0':>12} {a_step_avg:>12.1f}")
    print("="*70)

    # in câu sai
    b_wrong = [r for r in results if not r["b_correct"]]
    a_wrong = [r for r in results if not r["a_correct"]]

    if b_wrong:
        print(f"\n  Baseline sai ({len(b_wrong)} câu):")
        for r in b_wrong:
            print(f"    - {r['question']}")

    if a_wrong:
        print(f"\n  Agent sai ({len(a_wrong)} câu):")
        for r in a_wrong:
            print(f"    - {r['question']}")


def _save_markdown(results):
    total = len(results)
    b_correct = sum(r["b_correct"] for r in results)
    a_correct = sum(r["a_correct"] for r in results)
    b_lat_avg = sum(r["b_latency"] for r in results) // total
    a_lat_avg = sum(r["a_latency"] for r in results) // total
    a_tok_avg = sum(r["a_tokens"]  for r in results) // total

    lines = [
        "# Evaluation: Chatbot Baseline vs ReAct Agent",
        "",
        "## Chỉ số tổng hợp",
        "",
        "| Tiêu chí | Chatbot Baseline | ReAct Agent |",
        "|---|:---:|:---:|",
        f"| Trả lời đúng / {total} | {b_correct} ({b_correct/total:.0%}) | {a_correct} ({a_correct/total:.0%}) |",
        f"| Latency trung bình (ms) | {b_lat_avg:,} | {a_lat_avg:,} |",
        f"| Tokens trung bình / câu | N/A | {a_tok_avg:,} |",
        "",
        "## Chi tiết từng câu",
        "",
        "| # | Câu hỏi | Baseline | Agent |",
        "|---|---------|:---:|:---:|",
    ]

    for i, r in enumerate(results, 1):
        b = "✅" if r["b_correct"] else "❌"
        a = "✅" if r["a_correct"] else "❌"
        lines.append(f"| {i} | {r['question']} | {b} | {a} |")

    lines += [
        "",
        "## Câu trả lời mẫu (5 câu đầu)",
        "",
    ]
    for r in results[:5]:
        lines += [
            f"### {r['question']}",
            "",
            f"**Baseline:** {r['b_ans'][:300]}{'...' if len(r['b_ans']) > 300 else ''}",
            "",
            f"**Agent:** {r['a_ans'][:300]}{'...' if len(r['a_ans']) > 300 else ''}",
            "",
        ]

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "evaluation_results_real.md"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  Kết quả đã lưu: docs/evaluation_results_real.md")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Thiếu OPENAI_API_KEY trong .env")
        sys.exit(1)
    run_comparison()
