"""Ready-made charts for the Astraeon app, built as Vega-Lite specs (no extra packages needed).

Draw one in a Streamlit page:

    import streamlit as st
    from astraeon.charts import moon_chart, MOON_CHART_ALT

    st.vega_lite_chart(moon_chart(), alt=MOON_CHART_ALT)
    st.vega_lite_chart(moon_chart(selected=(34, 8.2)), alt=MOON_CHART_ALT)   # with a box around 34% / 8.2 psi

Charts fill the page width by default (don't use the deprecated use_container_width).
If Streamlit's theme changes the colours, pass theme=None to st.vega_lite_chart.
"""
from __future__ import annotations

from .data import MOON_O2_MIN, MOON_PSI_MAX, load_atmospheres, load_investigations, load_moon_tests, short_name

ACCENT = "#2563eb"        # the one highlight colour: tests inside the Moon-base zone
MUTED = "#a8a29e"         # every other test
REFERENCE = "#6b7280"     # zone edges and labels
MARKER = "#ea580c"        # preset atmospheres and the selected atmosphere
O2_DOMAIN = [10, 46]
MOON_CHART_ALT = "Flight tests by chamber oxygen and pressure; only ACME CFI-G tests fall inside the Moon-base zone"


def moon_chart(max_psi: float = 50, height: int = 420, selected: tuple[float, float] | None = None,
               show_atmospheres: bool = True, o2_tol: float = 3.0, psi_tol: float = 1.5) -> dict:
    """Every flight test's chamber oxygen vs. pressure, with the Moon-base zone shaded.

    selected = (oxygen %, pressure psi) draws a box of +/- o2_tol and +/- psi_tol around that point,
    matching astraeon.data.tests_near(). show_atmospheres adds the presets from data/atmospheres.json.
    Data: data/moon_tests.csv (746 tests from 4 PSI investigations); tests above max_psi are counted
    in the subtitle instead of drawn.
    """
    names = {r["id"]: short_name(r["name"], r["source_link"]) for r in load_investigations()}
    tests = load_moon_tests()
    shown = [t for t in tests if t["pressure_psi"] <= max_psi]
    zone = [t for t in tests if t["in_zone"]]
    hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
    zone_names = sorted({names.get(t["id"], t["id"]) for t in zone})

    inside, other = "Test inside the Moon-base zone", "Other flight tests"
    if len(zone_names) == 1:
        title = f"Only {zone_names[0]} tests reached Moon-base conditions"
    elif zone_names:
        title = f"{len(zone_names)} experiments reached Moon-base conditions"
    else:
        title = "No test reached Moon-base conditions"
    subtitle = [f"{len(zone)} of {len(tests)} flight tests ran at {MOON_O2_MIN:g}% oxygen or more and "
                f"{MOON_PSI_MAX:g} psi or less; {hot} ignited a hot flame."]
    hidden = len(tests) - len(shown)
    if hidden:
        subtitle.append(f"{hidden} tests above {max_psi:g} psi are not shown.")

    x = {"type": "quantitative", "scale": {"domain": [0, max_psi]}}
    y = {"type": "quantitative", "scale": {"domain": O2_DOMAIN}}
    points = [{
        "experiment": names.get(t["id"], t["id"]), "test": t["test"], "fuel": t["fuel"],
        "oxygen": t["o2_percent"], "pressure": t["pressure_psi"],
        "outcome": t["outcome"] or "not recorded",
        "group": inside if t["in_zone"] else other, "draw_order": 1 if t["in_zone"] else 0,
    } for t in shown]

    layers = [
        {   # the Moon-base zone
            "data": {"values": [{"x": 0, "x2": MOON_PSI_MAX, "y": MOON_O2_MIN, "y2": O2_DOMAIN[1]}]},
            "mark": {"type": "rect", "color": MUTED, "opacity": 0.18},
            "encoding": {"x": {"field": "x", **x}, "x2": {"field": "x2"},
                         "y": {"field": "y", **y}, "y2": {"field": "y2"}},
        },
        {   # 10.2 psi edge
            "data": {"values": [{"p": MOON_PSI_MAX}]},
            "mark": {"type": "rule", "color": REFERENCE, "strokeDash": [4, 3]},
            "encoding": {"x": {"field": "p", **x}},
        },
        {   # 30% oxygen edge
            "data": {"values": [{"o": MOON_O2_MIN}]},
            "mark": {"type": "rule", "color": REFERENCE, "strokeDash": [4, 3]},
            "encoding": {"y": {"field": "o", **y}},
        },
        {   # one dot per flight test
            "data": {"values": points},
            "mark": {"type": "circle", "size": 45, "opacity": 0.8},
            "encoding": {
                "x": {"field": "pressure", **x, "title": "Chamber pressure (psi)"},
                "y": {"field": "oxygen", **y, "title": "Chamber oxygen at test start (%)"},
                "color": {"field": "group", "type": "nominal",
                          "scale": {"domain": [inside, other], "range": [ACCENT, MUTED]},
                          "legend": {"orient": "top", "title": None, "labelLimit": 300}},
                "order": {"field": "draw_order", "type": "quantitative"},
                "tooltip": [
                    {"field": "experiment", "title": "Experiment"},
                    {"field": "test", "title": "Test"},
                    {"field": "fuel", "title": "Fuel"},
                    {"field": "oxygen", "title": "Oxygen (%)"},
                    {"field": "pressure", "title": "Pressure (psi)"},
                    {"field": "outcome", "title": "Outcome"},
                ],
            },
        },
        {   # zone label
            "data": {"values": [{"x": 0.5, "y": O2_DOMAIN[1] - 0.8, "label": "Moon-base zone"}]},
            "mark": {"type": "text", "align": "left", "baseline": "top", "color": REFERENCE, "fontWeight": "bold"},
            "encoding": {"x": {"field": "x", **x}, "y": {"field": "y", **y}, "text": {"field": "label"}},
        },
    ]

    atmospheres = [a for a in load_atmospheres() if 0 <= a["pressure_psi"] <= max_psi] if show_atmospheres else []
    if atmospheres:
        layers.append({   # preset atmospheres from data/atmospheres.json
            "data": {"values": [{"atmosphere": a["name"], "oxygen": a["o2_percent"], "pressure": a["pressure_psi"],
                                 "source": a["source"]} for a in atmospheres]},
            "mark": {"type": "point", "filled": True, "size": 150, "color": MARKER, "stroke": "white",
                     "strokeWidth": 1, "opacity": 1},
            "encoding": {
                "x": {"field": "pressure", **x}, "y": {"field": "oxygen", **y},
                "shape": {"field": "atmosphere", "type": "nominal",
                          "scale": {"range": ["diamond", "square", "triangle-up", "cross", "triangle-down"]},
                          "legend": {"orient": "bottom", "title": "Atmospheres (hover for the source)",
                                     "columns": 2, "labelLimit": 340, "titleLimit": 400,
                                     "symbolFillColor": MARKER, "symbolStrokeColor": MARKER}},
                "tooltip": [{"field": "atmosphere", "title": "Atmosphere"},
                            {"field": "oxygen", "title": "Oxygen (%)"},
                            {"field": "pressure", "title": "Pressure (psi)"},
                            {"field": "source", "title": "Source"}],
            },
        })

    if selected is not None:
        o2, psi = selected
        box = {"x": max(0, psi - psi_tol), "x2": min(max_psi, psi + psi_tol),
               "y": max(O2_DOMAIN[0], o2 - o2_tol), "y2": min(O2_DOMAIN[1], o2 + o2_tol)}
        layers.append({   # the "near" box used by tests_near()
            "data": {"values": [box]},
            "mark": {"type": "rect", "fill": MARKER, "fillOpacity": 0.06, "stroke": MARKER, "strokeWidth": 2,
                     "strokeDash": [3, 2], "clip": True},
            "encoding": {"x": {"field": "x", **x}, "x2": {"field": "x2"},
                         "y": {"field": "y", **y}, "y2": {"field": "y2"}},
        })
        layers.append({   # the selected atmosphere
            "data": {"values": [{"oxygen": o2, "pressure": psi}]},
            "mark": {"type": "point", "shape": "circle", "filled": False, "size": 220, "stroke": MARKER,
                     "strokeWidth": 2.5, "clip": True},
            "encoding": {"x": {"field": "pressure", **x}, "y": {"field": "oxygen", **y},
                         "tooltip": [{"field": "oxygen", "title": "Selected oxygen (%)"},
                                     {"field": "pressure", "title": "Selected pressure (psi)"}]},
        })

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {"text": title, "subtitle": subtitle, "anchor": "start"},
        "width": "container",
        "height": height,
        # Streamlit's theme fits the WHOLE chart (title + legends + plot) into `height`, which squashes
        # the plot. fit-x fits only the width to the page and keeps `height` for the plot itself.
        "autosize": {"type": "fit-x", "contains": "padding"},
        "layer": layers,
    }
