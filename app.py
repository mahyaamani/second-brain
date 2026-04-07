"""
Second Brain — Streamlit UI with knowledge graph sidebar.
Run with: streamlit run app.py
"""

import queue
from pathlib import Path
from dotenv import load_dotenv
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components

load_dotenv()

import agent
from tools import wiki as wiki_tools
from tools import interaction
from tools.graph_extractor import extract_knowledge_graph

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Second Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "history": [],
    "messages": [],
    "pending_question": None,
    "waiting_for_answer": False,
    "answer_queue": queue.Queue(),
    "running": False,
    "graph_expanded": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Graph helpers ─────────────────────────────────────────────────────────────
NODE_COLORS = {"question": "#e74c3c", "concept": "#3498db",
               "wiki_page": "#2ecc71", "web_source": "#f39c12", "fact": "#9b59b6"}
NODE_SHAPES = {"question": "star", "concept": "dot",
               "wiki_page": "square", "web_source": "triangle", "fact": "diamond"}
NODE_SIZES  = {"question": 35, "concept": 22, "wiki_page": 20, "web_source": 18, "fact": 16}


def render_graph(graph_data: dict, height: int = 500):
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes:
        st.caption("No graph data yet.")
        return
    net = Network(height=f"{height}px", width="100%",
                  bgcolor="#0d1117", font_color="#ffffff", directed=True)
    net.barnes_hut(gravity=-6000, central_gravity=0.3, spring_length=140)
    for n in nodes:
        t = n.get("type", "concept")
        net.add_node(n["id"], label=n["label"],
                     color=NODE_COLORS.get(t, "#888"), shape=NODE_SHAPES.get(t, "dot"),
                     size=NODE_SIZES.get(t, 20), font={"size": 13, "face": "Arial"},
                     title=f"[{t}] {n['label']}")
    for e in edges:
        net.add_edge(e["from"], e["to"], label=e.get("label", ""),
                     color="#555", font={"size": 10, "color": "#aaa"},
                     arrows="to", smooth={"type": "curvedCW", "roundness": 0.2})
    components.html(net.generate_html(notebook=False), height=height + 10, scrolling=False)
    legend = " &nbsp;|&nbsp; ".join(
        f'<span style="color:{NODE_COLORS[t]}">{sym} {t.replace("_"," ")}</span>'
        for t, sym in [("question","★"),("concept","●"),("wiki_page","■"),("web_source","▲")])
    st.markdown(f'<div style="font-size:0.72rem;color:#666;margin-top:4px">{legend}</div>',
                unsafe_allow_html=True)


# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Right sidebar column */
div[data-testid="stHorizontalBlock"]
  > div[data-testid="stColumn"]:last-child {
    background-color: #0d1117!important;
    border-left: 1px solid #30363d!important;
    min-height: 100vh!important;
    padding: 1rem 0.8rem!important;
}

/* Collapsed right sidebar — center content vertically */
.sidebar-collapsed-label {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    color: #8b949e;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    margin: auto;
    padding-top: 1rem;
}

.tool-call {
    font-size: 0.78em; color: #888;
    background: #161b22;
    border-left: 3px solid #444;
    padding: 4px 10px; margin: 2px 0;
    border-radius: 0 4px 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Left sidebar — wiki ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 Second Brain")
    st.caption("Your persistent AI knowledge base")
    st.divider()
    st.subheader("📚 Wiki Pages")
    wiki_dir = Path(__file__).parent / "wiki"
    pages = sorted(
        str(p.relative_to(wiki_dir)).removesuffix(".md").replace("\\", "/")
        for p in wiki_dir.rglob("*.md") if p.stem not in ("index", "log")
    )
    if pages:
        sel = st.selectbox("Browse pages", ["— select —"] + pages)
        if sel and sel != "— select —":
            st.markdown(f"**`{sel}`**")
            st.markdown(wiki_tools.read_wiki_page(sel))
    else:
        st.info("No wiki pages yet. Start chatting!")
    st.divider()
    st.subheader("📋 Activity log")

    log_path = wiki_dir / "log.md"
    log_entries = []  # list of {"date": str, "time": str, "text": str}
    if log_path.exists():
        import re
        for line in log_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\*\*(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})\*\* — (.+)", line)
            if m:
                log_entries.append({"date": m.group(1), "time": m.group(2), "text": m.group(3)})

    if log_entries:
        # Search controls
        keyword = st.text_input("Search by keyword", placeholder="e.g. nutrition, goals…",
                                label_visibility="collapsed", key="log_keyword")
        all_dates = sorted({e["date"] for e in log_entries}, reverse=True)
        date_options = ["All dates"] + all_dates
        selected_date = st.selectbox("Filter by date", date_options,
                                     label_visibility="collapsed", key="log_date")

        # Filter
        filtered = log_entries
        if selected_date != "All dates":
            filtered = [e for e in filtered if e["date"] == selected_date]
        if keyword.strip():
            kw = keyword.strip().lower()
            filtered = [e for e in filtered if kw in e["text"].lower() or kw in e["date"]]

        filtered = list(reversed(filtered))   # newest first

        st.caption(f"{len(filtered)} of {len(log_entries)} entries")

        for e in filtered:
            st.markdown(
                f'<div style="border-left:2px solid #30363d;padding:4px 8px;margin:4px 0">'
                f'<span style="font-size:0.7rem;color:#8b949e">{e["date"]} {e["time"]}</span><br>'
                f'<span style="font-size:0.8rem;color:#c9d1d9">{e["text"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No activity yet.")

    st.divider()
    if st.button("🔄 Refresh wiki", use_container_width=True):
        st.rerun()

# ── Latest graph ──────────────────────────────────────────────────────────────
latest_graph_msg = next(
    (m for m in reversed(st.session_state.messages)
     if m["role"] == "assistant" and m.get("graph")), None)
latest_graph = latest_graph_msg["graph"] if latest_graph_msg else None

# ── Layout ────────────────────────────────────────────────────────────────────
expanded = st.session_state.graph_expanded
chat_col, graph_col = st.columns([5, 2] if expanded else [10, 1], gap="small")

# ── Chat column ───────────────────────────────────────────────────────────────
with chat_col:
    st.header("Chat")

    for msg in st.session_state.messages:
        role = msg["role"]
        if role == "tool":
            st.markdown(f'<div class="tool-call">⚙️ {msg["content"]}</div>',
                        unsafe_allow_html=True)
        elif role == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(msg["content"])

    if st.session_state.waiting_for_answer and st.session_state.pending_question:
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(f"**{st.session_state.pending_question}**")
        answer = st.chat_input("Your answer…")
        if answer:
            st.session_state.messages.append({"role": "user", "content": answer})
            st.session_state.answer_queue.put(answer)
            st.session_state.waiting_for_answer = False
            st.session_state.pending_question = None
            st.rerun()

    elif not st.session_state.running:
        user_input = st.chat_input(
            "Ask anything — try: 'research stoicism' | 'interview me about my goals'")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.running = True

            def ui_ask_user(q):
                st.session_state.pending_question = q
                st.session_state.waiting_for_answer = True
                return st.session_state.answer_queue.get()
            interaction.ask_user = ui_ask_user

            collected: list[str] = []
            import agent as _agent
            orig = dict(_agent.TOOL_DISPATCH)

            def make_logged(name, fn):
                def logged(args):
                    parts = [f"{k}={str(v)[:52]!r}" for k, v in args.items()]
                    s = f"{name}({', '.join(parts)})"
                    collected.append(s)
                    st.session_state.messages.append({"role": "tool", "content": s})
                    return fn(args)
                return logged

            for name, fn in orig.items():
                _agent.TOOL_DISPATCH[name] = make_logged(name, fn)

            with st.spinner("Thinking…"):
                try:
                    response, new_history = agent.run(user_input, st.session_state.history)
                    st.session_state.history = new_history
                    graph_data = extract_knowledge_graph(user_input, response, collected)
                    st.session_state.messages.append({
                        "role": "assistant", "content": response,
                        "graph": graph_data, "tool_calls": list(collected),
                    })
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"❌ Error: {e}"})
                finally:
                    _agent.TOOL_DISPATCH.update(orig)

            st.session_state.running = False
            st.rerun()
    else:
        st.chat_input("Waiting for response…", disabled=True)

# ── Right graph sidebar ───────────────────────────────────────────────────────
with graph_col:
    if expanded:
        # Header with collapse button
        title_col, btn_col = st.columns([4, 1])
        with title_col:
            st.subheader("Knowledge Graph")
        with btn_col:
            if st.button("›", help="Collapse", use_container_width=True):
                st.session_state.graph_expanded = False
                st.rerun()
        st.divider()

        if latest_graph:
            n_nodes = len(latest_graph.get("nodes", []))
            n_edges = len(latest_graph.get("edges", []))
            st.caption(f"{n_nodes} nodes · {n_edges} edges")
            render_graph(latest_graph, height=500)

            past = [(i, m) for i, m in enumerate(st.session_state.messages)
                    if m["role"] == "assistant" and m.get("graph") and m is not latest_graph_msg]
            if past:
                with st.expander(f"Previous graphs ({len(past)})"):
                    for i, m in past:
                        label = next(
                            (st.session_state.messages[j]["content"][:55]
                             for j in range(i - 1, -1, -1)
                             if st.session_state.messages[j]["role"] == "user"), "Exchange")
                        st.caption(f"**{label}**")
                        render_graph(m["graph"], height=260)
                        st.divider()
        else:
            st.caption("Graph will appear here after your first message.")
            st.markdown("""
- ★ question
- ● concept
- ■ wiki page
- ▲ web source
""")
    else:
        # Collapsed — show just a toggle button
        if st.button("‹", help="Expand graph", use_container_width=True):
            st.session_state.graph_expanded = True
            st.rerun()
        st.markdown('<div class="sidebar-collapsed-label">Knowledge Graph</div>',
                    unsafe_allow_html=True)
