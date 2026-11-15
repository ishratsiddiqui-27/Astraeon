"""Ask Astraeon: retrieval-augmented answers (RAG) grounded in this repo's data files, with numbered sources.

1. build_corpus()  turns the data files into small passages ("documents"), each made of short text blocks.
2. Retriever       ranks passages for a question with BM25 (keyword search; pure Python, no extra packages).
3. answer()        sends the best passages to Google Gemini, numbered [1], [2], ..., and tells it to answer only
                   from them and cite the numbers. The [n] markers in the reply become the source list.

Only answer() needs the `google-genai` package and a Gemini API key; corpus building and retrieval run anywhere.
"""
from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field

from . import data
from .data import MOON_O2_MIN, MOON_PSI_MAX, MOON_STATUSES, NOT_REPORTED, SCORE_COLUMNS, show

MODEL = "gemini-3.8-flash"    # stable and on Gemini's free tier; override with GEMINI_MODEL
MAX_OUTPUT_TOKENS = 4096      # includes the model's thinking tokens; answers are asked to stay short
TOP_K = 8                     # passages sent per question (plus the dataset overview)

SYSTEM_PROMPT = f"""You answer questions about Astraeon, a NASA Space Apps project on fire safety for spacecraft \
and a future Moon base. Its data covers {{n}} NASA Physical Sciences Informatics (PSI) microgravity combustion \
experiments, their per-test oxygen and pressure records, the team's relevance rankings, three spaceflight fire \
incidents, and known research gaps.

Each message gives you numbered passages from that data. They are your only source of facts. Answer from them, \
and after each claim cite the passages it comes from by number in square brackets, like [2] or [1][3]. If the \
passages don't contain the answer, say the Astraeon data doesn't cover it; don't fill the gap from general \
knowledge. A blank or "{NOT_REPORTED}" value means the source doesn't report it, never zero.

The Moon-base zone is {MOON_O2_MIN:g}% oxygen or more at {MOON_PSI_MAX:g} psi or less (NASA Space Apps challenge \
brief). No PSI experiment ran in partial gravity, so Moon relevance is inferred from oxygen and pressure only; \
say so when an answer depends on lunar gravity.

Write for students and engineers: plain words, short paragraphs, under 150 words unless a list is clearer. Quote \
numbers exactly as the passages give them, with units."""


@dataclass
class Doc:
    """One retrievable passage. `blocks` are the citable units (shown as quotes under each source)."""
    doc_id: str
    title: str
    source: str
    blocks: list[str]
    kind: str
    tokens: Counter = field(default_factory=Counter, repr=False)
    length: int = 0


# --- Corpus ------------------------------------------------------------------------------------------------
def _field(label: str, value) -> str:
    return f"{label}: {show(value).rstrip('.')}"


def _experiment_docs(records: list[dict], tests: list[dict]) -> list[Doc]:
    by_experiment: dict[str, list[dict]] = {}
    for t in tests:
        by_experiment.setdefault(t["id"], []).append(t)
    docs = []
    for r in records:
        status = MOON_STATUSES.get(r["moon_status"], {}).get("label", r["moon_status"])
        scores = ", ".join(f"{label} {show(r[col])}/10" for label, col in SCORE_COLUMNS.items())
        blocks = [
            f"{r['short_name']} full name: {r['name']}.",
            _field("Topic", r["topic"]) + ". " + _field("Study type", r["study_type"]) + ".",
            _field("Fuel", r["fuel_detail"] or r["fuel_type"]) + ".",
            _field("Hardware", r["hardware"]) + ".",
            _field("Oxygen", r["o2_percent"]) + ". " + _field("Pressure", r["pressure_psi"]) + ".",
            _field("Gravity", r["gravity"]) + ". " + _field("Airflow", r["airflow"]) + ".",
            _field("Objective", r["objective"]),
            _field("What was varied", r["what_varied"]) + ". " + _field("What stayed the same", r["what_same"]) + ".",
            _field("Sensors", r["sensors"]) + ".",
            _field("Plain-language summary", r["simple_summary"]),
            _field("Why it matters", r["why_it_matters"]),
            f"Moon status: {status}. {show(r['moon_takeaway'])}",
            f"Moon-base evidence level: {r['evidence_label']}. {show(r['evidence_detail'])}",
            f"Relevance scores (0 to 10): {scores}. Reason: {show(r['reason'])}",
            _field("Flight platform", r["flight_platform"]) + ". "
            + f"Investigation dates: {show(r['investigation_start'])} to {show(r['investigation_end'])}.",
        ]
        if r.get("notes"):
            blocks.append(_field("Data notes", r["notes"]))
        runs = by_experiment.get(r["id"], [])
        if runs:
            o2s = [t["o2_percent"] for t in runs]
            psis = [t["pressure_psi"] for t in runs]
            zone = [t for t in runs if t["in_zone"]]
            hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
            blocks.append(
                f"PSI per-test records for {r['short_name']}: {len(runs)} flight tests, chamber oxygen "
                f"{min(o2s):g} to {max(o2s):g}%, pressure {min(psis):.2f} to {max(psis):.2f} psi. "
                f"{len(zone)} tests ran inside the Moon-base zone ({MOON_O2_MIN:g}% oxygen or more, "
                f"{MOON_PSI_MAX:g} psi or less), {hot} of them with hot ignition."
            )
        docs.append(Doc(f"exp:{r['id']}", f"{r['short_name']}: {r['name']}", r["source_link"] or f"experiment:{r['id']}",
                        [b for b in blocks if b], "experiment"))
    return docs


def _markdown_docs(file_name: str, label: str, skip: tuple[str, ...]) -> list[Doc]:
    """Split a Markdown file into one passage per ## / ### section; paragraphs and tables become blocks."""
    path = data.DATA_DIR / file_name
    if not path.exists():
        return []
    docs, heading, lines = [], None, []

    def flush():
        if heading and not heading.lower().startswith(skip):
            text = "\n".join(lines).strip()
            blocks = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and p.strip() != "---"]
            if blocks:
                docs.append(Doc(f"{file_name}#{heading}", f"{label}: {heading}", f"{file_name} - {heading}",
                                blocks, "notes"))

    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{2,3}\s+(.*)", line)
        if match:
            flush()
            heading, lines = match.group(1).strip(), []
        else:
            lines.append(line)
    flush()
    return docs


def _overview_doc(records: list[dict], tests: list[dict]) -> Doc:
    """Dataset-wide counts, computed from the files. Sent with every question."""
    neither = [r for r in records if show(r["o2_percent"]) == NOT_REPORTED and show(r["pressure_psi"]) == NOT_REPORTED]
    study = Counter(r["study_type"] or "not reported" for r in records)
    zone = [t for t in tests if t["in_zone"]]
    hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
    names = {r["id"]: r["short_name"] for r in records}
    status_lines = []
    for status, look in MOON_STATUSES.items():
        members = [r["short_name"] for r in records if r["moon_status"] == status]
        if members:
            status_lines.append(f"{look['label']}: {len(members)} ({', '.join(members)})")
    return Doc("overview", "Astraeon dataset overview", "Astraeon data files (computed counts)", [
        f"The dataset has {len(records)} NASA PSI combustion experiments: "
        + ", ".join(f"{n} {k}" for k, n in study.most_common()) + ".",
        f"{sum(1 for r in records if show(r['o2_percent']) != NOT_REPORTED)} of {len(records)} report oxygen, "
        f"{sum(1 for r in records if show(r['pressure_psi']) != NOT_REPORTED)} report pressure, and {len(neither)} "
        "report neither.",
        f"Per-test records: {len(tests)} flight tests from {len({t['id'] for t in tests})} experiments "
        f"({', '.join(sorted({names.get(t['id'], t['id']) for t in tests}))}) record chamber oxygen and pressure "
        f"for each test. {len(zone)} of them ran in the Moon-base zone ({MOON_O2_MIN:g}% oxygen or more, "
        f"{MOON_PSI_MAX:g} psi or less), all from {', '.join(sorted({names.get(t['id'], t['id']) for t in zone})) or 'none'}; "
        f"{hot} had hot ignition.",
        "Moon status of the experiments: " + "; ".join(status_lines) + ".",
        "Experiments in the dataset: " + ", ".join(r["short_name"] for r in records) + ".",
    ], "overview")


def build_corpus() -> list[Doc]:
    records = data.load_all_records()
    tests = data.load_moon_tests()
    docs = [_overview_doc(records, tests), *_experiment_docs(records, tests)]
    docs += _markdown_docs("DATA_NOTES.md", "Data notes", skip=("1.",))
    docs += _markdown_docs("RANKINGS_NOTES.md", "Rankings notes", skip=("changes",))
    docs += _markdown_docs("about.md", "About Astraeon", skip=())
    for inc in data.load_incidents():
        blocks = [f"{inc['name']} ({inc.get('date', '')}).", inc.get("summary", "")]
        if inc.get("related_names"):
            blocks.append("Related experiments in Astraeon: " + ", ".join(inc["related_names"]) + ".")
        if inc.get("data_note"):
            blocks.append(inc["data_note"])
        sources = inc.get("sources") or []
        docs.append(Doc(f"incident:{inc['id']}", f"Incident: {inc['name']}", sources[0] if sources else f"incident:{inc['id']}",
                        [b for b in blocks if b], "incident"))
    for gap in data.load_research_gaps():
        blocks = [gap.get("summary", ""), gap.get("evidence", "")]
        if gap.get("related_names"):
            blocks.append("Related experiments: " + ", ".join(gap["related_names"]) + ".")
        docs.append(Doc(f"gap:{gap['id']}", f"Research gap: {gap['title']}", f"Astraeon research gaps ({gap.get('source', '')})",
                        [b for b in blocks if b], "gap"))
    for atm in data.load_atmospheres():
        docs.append(Doc(f"atmosphere:{atm['id']}", f"Atmosphere: {atm['name']}", atm.get("source_link") or atm.get("source", ""),
                        [f"{atm['name']}: {atm['o2_percent']}% oxygen at {atm['pressure_psi']} psi.", atm.get("note", ""),
                         f"Source: {atm.get('source', '')}"], "atmosphere"))
    for term, definition in data.load_glossary().items():
        docs.append(Doc(f"glossary:{term}", f"Glossary: {term}", "Astraeon glossary", [f"{term}: {definition}"], "glossary"))
    return docs


# --- Retrieval (BM25) ------------------------------------------------------------------------------------
STOPWORDS = set("""a an and are as at be by can did do does for from had has have how i if in into is it its of on or
that the their them there these this those to was were what when where which who why will with you your about any
tell me show give""".split())
SYNONYMS = {"lunar": "moon", "o2": "oxygen", "psia": "psi", "fires": "fire", "flames": "flame", "tests": "test",
            "experiments": "experiment", "extinguish": "suppression", "extinguisher": "suppression",
            "smoke": "detection", "detector": "detection", "safe": "safety"}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower())
    return [SYNONYMS.get(w, w) for w in words if w not in STOPWORDS]


class Retriever:
    def __init__(self, docs: list[Doc], k1: float = 1.5, b: float = 0.75):
        self.docs, self.k1, self.b = docs, k1, b
        for d in docs:
            # The title counts twice, so a question naming an experiment finds its own passage first.
            d.tokens = Counter(tokenize(d.title) * 2 + tokenize(" ".join(d.blocks)))
            d.length = sum(d.tokens.values())
        self.avg_len = sum(d.length for d in docs) / max(1, len(docs))
        df = Counter(t for d in docs for t in d.tokens)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def score(self, query_tokens: list[str], d: Doc) -> float:
        s = 0.0
        for t in set(query_tokens):
            f = d.tokens.get(t, 0)
            if f:
                s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * d.length / self.avg_len))
        return s

    def search(self, query: str, k: int = TOP_K) -> list[tuple[Doc, float]]:
        q = tokenize(query)
        text = query.lower()
        scored = []
        for d in self.docs:
            if d.kind == "overview":
                continue
            s = self.score(q, d)
            if d.kind == "experiment":
                # A question that names the experiment exactly ("FLEX-2", not "FLEX") puts it first.
                name = d.title.split(":")[0].lower()
                if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text):
                    s += 10
            scored.append((d, s))
        scored = [(d, s) for d, s in scored if s > 0]
        scored.sort(key=lambda pair: -pair[1])
        return scored[:k]

    def overview(self) -> Doc | None:
        return next((d for d in self.docs if d.kind == "overview"), None)


# --- Answering with Gemini --------------------------------------------------------------------------------
def build_prompt(question: str, docs: list[Doc], earlier: list[tuple[str, str]] | None = None) -> str:
    """The user message: numbered passages, optional earlier Q&A (context for follow-ups), then the question."""
    passages = "\n\n".join(f"[{i}] {d.title}\nSource: {d.source}\n" + "\n".join(d.blocks)
                           for i, d in enumerate(docs, start=1))
    context = ""
    if earlier:
        context = "Earlier in this chat (context only, not a source):\n" + "\n".join(
            f"Q: {q}\nA: {a}" for q, a in earlier) + "\n\n"
    return f"Passages:\n\n{passages}\n\n{context}Question: {question}"


_CITE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def _best_quotes(doc: Doc, answer_text: str, limit: int = 2) -> list[str]:
    """The passage blocks that share the most words with the answer (shown under the source)."""
    words = set(tokenize(answer_text))
    return sorted(doc.blocks, key=lambda b: -len(words & set(tokenize(b))))[:limit]


def parse_answer(text: str, docs: list[Doc]) -> dict:
    """Renumber the model's [n] markers in order of first use and build the source list.
    Markers that point at no passage are dropped, so every number shown links to a real passage."""
    numbers: dict[int, int] = {}

    def renumber(match: re.Match) -> str:
        out = []
        for part in match.group(1).split(","):
            idx = int(part) - 1
            if 0 <= idx < len(docs):
                if idx not in numbers:
                    numbers[idx] = len(numbers) + 1
                out.append(f"[{numbers[idx]}]")
        return "".join(out)

    cleaned = _CITE.sub(renumber, text)
    cleaned = re.sub(r"[ \t]+([.,;:])", r"\1", cleaned).strip()
    sources = [{"n": n, "title": docs[idx].title, "source": docs[idx].source,
                "quotes": _best_quotes(docs[idx], cleaned)}
               for idx, n in sorted(numbers.items(), key=lambda pair: pair[1])]
    return {"text": cleaned, "sources": sources}


def answer(question: str, retriever: Retriever, api_key: str, model: str = MODEL,
           earlier: list[tuple[str, str]] | None = None, n_experiments: int = 24) -> dict:
    """Retrieve, ask Gemini, return {"text", "sources", "passages"}. Raises google.genai errors."""
    from google import genai
    from google.genai import types

    hits = [d for d, _ in retriever.search(question + (" " + earlier[-1][0] if earlier else ""))]
    overview = retriever.overview()
    docs = ([overview] if overview else []) + hits
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=build_prompt(question, docs, earlier),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT.replace("{n}", str(n_experiments)),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ),
    )
    text = response.text or ""
    result = parse_answer(text, docs) if text else {"text": "", "sources": []}
    finish = str(getattr(response.candidates[0], "finish_reason", "")) if response.candidates else ""
    if not text:
        result["text"] = "No answer came back (the question may have been blocked). Try rephrasing it."
    elif "MAX_TOKENS" in finish:
        result["text"] += "\n\n*(Answer cut short.)*"
    result["passages"] = docs
    return result


def friendly_error(exc: Exception) -> str | None:
    """A short message for a Gemini API error, or None if `exc` isn't one (so the caller re-raises)."""
    try:
        from google.genai import errors
    except ImportError:
        if isinstance(exc, ImportError):
            return "The `google-genai` package isn't installed, so AI answers are off."
        return None
    if isinstance(exc, errors.ClientError):
        if exc.code == 429:
            return ("The free Gemini quota is used up for now. Try again in a minute "
                    "(daily limits reset at midnight Pacific time).")
        if exc.code in (401, 403) or "API_KEY" in str(exc):
            return "The Gemini API key was rejected. Check GEMINI_API_KEY."
        if exc.code == 404:
            return "That Gemini model wasn't found. Check GEMINI_MODEL."
        return f"The request was rejected ({exc.code}): {exc.message}"
    if isinstance(exc, errors.ServerError):
        return "Gemini is unavailable right now. Try again shortly."
    if isinstance(exc, errors.APIError):
        return f"Gemini API error ({exc.code}): {exc.message}"
    return None


def load_dotenv(path=None) -> None:
    """Copy KEY=VALUE lines from the project's .env file into os.environ (variables already set win).
    For local runs only; on Streamlit Cloud the key goes in the app's Secrets instead."""
    path = path or data.ROOT / ".env"
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.removeprefix("export ").strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)
