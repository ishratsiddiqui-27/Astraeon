"""Look and feel from the Figma design: global CSS plus small HTML pieces (page headers, hero art, stat tiles,
timeline, footer).

.streamlit/config.toml sets the colours and fonts. This module adds what a theme can't: the starfield
background, glass cards, glow on hover, the orbiting Moon and gentle fade-ins.

Cards are keyed containers, styled through the `st-key-<key>` class Streamlit adds to them:
    with st.container(key="card_home_chart"):          # glass card
    with st.container(key="cardaccent_home_gap"):      # card with a violet-to-ember glow
    with st.container(key="carddashed_compare_add"):   # dashed placeholder card
If a selector ever stops matching after a Streamlit upgrade, the page falls back to the plain dark theme.
"""
from __future__ import annotations

import html
import random

import streamlit as st


def _stars(n: int, seed: int, size: float, alpha: float) -> str:
    rng = random.Random(seed)
    dots = [f"radial-gradient({size}px {size}px at {rng.uniform(0, 100):.1f}% {rng.uniform(0, 100):.1f}%, "
            f"rgba(255,255,255,{alpha}) 50%, transparent 51%)" for _ in range(n)]
    return ",\n    ".join(dots)


CSS = """
<style>
:root {
  --astra-bg: #0A0F1E; --astra-card: rgba(17, 26, 46, 0.72); --astra-border: #1E2A44;
  --astra-text: #E6E9F2; --astra-muted: #8B95AD; --astra-orange: #F97316; --astra-blue: #60A5FA;
  --astra-violet: #7C3AED; --astra-heading: "Space Grotesk", "Inter", sans-serif;
}

/* Deep-space background: two faint nebula glows, plus two star layers that twinkle out of step. */
.stApp {
  background:
    radial-gradient(1100px 560px at 88% -8%, rgba(124, 58, 237, 0.16), transparent 62%),
    radial-gradient(900px 520px at -12% 12%, rgba(49, 46, 129, 0.22), transparent 60%),
    var(--astra-bg);
  isolation: isolate;
}
.stApp::before, .stApp::after {
  content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
}
.stApp::before {
  background-image:
    %STARS_A%;
  animation: astra-twinkle 7s ease-in-out infinite alternate;
}
.stApp::after {
  background-image:
    %STARS_B%;
  animation: astra-twinkle 11s ease-in-out infinite alternate-reverse;
}
@keyframes astra-twinkle { from { opacity: 0.25; } to { opacity: 0.9; } }

/* Glass cards (keyed containers). */
div[class*="st-key-card_"], div[class*="st-key-cardaccent_"], div[class*="st-key-carddashed_"] {
  background: var(--astra-card);
  border: 1px solid var(--astra-border);
  border-radius: 14px;
  padding: 1.15rem 1.25rem 1.2rem;
  backdrop-filter: blur(6px);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
  animation: astra-rise 0.5s ease both;
}
div[class*="st-key-card_"]:hover, div[class*="st-key-cardaccent_"]:hover {
  border-color: rgba(249, 115, 22, 0.38);
  box-shadow: 0 10px 34px rgba(124, 58, 237, 0.16), 0 0 0 1px rgba(249, 115, 22, 0.10);
  transform: translateY(-2px);
}
div[class*="st-key-cardaccent_"] {
  background: linear-gradient(155deg, rgba(124, 58, 237, 0.20), rgba(17, 26, 46, 0.82) 48%, rgba(249, 115, 22, 0.08));
  border-color: rgba(124, 58, 237, 0.38);
}
div[class*="st-key-carddashed_"] { background: rgba(17, 26, 46, 0.35); border-style: dashed; }
@keyframes astra-rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* Call-to-action buttons (keyed: ctaprimary_*, ctasecondary_*). Dark text on orange passes WCAG AA. */
div[class*="st-key-ctaprimary_"] button {
  background: var(--astra-orange) !important; border: 1px solid var(--astra-orange) !important;
  transition: box-shadow 0.25s ease;
}
div[class*="st-key-ctaprimary_"] button, div[class*="st-key-ctaprimary_"] button * {
  color: #0B1020 !important; font-weight: 600 !important;
}
div[class*="st-key-ctaprimary_"] button:hover { box-shadow: 0 0 26px rgba(249, 115, 22, 0.45); }
div[class*="st-key-ctasecondary_"] button {
  background: rgba(17, 26, 46, 0.6) !important; border: 1px solid #2A3550 !important;
}
div[class*="st-key-ctasecondary_"] button:hover { border-color: var(--astra-blue) !important; }

/* Page header */
.astra-eyebrow {
  color: var(--astra-orange); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; margin: 0 0 0.55rem;
}
.astra-titlerow { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem 1rem; justify-content: space-between; }
.astra-h1 {
  font-family: var(--astra-heading); font-weight: 600; color: var(--astra-text);
  font-size: clamp(1.7rem, 2.6vw, 2.35rem); line-height: 1.15; letter-spacing: -0.01em; margin: 0; padding: 0;
}
.astra-hero-h1 { font-size: clamp(1.9rem, 2.9vw, 2.5rem); }
.astra-lede { color: var(--astra-muted); font-size: 0.98rem; line-height: 1.6; margin: 0.6rem 0 0; max-width: 44rem; }
.astra-pill {
  display: inline-flex; align-items: center; gap: 0.4rem; white-space: nowrap;
  border: 1px solid rgba(96, 165, 250, 0.35); background: rgba(96, 165, 250, 0.08); color: #BFDBFE;
  border-radius: 999px; padding: 0.3rem 0.8rem; font-size: 0.78rem;
}
.astra-pill::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--astra-blue); }
.astra-head { animation: astra-rise 0.55s ease both; margin-bottom: 0.4rem; }
.astra-small { color: var(--astra-muted); font-size: 0.78rem; margin-top: 0.2rem; }
.astra-h3 { font-family: var(--astra-heading); font-size: 1.35rem; font-weight: 600; line-height: 1.3; margin: 0.1rem 0 0.4rem; color: var(--astra-text); }

/* Stat tiles */
.astra-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; }
.astra-tile {
  background: var(--astra-card); border: 1px solid var(--astra-border); border-radius: 14px;
  padding: 1rem 1.15rem; animation: astra-rise 0.5s ease both;
}
.astra-tile b { display: block; font-family: var(--astra-heading); font-size: 1.9rem; font-weight: 600; color: var(--astra-blue); line-height: 1.1; }
.astra-tile span { display: block; color: var(--astra-muted); font-size: 0.82rem; margin-top: 0.35rem; }
.astra-tile:nth-child(2) { animation-delay: 0.06s; } .astra-tile:nth-child(3) { animation-delay: 0.12s; }
.astra-tile:nth-child(4) { animation-delay: 0.18s; }

/* Moon illustration */
.astra-moon { position: relative; display: flex; flex-direction: column; align-items: center; animation: astra-rise 0.7s ease both; }
.astra-moon svg { width: min(100%, 340px); height: auto; overflow: visible; filter: drop-shadow(0 0 46px rgba(124, 58, 237, 0.45)); }
.astra-orbit { transform-origin: 170px 170px; animation: astra-spin 26s linear infinite; }
.astra-float { transform-origin: 170px 170px; animation: astra-float 9s ease-in-out infinite; }
@keyframes astra-spin { to { transform: rotate(360deg); } }
@keyframes astra-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.astra-moon-caption { text-align: center; margin-top: 0.4rem; }
.astra-moon-caption .astra-eyebrow { color: var(--astra-muted); margin-bottom: 0.25rem; }
.astra-moon-caption p { color: var(--astra-muted); font-size: 0.82rem; margin: 0; line-height: 1.5; }

/* Timeline (Fire history) */
.astra-timeline { display: grid; grid-template-columns: repeat(var(--astra-cols, 3), 1fr); gap: 1rem; position: relative; margin: 0.6rem 0 0.2rem; }
.astra-timeline::before { content: ""; position: absolute; left: 0; right: 0; top: 2.35rem; height: 1px; background: linear-gradient(90deg, var(--astra-orange), rgba(124, 58, 237, 0.6), var(--astra-border)); }
.astra-timeline div { font-family: var(--astra-heading); font-size: 1.35rem; color: var(--astra-text); padding-bottom: 1.1rem; position: relative; }
.astra-timeline div::after { content: ""; position: absolute; left: 0.1rem; top: 2.1rem; width: 10px; height: 10px; border-radius: 50%; background: var(--astra-orange); box-shadow: 0 0 14px rgba(249, 115, 22, 0.7); }
@media (max-width: 640px) { .astra-timeline { display: none; } }

/* Note bar and footer */
.astra-note {
  display: flex; gap: 0.9rem; align-items: baseline; flex-wrap: wrap;
  background: rgba(17, 26, 46, 0.55); border: 1px solid var(--astra-border); border-radius: 12px;
  padding: 0.7rem 1rem; color: var(--astra-muted); font-size: 0.85rem;
}
.astra-note b { color: var(--astra-orange); font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 600; }
.astra-footer {
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
  border-top: 1px solid var(--astra-border); margin-top: 2rem; padding-top: 1rem;
  color: var(--astra-muted); font-size: 0.72rem; letter-spacing: 0.08em;
}
.astra-footer span:first-child { text-transform: uppercase; }

@media (prefers-reduced-motion: reduce) {
  .stApp::before, .stApp::after, .astra-orbit, .astra-float, .astra-tile, .astra-head, .astra-moon,
  div[class*="st-key-card_"], div[class*="st-key-cardaccent_"], div[class*="st-key-carddashed_"] {
    animation: none !important; transition: none !important;
  }
}
</style>
""".replace("%STARS_A%", _stars(70, 7, 1.2, 0.75)).replace("%STARS_B%", _stars(45, 21, 1.8, 0.55))

MOON_SVG = """
<svg viewBox="0 0 340 340" role="img" aria-label="Illustration of the Moon with an orbit ring">
  <defs>
    <radialGradient id="astraHalo" cx="50%" cy="50%" r="50%">
      <stop offset="45%" stop-color="#7C3AED" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="astraMoon" cx="38%" cy="34%" r="70%">
      <stop offset="0%" stop-color="#F1F2FA"/>
      <stop offset="55%" stop-color="#B9BED6"/>
      <stop offset="100%" stop-color="#5D6385"/>
    </radialGradient>
  </defs>
  <circle cx="170" cy="170" r="165" fill="url(#astraHalo)"/>
  <circle cx="170" cy="170" r="132" fill="none" stroke="#2A3550" stroke-width="1"/>
  <g class="astra-float">
    <circle cx="170" cy="170" r="70" fill="url(#astraMoon)"/>
    <circle cx="146" cy="150" r="11" fill="#8E93B3" opacity="0.55"/>
    <circle cx="190" cy="186" r="15" fill="#8E93B3" opacity="0.45"/>
    <circle cx="183" cy="139" r="6" fill="#8E93B3" opacity="0.5"/>
    <circle cx="150" cy="196" r="5" fill="#8E93B3" opacity="0.5"/>
  </g>
  <g class="astra-orbit">
    <circle cx="170" cy="170" r="104" fill="none" stroke="#7C3AED" stroke-opacity="0.55" stroke-width="1" stroke-dasharray="2 6"/>
    <circle cx="170" cy="66" r="5" fill="#F97316"/>
    <circle cx="170" cy="66" r="11" fill="#F97316" opacity="0.18"/>
  </g>
</svg>
"""


def _e(text) -> str:
    return html.escape(str(text))


def inject() -> None:
    """Add the global CSS. Call once per run, from app.py."""
    st.html(CSS)


def page_header(eyebrow: str, title: str, lede: str = "", pill: str | None = None, hero: bool = False) -> None:
    pill_html = f'<span class="astra-pill">{_e(pill)}</span>' if pill else ""
    lede_html = f'<p class="astra-lede">{_e(lede)}</p>' if lede else ""
    h1_class = "astra-h1 astra-hero-h1" if hero else "astra-h1"
    st.html(f'<div class="astra-head"><div class="astra-eyebrow">{_e(eyebrow)}</div>'
            f'<div class="astra-titlerow"><h1 class="{h1_class}">{_e(title)}</h1>{pill_html}</div>{lede_html}</div>')


def eyebrow(text: str) -> None:
    st.html(f'<div class="astra-eyebrow">{_e(text)}</div>')


def card_title(text: str, eyebrow_text: str | None = None) -> None:
    """Heading inside a card: optional orange eyebrow, then a Space Grotesk title."""
    top = f'<div class="astra-eyebrow">{_e(eyebrow_text)}</div>' if eyebrow_text else ""
    st.html(f'{top}<div class="astra-h3">{_e(text)}</div>')


def stat_tiles(items: list[tuple[object, str]]) -> None:
    tiles = "".join(f'<div class="astra-tile"><b>{_e(value)}</b><span>{_e(label)}</span></div>' for value, label in items)
    st.html(f'<div class="astra-tiles">{tiles}</div>')


def moon_art(caption_title: str, caption_text: str) -> None:
    st.html(f'<div class="astra-moon">{MOON_SVG}<div class="astra-moon-caption">'
            f'<div class="astra-eyebrow">{_e(caption_title)}</div><p>{_e(caption_text)}</p></div></div>')


def timeline(years: list[str]) -> None:
    cells = "".join(f"<div>{_e(y)}</div>" for y in years)
    st.html(f'<div class="astra-timeline" style="--astra-cols:{len(years)}" aria-hidden="true">{cells}</div>')


def note(label: str, text: str) -> None:
    st.html(f'<div class="astra-note"><b>{_e(label)}</b><span>{_e(text)}</span></div>')


def footer() -> None:
    st.html('<div class="astra-footer"><span>Astraeon / Fire science beyond Earth</span>'
            '<span>NASA PSI data · Evidence before extrapolation</span></div>')
