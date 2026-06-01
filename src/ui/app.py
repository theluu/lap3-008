import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def build_tools():
    from src.tools.vinuni_search import search_vinuni_info, get_scholarship_info
    return [
        {
            "name": "search_vinuni_info",
            "description": "Tìm kiếm thông tin tuyển sinh VinUni theo từ khóa. Input: câu hỏi hoặc từ khóa.",
            "func": search_vinuni_info,
        },
        {
            "name": "get_scholarship_info",
            "description": "Lấy thông tin học bổng và học phí VinUni. Không cần argument.",
            "func": lambda _: get_scholarship_info(),
        },
    ]


MODELS = {
    "OpenAI": {
        "gpt-4o-mini": "GPT-4o Mini (nhanh, rẻ)",
        "gpt-4o":      "GPT-4o (mạnh nhất)",
    },
    "Google Gemini": {
        "gemini-1.5-flash": "Gemini 1.5 Flash (nhanh, rẻ)",
        "gemini-1.5-pro":   "Gemini 1.5 Pro (mạnh)",
        "gemini-2.0-flash": "Gemini 2.0 Flash (mới nhất)",
    },
}


def get_agent(provider_name: str, model_name: str):
    key = f"agent_{provider_name}_{model_name}"
    if key not in st.session_state:
        from src.agent.agent import ReActAgent
        if provider_name == "OpenAI":
            from src.core.openai_provider import OpenAIProvider
            llm = OpenAIProvider(model_name=model_name, api_key=os.getenv("OPENAI_API_KEY"))
        elif provider_name == "Google Gemini":
            from src.core.gemini_provider import GeminiProvider
            llm = GeminiProvider(model_name=model_name, api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        st.session_state[key] = ReActAgent(llm=llm, tools=build_tools(), max_steps=5)
    return st.session_state[key]


def render_message(msg: dict, show_token_cost: bool):
    """Render một message với tuỳ chọn hiển thị token cost (V2)."""
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if show_token_cost and msg["role"] == "assistant" and "usage" in msg:
            u = msg["usage"]
            st.caption(
                f"⏱ {msg.get('elapsed_ms', 0)} ms · "
                f"🔢 {u['total_tokens']:,} tokens "
                f"({u['prompt_tokens']:,} in / {u['completion_tokens']:,} out) · "
                f"💰 ${u['cost']:.4f} · "
                f"🔄 {u['steps']} steps"
            )


def main():
    st.set_page_config(
        page_title="VinUni Admissions Q&A",
        page_icon="🎓",
        layout="wide",
    )

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

    tab_chat, tab_arch, tab_compare = st.tabs(["💬 Chat", "📐 Architecture", "📊 So sánh"])

    # ── Architecture Tab ──────────────────────────────────────────────────
    with tab_arch:
        st.header("ReAct Agent — Luồng hoạt động")
        st.markdown("""
```
User hỏi
  └─► ReActAgent.run()
        └─► LLM generate (Thought + Action)
              ├─► Parse: Final Answer? ──► Trả lời user ✓
              ├─► Parse: Action found?
              │     ├─► Validate tool name
              │     │     ├─► Hợp lệ → execute_tool() → Observation → lặp lại
              │     │     └─► Không hợp lệ → HALLUCINATION_ERROR log → nudge LLM
              │     └─► Parse fail → retry (max 2) → trả raw response
              └─► max_steps reached → fallback message
```
        """)

        st.header("Kiến trúc hệ thống")
        st.code("""
User → Streamlit UI (src/ui/app.py)
  → ReActAgent (src/agent/agent.py, max 5 steps)
    → Tool: search_vinuni_info(query)       [src/tools/vinuni_search.py]
      → data/vinuni_admissions.json         [scraped từ vinuni.edu.vn]
      → Unicode normalize + keyword match → top-3 chunks
    → Tool: get_scholarship_info()          [shortcut học bổng/học phí]
    → LLM tổng hợp Final Answer
  → Hiển thị response + ghi logs/YYYY-MM-DD.log (JSON)
        """, language="text")

        st.header("Tool Design Evolution")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("v1 — Keyword Search")
            st.markdown("""
- Tách từ đơn giản bằng `split()`
- Không xử lý tiếng Việt có dấu
- Score = số từ trùng khớp chính xác
- Kết quả: miss nhiều query không dấu
            """)
        with col2:
            st.subheader("v2 — Fuzzy + Unicode Normalize")
            st.markdown("""
- `_normalize()`: bỏ dấu Unicode trước khi so sánh
- Partial match: từ ngắn nằm trong từ dài cũng tính
- Score = exact×2 + partial
- Kết quả: tìm đúng cả query có/không dấu
            """)

    # ── So sánh Tab ───────────────────────────────────────────────────────
    with tab_compare:
        import unicodedata

        TEST_CASES = [
            ("Điều kiện tuyển sinh VinUni là gì?",        ["tuyen sinh", "admission", "vinuni"]),
            ("Học bổng VinUni có những loại nào?",         ["hoc bong", "scholarship"]),
            ("Học phí VinUni là bao nhiêu?",               ["phi", "hoc phi", "tuition", "fee", "chi phi"]),
            ("Yêu cầu tiếng Anh như thế nào?",            ["english", "ielts", "tieng anh", "language"]),
            ("Đối tác quốc tế của VinUni là gì?",          ["quoc te", "international", "partner", "cornell"]),
            ("Có chương trình học bổng toàn phần không?",  ["hoc bong", "scholarship", "full", "toan phan"]),
            ("Quy trình nộp hồ sơ tuyển sinh?",            ["ho so", "apply", "application", "nop"]),
            ("VinUni có những ngành học nào?",             ["program", "nganh", "engineering", "business"]),
        ]

        def _normalize(text):
            nfkd = unicodedata.normalize("NFKD", text.lower())
            return "".join(c for c in nfkd if not unicodedata.combining(c))

        def _contains_any(text, keywords):
            norm = _normalize(text)
            return any(kw in norm for kw in keywords)

        st.header("📊 Baseline vs ReAct Agent")
        st.caption("Chạy 8 câu hỏi đại diện qua cả 2 phía, so sánh kết quả trực tiếp.")

        if st.button("▶ Chạy so sánh", type="primary"):
            from src.chatbot.baseline import run_baseline

            agent = get_agent("OpenAI", "gpt-4o-mini")
            rows = []
            progress = st.progress(0, text="Đang chạy...")

            for i, (q, kws) in enumerate(TEST_CASES):
                progress.progress((i + 1) / len(TEST_CASES), text=f"[{i+1}/8] {q[:40]}...")

                # Baseline
                t0 = time.time()
                try:
                    b_ans = run_baseline(q)
                    b_lat = int((time.time() - t0) * 1000)
                    b_ok  = _contains_any(b_ans, kws)
                except Exception as e:
                    b_ans, b_lat, b_ok = f"Lỗi: {e}", 0, False

                # Agent
                t0 = time.time()
                try:
                    a_ans = agent.run(q)
                    a_lat = int((time.time() - t0) * 1000)
                    a_ok  = _contains_any(a_ans, kws)
                    a_tok = agent.last_run_usage.get("total_tokens", 0)
                except Exception as e:
                    a_ans, a_lat, a_ok, a_tok = f"Lỗi: {e}", 0, False, 0

                rows.append({
                    "q": q, "kws": kws,
                    "b_ok": b_ok, "b_lat": b_lat, "b_ans": b_ans,
                    "a_ok": a_ok, "a_lat": a_lat, "a_tok": a_tok, "a_ans": a_ans,
                })

            progress.empty()
            st.session_state["compare_results"] = rows

        # Hiển thị kết quả nếu đã chạy
        if "compare_results" in st.session_state:
            rows = st.session_state["compare_results"]
            n = len(rows)
            b_score = sum(r["b_ok"] for r in rows)
            a_score = sum(r["a_ok"] for r in rows)
            b_lat   = sum(r["b_lat"] for r in rows) // n
            a_lat   = sum(r["a_lat"] for r in rows) // n
            a_tok   = sum(r["a_tok"] for r in rows) // n

            # Tổng hợp
            c1, c2, c3 = st.columns(3)
            c1.metric("Baseline đúng",  f"{b_score}/{n}", f"{b_score/n:.0%}")
            c2.metric("Agent đúng",     f"{a_score}/{n}", f"{a_score/n:.0%}",
                      delta_color="normal" if a_score >= b_score else "inverse")
            c3.metric("Agent avg token", f"{a_tok:,}")

            col1, col2 = st.columns(2)
            col1.metric("Baseline avg latency", f"{b_lat} ms")
            col2.metric("Agent avg latency",    f"{a_lat} ms")

            st.divider()

            # Bảng chi tiết
            st.subheader("Chi tiết từng câu")
            for i, r in enumerate(rows, 1):
                b_icon = "✅" if r["b_ok"] else "❌"
                a_icon = "✅" if r["a_ok"] else "❌"
                with st.expander(f"{b_icon} / {a_icon}  {r['q']}"):
                    cl, cr = st.columns(2)
                    with cl:
                        st.markdown(f"**Baseline** {b_icon} · {r['b_lat']} ms")
                        st.write(r["b_ans"])
                    with cr:
                        st.markdown(f"**Agent** {a_icon} · {r['a_lat']} ms · {r['a_tok']} tokens")
                        st.write(r["a_ans"])

    # ── Chat Tab ──────────────────────────────────────────────────────────
    with tab_chat:
        st.title("🎓 VinUni Admissions Assistant")
        st.caption("Hỏi đáp về tuyển sinh khóa đầu tiên vào Đại học VinUni")

        # Init state trước — đảm bảo sidebar đọc giá trị mới nhất
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "total_queries" not in st.session_state:
            st.session_state.total_queries = 0
        if "latencies" not in st.session_state:
            st.session_state.latencies = []
        if "total_tokens" not in st.session_state:
            st.session_state.total_tokens = 0
        if "total_cost" not in st.session_state:
            st.session_state.total_cost = 0.0

        # Version và provider được lưu bởi widget key
        app_version = st.session_state.get("app_version", "Version 1 — Cơ bản")
        show_token_cost = (app_version == "Version 2 — Tính phí token")
        selected_provider = st.session_state.get("selected_provider", "OpenAI") if show_token_cost else "OpenAI"
        selected_model    = st.session_state.get("selected_model", "gpt-4o-mini")

        # Chat history (mỗi msg có thể kèm usage nếu là assistant)
        for msg in st.session_state.messages:
            render_message(msg, show_token_cost)

        # Chat input
        if prompt := st.chat_input("Hỏi về tuyển sinh VinUni..."):
            user_msg = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_msg)
            render_message(user_msg, show_token_cost)

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

            assistant_msg = {
                "role": "assistant",
                "content": response,
                "usage": usage,
                "elapsed_ms": elapsed_ms,
            }
            st.session_state.messages.append(assistant_msg)
            st.session_state.total_queries += 1

        # Sidebar render SAU khi state đã cập nhật
        with st.sidebar:
            st.header("⚙️ Cài đặt")

            # ── Version selector ──────────────────────────────────────────
            st.radio(
                "Chế độ hiển thị",
                options=["Version 1 — Cơ bản", "Version 2 — Tính phí token"],
                key="app_version",
                help=(
                    "**V1**: Không hiển thị thông tin token/chi phí.\n\n"
                    "**V2**: Hiển thị số token và chi phí sau mỗi câu trả lời."
                ),
            )

            st.divider()

            # V2: chọn provider trước, rồi model tương ứng
            if show_token_cost:
                st.radio(
                    "Provider",
                    options=list(MODELS.keys()),
                    key="selected_provider",
                )
                active_provider = st.session_state.get("selected_provider", "OpenAI")
            else:
                active_provider = "OpenAI"

            model_options = MODELS[active_provider]
            # Reset model nếu model cũ không thuộc provider mới
            current_model = st.session_state.get("selected_model", "")
            if current_model not in model_options:
                st.session_state["selected_model"] = list(model_options.keys())[0]

            selected_model = st.selectbox(
                "Model",
                options=list(model_options.keys()),
                format_func=lambda m: model_options[m],
                key="selected_model",
            )
            st.caption(f"Đang dùng: `{active_provider}` / `{selected_model}`")

            st.divider()
            if st.button("🗑️ Xóa lịch sử"):
                st.session_state.messages = []
                st.session_state.latencies = []
                st.session_state.total_queries = 0
                st.session_state.total_tokens = 0
                st.session_state.total_cost = 0.0
                st.rerun()

            st.divider()
            st.header("📊 Thống kê")
            st.metric("Tổng câu hỏi", st.session_state.total_queries)

            if st.session_state.latencies:
                lats = st.session_state.latencies
                st.metric("Avg Latency", f"{sum(lats) // len(lats)} ms")
                st.metric("Last Query", f"{lats[-1]} ms")

            # Token & Chi phí — chỉ hiện ở Version 2
            if show_token_cost:
                st.divider()
                st.header("🔢 Token & Chi phí")
                st.metric("Tổng Tokens", f"{st.session_state.total_tokens:,}")
                cost = st.session_state.total_cost
                st.metric("Tổng Chi phí", f"${cost:.4f}")
                if st.session_state.total_queries > 0:
                    avg_cost = cost / st.session_state.total_queries
                    st.caption(f"~${avg_cost:.4f} / câu hỏi")


if __name__ == "__main__":
    main()
