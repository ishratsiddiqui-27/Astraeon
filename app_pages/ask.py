"""Ask Astraeon: questions answered only from the project's data files, with numbered sources (RAG).

Needs GEMINI_API_KEY: in Streamlit secrets when deployed, or in the git-ignored .env file locally (never in the
repo). Without a key the page still works as a search over the same passages.
"""
import os

import streamlit as st

from astraeon import rag, ui

MAX_QUESTIONS = 20          # per browser session, to stay inside the free Gemini quota
MAX_CHARS = 500
SUGGESTIONS = {
    ":material/nightlight: Which experiments tested fire at Moon-base air?":
        "Which experiments tested fire at Moon-base air?",
    ":material/water_drop: Why is FLEX a near miss?": "Why is FLEX only a near miss for a Moon base?",
    ":material/history: What happened in the Mir fire?": "What happened in the Mir fire, and which experiments relate to it?",
    ":material/help_outline: What don't we know yet?": "What can't the PSI data tell us about fire on the Moon?",
}


@st.cache_resource
def get_retriever() -> rag.Retriever:
    return rag.Retriever(rag.build_corpus())


def secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:              # no secrets file at all (e.g. a fresh Codespace)
        value = None
    return value or os.environ.get(name)


def show_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})", icon=":material/menu_book:"):
        for s in sources:
            title = ui.md(s["title"])
            label = f"[{title}]({s['source']})" if s["source"].startswith("http") else f"{title} · {ui.md(s['source'])}"
            st.markdown(f"**[{s['n']}]** {label}")
            for quote in s["quotes"]:
                st.caption(ui.md(quote))


rag.load_dotenv()           # local runs: read GEMINI_API_KEY from .env
api_key = secret("GEMINI_API_KEY") or secret("GOOGLE_API_KEY")
model = secret("GEMINI_MODEL") or rag.MODEL
if "ask_history" not in st.session_state:
    st.session_state.ask_history = []
history = st.session_state.ask_history

st.title("Ask Astraeon", anchor=False)
st.caption("Answers come only from Astraeon's data: the NASA PSI experiments, the Moon-base test records, the "
           "rankings, fire history and research gaps. Every answer lists its sources.")
if not api_key:
    st.info("AI answers are off because no API key is set, so questions return the most relevant passages "
            "from the data instead.", icon=":material/key_off:")

for msg in history:
    with st.chat_message(msg["role"], avatar=":material/rocket_launch:" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])
        show_sources(msg.get("sources", []))

asked = sum(1 for m in history if m["role"] == "user")
prompt = st.chat_input("Ask about the experiments, Moon-base air or fire history", max_chars=MAX_CHARS,
                       submit_mode="disable", disabled=asked >= MAX_QUESTIONS)
if asked >= MAX_QUESTIONS:
    st.caption(f"That's the {MAX_QUESTIONS}-question limit for this session. Reload the page to start over.")

if not history:
    suggestions = st.empty()
    picked = suggestions.pills("Try asking", list(SUGGESTIONS), label_visibility="collapsed", key="ask_suggestion")
    if picked:
        prompt = SUGGESTIONS[picked]
    if prompt:
        suggestions.empty()

if prompt:
    question = prompt.strip()[:MAX_CHARS]
    history.append({"role": "user", "content": ui.md(question)})
    with st.chat_message("user"):
        st.markdown(ui.md(question))

    with st.chat_message("assistant", avatar=":material/rocket_launch:"):
        retriever = get_retriever()
        failed = False
        if not api_key:
            hits = retriever.search(question, k=3)
            if hits:
                text = "AI answers are off, so here are the closest passages from the Astraeon data."
                sources = [{"n": i, "title": d.title, "source": d.source, "quotes": d.blocks[:3]}
                           for i, (d, _) in enumerate(hits, start=1)]
            else:
                text, sources = "Nothing in the Astraeon data matches that question.", []
        else:
            earlier = [(history[i]["content"], history[i + 1]["content"])
                       for i in range(max(0, len(history) - 5), len(history) - 1, 2)
                       if history[i]["role"] == "user" and history[i + 1]["role"] == "assistant"][-2:]
            try:
                with st.spinner("Searching the data and writing an answer..."):
                    result = rag.answer(question, retriever, api_key, model=model, earlier=earlier,
                                        n_experiments=len(ui.experiments()))
                text, sources = result["text"] or "No answer came back. Try rephrasing.", result["sources"]
            except Exception as exc:
                message = rag.friendly_error(exc)
                if message is None:
                    raise
                text, sources, failed = message, [], True
        if failed:
            st.error(text, icon=":material/error:")
        else:
            st.markdown(text)
        show_sources(sources)
    history.append({"role": "assistant", "content": text, "sources": sources})
