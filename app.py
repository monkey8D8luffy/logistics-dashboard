"""
Last-mile delivery operations dashboard, liquid-glass edition.
Enterprise-grade layout with balanced grid rows, professional logistics analytics,
and zero layout gaps.

Run locally: streamlit run app.py --server.port 8502
"""
from __future__ import annotations

import html
import inspect
import io
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Last-Mile Logistics Operations",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────── design tokens ─────────────────────────────
AMBER = "#ff9a1f"
GREEN = "#2fd06b"
RED = "#ff5d5d"
BLUE = "#3b82f6"
PURPLE = "#a855f7"
MIST = "#9ba3ae"
INK = "#090b0e"
FONT = "Manrope, system-ui, -apple-system, 'Segoe UI', sans-serif"
DATA_FILE = "Last mile Delivery Data.csv"
CAT_COLS = ["Weather", "Traffic", "Vehicle", "Area", "Category"]
NUM_COLS = ["Delivery_Time", "Agent_Age", "Agent_Rating"]
TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PLOT_CFG = {"displayModeBar": False, "responsive": True}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root{
  --ink:#090b0e;--tx:#f4f5f7;--mute:#9ba3ae;--amber:#ff9a1f;--green:#2fd06b;--red:#ff5d5d;--blue:#3b82f6;--purple:#a855f7;
}

html,body{background:var(--ink)}
.stApp{
  background:
    radial-gradient(45vw 38vh at 4% 0%, rgba(255,154,31,.28), transparent 70%),
    radial-gradient(40vw 40vh at 92% 3%, rgba(47,208,107,.24), transparent 70%),
    radial-gradient(35vw 35vh at 95% 55%, rgba(59,130,246,.18), transparent 70%),
    radial-gradient(42vw 38vh at 2% 98%, rgba(47,208,107,.20), transparent 70%),
    var(--ink);
  background-attachment:fixed;color:var(--tx);-webkit-font-smoothing:antialiased;
}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{background:transparent!important}
.stApp,.stApp p,.stApp label,.stApp li,.stApp input,.stApp button,.stApp textarea,.stApp table,
[data-baseweb],[data-testid="stMarkdownContainer"] *{font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif!important}
[data-testid="stIconMaterial"]{font-family:'Material Symbols Rounded'!important}
.block-container{max-width:1520px;padding:1.6rem 2rem 3rem!important}
footer,[data-testid="stDeployButton"],[data-testid="stStatusWidget"]{display:none!important}
[data-stale="true"]{opacity:1!important;transition:none!important}
::selection{background:rgba(255,154,31,.35)}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:9px}

/* Clean uniform card styling */
[class*="st-key-card_"]{
  padding:1.15rem 1.35rem!important;border-radius:18px!important;
  background:
    radial-gradient(130% 70% at 0% 0%, rgba(255,255,255,.10), transparent 55%),
    linear-gradient(150deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.025) 45%, rgba(255,255,255,.02) 65%, rgba(255,255,255,.06) 100%);
  border:1px solid rgba(255,255,255,.11)!important;border-top-color:rgba(255,255,255,.24)!important;border-left-color:rgba(255,255,255,.18)!important;
  -webkit-backdrop-filter:blur(24px) saturate(160%);backdrop-filter:blur(24px) saturate(160%);
  box-shadow:0 14px 36px -10px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.22);
  margin-bottom:0.75rem!important;
}

/* Sidebar styling */
[data-testid="stSidebar"]{background:rgba(10,12,16,.58)!important;-webkit-backdrop-filter:blur(28px);backdrop-filter:blur(28px);border-right:1px solid rgba(255,255,255,.08)}
[data-testid="stSidebar"]>div:first-child,[data-testid="stSidebarContent"]{background:transparent!important;padding:1.4rem 1.1rem!important}
.sb-brand{display:flex;align-items:center;gap:.6rem;font-weight:800;font-size:16px;color:#fff;letter-spacing:-.01em;padding-bottom:.6rem;border-bottom:1px solid rgba(255,255,255,.08)}
.sb-h{font-size:11.5px;font-weight:700;color:#9ba3ae;text-transform:uppercase;letter-spacing:.05em;margin:1rem 0 .4rem}

/* Widgets */
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{color:#cfd4db!important;font-size:12px!important;font-weight:600!important}
[data-baseweb="select"]>div{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:10px!important}
[data-baseweb="select"]>div:focus-within{border-color:rgba(255,154,31,.7)!important;box-shadow:0 0 0 3px rgba(255,154,31,.16)}
span[data-baseweb="tag"]{background-color:rgba(255,154,31,.16)!important;border:1px solid rgba(255,154,31,.35)!important;border-radius:6px!important}
span[data-baseweb="tag"] span{color:#ffd9a3!important;font-weight:600!important}
span[data-baseweb="tag"] span[data-baseweb="delete-icon"] svg{fill:#ffd9a3!important}
[data-baseweb="popover"]>div,[data-baseweb="menu"]{background:rgba(18,20,25,.95)!important;-webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.14);border-radius:12px!important}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 4px rgba(255,154,31,.25),0 0 18px rgba(255,154,31,.6)!important}
[data-testid="stSliderThumbValue"]{color:#ffd9a3!important;font-weight:700!important;font-size:11.5px!important}
.stButton>button,.stDownloadButton>button{width:100%;background:rgba(255,255,255,.06);color:#eef0f3;border:1px solid rgba(255,255,255,.14);border-radius:10px;font-weight:600;font-size:12.5px;padding:.38rem .75rem;transition:all .18s}
.stButton>button:hover,.stDownloadButton>button:hover{background:rgba(255,154,31,.18);border-color:rgba(255,154,31,.6);color:#fff;box-shadow:0 0 18px rgba(255,154,31,.25)}
[data-testid="stBaseButton-pills"],[data-testid="stBaseButton-segmented_control"]{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.12)!important;color:#cfd4db!important;border-radius:999px!important;font-weight:600!important;font-size:12px!important;padding:.2rem .65rem!important}
[data-testid="stBaseButton-pillsActive"],[data-testid="stBaseButton-segmented_controlActive"]{background:rgba(255,154,31,.2)!important;border:1px solid rgba(255,154,31,.7)!important;color:#ffd9a3!important;border-radius:999px!important;font-weight:700!important;box-shadow:0 0 16px rgba(255,154,31,.22)}

/* ==================== APPLE LIQUID GLASS TAB BAR ==================== */
/* Remove default lines on tab wrappers and lists */
div[data-testid="stTabs"],
div[data-testid="stTabs"] > div,
div[data-testid="stTabs"] > div:first-child,
.e78jmjr2,
.e78jmjr0 {
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* Floating liquid glass pill dock - ONLY applied to div[role="tablist"] */
div[role="tablist"], div.e78jmjr3 {
  display: inline-flex !important;
  align-items: center !important;
  gap: 3px !important;
  padding: 5px 6px !important;
  border-radius: 9999px !important;
  background: 
    radial-gradient(120% 80% at 50% 0%, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.03) 100%),
    rgba(14, 17, 23, 0.65) !important;
  -webkit-backdrop-filter: blur(36px) saturate(200%) contrast(110%) !important;
  backdrop-filter: blur(36px) saturate(200%) contrast(110%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.35) !important;
  border-left: 1px solid rgba(255, 255, 255, 0.22) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
  box-shadow: 
    0 16px 45px -8px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.35),
    inset 0 -1px 0 rgba(0, 0, 0, 0.3),
    inset 0 0 20px rgba(255, 255, 255, 0.02) !important;
  margin: 0.6rem 0 1.35rem 0 !important;
  width: fit-content !important;
  max-width: 100% !important;
  position: relative !important;
  overflow: visible !important;
}

/* Individual tab buttons */
div[data-testid="stTab"], div[role="tab"] {
  position: relative !important;
  z-index: 2 !important;
  border-radius: 9999px !important;
  padding: 7px 16px !important;
  color: #9ba3ae !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  letter-spacing: -0.01em !important;
  white-space: nowrap !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  cursor: pointer !important;
  transition: color 0.25s ease, transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  user-select: none !important;
  outline: none !important;
}

div[data-testid="stTab"]:hover, div[role="tab"]:hover {
  color: #ffffff !important;
}

div[data-testid="stTab"]:active, div[role="tab"]:active {
  transform: scale(0.96) !important;
}

/* Selected Tab state typography */
div[data-testid="stTab"][aria-selected="true"], div[role="tab"][aria-selected="true"] {
  color: #ffffff !important;
  font-weight: 700 !important;
  text-shadow: 0 0 14px rgba(255, 170, 50, 0.6) !important;
}

div[data-testid="stTab"] p, div[role="tab"] p {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 13.5px !important;
  letter-spacing: -0.01em !important;
}

/* Completely remove React-Aria default red underline indicator */
.react-aria-SelectionIndicator,
div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
}

/* The Animated Liquid Morph Pill (Apple spring physics & visionOS optics) */
.apple-liquid-pill {
  position: absolute !important;
  z-index: 1 !important;
  pointer-events: none !important;
  border-radius: 9999px !important;
  background: 
    radial-gradient(120% 90% at 50% -15%, rgba(255, 185, 75, 0.45) 0%, rgba(255, 140, 20, 0.22) 65%, rgba(255, 100, 0, 0.12) 100%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(200%) !important;
  backdrop-filter: blur(24px) saturate(200%) !important;
  border: 1px solid rgba(255, 180, 70, 0.75) !important;
  border-top: 1px solid rgba(255, 245, 215, 0.95) !important;
  border-bottom: 1px solid rgba(255, 130, 20, 0.45) !important;
  box-shadow:
    0 8px 28px -2px rgba(255, 140, 20, 0.5),
    0 2px 10px rgba(0, 0, 0, 0.4),
    inset 0 1px 2px rgba(255, 255, 255, 0.9),
    inset 0 -1px 2px rgba(0, 0, 0, 0.45),
    inset 0 0 16px rgba(255, 160, 40, 0.3) !important;
  opacity: 0;
  transition: 
    left 0.44s cubic-bezier(0.34, 1.35, 0.64, 1),
    top 0.44s cubic-bezier(0.34, 1.35, 0.64, 1),
    width 0.38s cubic-bezier(0.34, 1.35, 0.64, 1),
    height 0.38s cubic-bezier(0.34, 1.35, 0.64, 1),
    opacity 0.25s ease,
    transform 0.2s cubic-bezier(0.34, 1.4, 0.64, 1) !important;
  filter: drop-shadow(0 0 12px rgba(255, 154, 31, 0.4)) !important;
}

/* Fallback liquid glass pill style when JS pill is aligning or loading */
div[role="tablist"]:not([data-pill-active="true"]) div[data-testid="stTab"][aria-selected="true"],
div[role="tablist"]:not([data-pill-active="true"]) div[role="tab"][aria-selected="true"] {
  background: radial-gradient(110% 80% at 50% -10%, rgba(255, 180, 60, 0.35) 0%, rgba(255, 135, 20, 0.15) 100%) !important;
  border: 1px solid rgba(255, 180, 80, 0.65) !important;
  border-top: 1px solid rgba(255, 245, 215, 0.9) !important;
  box-shadow: 0 6px 22px rgba(255, 140, 20, 0.38), inset 0 1px 1.5px rgba(255, 255, 255, 0.8) !important;
}

/* Hide fallback tab border when liquid pill is actively gliding */
div[role="tablist"][data-pill-active="true"] div[data-testid="stTab"][aria-selected="true"],
div[role="tablist"][data-pill-active="true"] div[role="tab"][aria-selected="true"] {
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
}

/* Zero space for injection helper iframe */
iframe[title="streamlit.components.v1.html"],
.element-container:has(> iframe[height="0"]),
div[data-testid="stCustomComponentV1"]:has(> iframe[height="0"]) {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Header & Typography */
.top-header{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin:0 0 .9rem}
.brand-group{display:flex;align-items:center;gap:.85rem}
.brand-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(145deg,rgba(255,154,31,.35),rgba(255,154,31,.08));border:1px solid rgba(255,154,31,.5);box-shadow:0 0 24px rgba(255,154,31,.25)}
.brand-title{font-size:24px;font-weight:800;letter-spacing:-.025em;line-height:1.15;color:#fff}
.brand-sub{font-size:12.5px;color:var(--mute);font-weight:500;margin-top:.15rem}
.badge-count{padding:.4rem .85rem;border-radius:999px;font-size:12.5px;font-weight:600;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14)}
.badge-count b{color:#ffd9a3}

/* Card titles */
.c-head{display:flex;align-items:baseline;justify-content:space-between;gap:.75rem;margin-bottom:.55rem}
.c-head b{font-size:14.5px;font-weight:700;color:#fff;letter-spacing:-.005em}
.c-head span{font-size:11.5px;color:var(--mute);font-weight:500}

/* Executive KPI Strip */
.kpi-row{display:grid;grid-template-columns:repeat(5, 1fr);gap:.75rem;margin-bottom:.9rem}
@media (max-width:1100px){.kpi-row{grid-template-columns:repeat(3, 1fr)}}
@media (max-width:700px){.kpi-row{grid-template-columns:1fr}}
.kpi-card{
  padding:.95rem 1.15rem;border-radius:16px;position:relative;overflow:hidden;
  background:
    radial-gradient(100% 60% at 0% 0%, rgba(255,255,255,.08), transparent 50%),
    linear-gradient(150deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.02) 100%);
  border:1px solid rgba(255,255,255,.1);border-top-color:rgba(255,255,255,.22);
  -webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);
  box-shadow:0 8px 24px -6px rgba(0,0,0,.5);
}
.kpi-label{font-size:11.5px;font-weight:600;color:#9ba3ae;text-transform:uppercase;letter-spacing:.03em}
.kpi-val{font-size:26px;font-weight:800;letter-spacing:-.02em;color:#fff;margin:.25rem 0 .15rem;line-height:1.15;font-variant-numeric:tabular-nums}
.kpi-sub{font-size:11.5px;color:#cfd4db;display:flex;align-items:center;gap:.35rem}
.kpi-badge{font-size:11px;font-weight:700;padding:.1rem .45rem;border-radius:99px}
.kpi-badge.grn{background:rgba(47,208,107,.16);color:#8ff0b3;border:1px solid rgba(47,208,107,.4)}
.kpi-badge.amb{background:rgba(255,154,31,.16);color:#ffd9a3;border:1px solid rgba(255,154,31,.4)}
.kpi-badge.red{background:rgba(255,93,93,.16);color:#ffa3a3;border:1px solid rgba(255,93,93,.4)}

/* Control Deck Box */
.deck-title{font-size:13px;font-weight:700;color:#ffd9a3;margin-bottom:.25rem}
.deck-note{font-size:11.5px;color:var(--mute);margin-top:.25rem;line-height:1.4}
.impact-box{padding:.65rem .85rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:12px;height:100%;display:flex;flex-direction:column;justify-content:center}
.impact-main{font-size:24px;font-weight:800;color:#fff;line-height:1.15}
.impact-main span{color:var(--green);margin-left:.35rem}
.impact-note{font-size:12px;color:#cfd4db;margin-top:.2rem}

/* Table and ranking */
.tbl-wrap{overflow-x:auto;max-height:290px}
.tbl{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
.tbl th{font-weight:600;color:var(--mute);text-align:left;padding:.5rem .65rem;border-bottom:1px solid rgba(255,255,255,.14);font-size:11.5px;white-space:nowrap;position:sticky;top:0;background:rgba(18,20,25,.95)}
.tbl td{padding:.55rem .65rem;border-bottom:1px solid rgba(255,255,255,.06);white-space:nowrap}
.tbl tr:last-child td{border-bottom:0}
.tbl tr:hover td{background:rgba(255,255,255,.03)}
.chip{display:inline-block;padding:.12rem .5rem;border-radius:99px;font-size:11px;font-weight:700}
.chip.late{background:rgba(255,93,93,.16);color:#ffa3a3;border:1px solid rgba(255,93,93,.4)}
.chip.ok{background:rgba(47,208,107,.16);color:#8ff0b3;border:1px solid rgba(47,208,107,.4)}

.rk{display:grid;grid-template-columns:1.3rem minmax(0,1.2fr) minmax(0,1fr) 3.8rem;align-items:center;gap:.6rem;padding:.42rem 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:12.5px}
.rk:last-child{border-bottom:0}
.rk .no{color:var(--mute);font-weight:600}
.rk .nm{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rk .bar{height:6px;border-radius:9px;background:rgba(255,255,255,.08);overflow:hidden}
.rk .bar b{display:block;height:100%;border-radius:9px}
.rk .val{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}

.ramp{display:flex;align-items:center;gap:.6rem;font-size:12px;color:#cfd4db;margin-bottom:.5rem}
.ramp i{display:block;width:110px;height:7px;border-radius:9px;background:linear-gradient(90deg,#2fd06b,#ff9a1f,#ff5d5d)}
.empty-box{padding:2.5rem 1rem;text-align:center}
.empty-box b{display:block;font-size:18px;font-weight:800;color:#fff;margin-bottom:.35rem}
.empty-box span{color:var(--mute);font-size:13px}
</style>
"""

# ───────────────────────────── helper utilities ─────────────────────────────
def md(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)

def H(s: str) -> str:
    return re.sub(r"\n\s*", "", s.strip())

def e(x) -> str:
    return html.escape(str(x))

_PLOT_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters
_DECK_HEIGHT = "height" in inspect.signature(st.pydeck_chart).parameters
fragment = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None) or (lambda f: f)

def show(fig, key: str) -> None:
    kw = {"width": "stretch"} if _PLOT_WIDTH else {"use_container_width": True}
    st.plotly_chart(fig, theme=None, config=PLOT_CFG, key=key, **kw)

def card_header(title: str, sub: str = "") -> str:
    sub_span = f"<span>{e(sub)}</span>" if sub else ""
    return f'<div class="c-head"><b>{e(title)}</b>{sub_span}</div>'

def base(fig, h: int, top: int = 12, **layout):
    cfg = dict(
        height=h,
        margin=dict(l=6, r=6, t=top, b=6),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color="#c9ced6", size=11.5),
        hoverlabel=dict(
            bgcolor="rgba(16,18,22,.94)",
            bordercolor="rgba(255,255,255,.2)",
            font=dict(family=FONT, color="#fff", size=11.5),
        ),
    )
    cfg.update(layout)
    fig.update_layout(**cfg)
    fig.update_xaxes(
        zeroline=False,
        showgrid=False,
        linecolor="rgba(255,255,255,.12)",
        ticks="",
        tickfont=dict(color="#9ba3ae", size=11),
        automargin=True,
    )
    fig.update_yaxes(
        zeroline=False,
        gridcolor="rgba(255,255,255,.06)",
        linecolor="rgba(0,0,0,0)",
        ticks="",
        tickfont=dict(color="#9ba3ae", size=11),
        automargin=True,
    )
    return fig

def target_line(fig, sla: float, axis: str = "y", label: str = "") -> None:
    line = dict(color="rgba(255,255,255,.7)", width=1.3, dash="dot")
    if axis == "y":
        fig.add_hline(y=sla, line=line)
    else:
        fig.add_vline(x=sla, line=line)
    if label:
        if axis == "x":
            fig.add_annotation(
                x=sla, y=1, yref="paper", yanchor="bottom", showarrow=False,
                text=label, font=dict(color="#ffffff", size=11)
            )

# ───────────────────────────── data loading & enrichment ─────────────────────────────
def _clean(raw: str) -> pd.DataFrame:
    start = raw.find("Order")
    df = pd.read_csv(io.StringIO(raw[max(start, 0):]))
    df.columns = [c.replace("\\", "").replace('"', "").strip() for c in df.columns]
    missing = [c for c in CAT_COLS + NUM_COLS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    
    df = df.dropna(subset=NUM_COLS).reset_index(drop=True)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=NUM_COLS).reset_index(drop=True)

    for c in CAT_COLS:
        df[c] = df[c].astype(str).str.replace("\\", "", regex=False).str.strip().str.title()
    df["Area"] = df["Area"].replace({"Metropolitian": "Metropolitan"})

    # Hour feature
    if "Order_Time" in df.columns:
        secs = pd.to_timedelta(df["Order_Time"].astype(str).str.strip(), errors="coerce").dt.total_seconds()
        hour = (secs // 3600).where(lambda s: s.between(0, 23))
        df["Hour"] = hour

    # Order-to-pickup prep delay
    if "Pickup_Time" in df.columns and "Order_Time" in df.columns:
        ot = pd.to_timedelta(df["Order_Time"].astype(str).str.strip(), errors="coerce").dt.total_seconds() / 60
        pt = pd.to_timedelta(df["Pickup_Time"].astype(str).str.strip(), errors="coerce").dt.total_seconds() / 60
        prep = (pt - ot) % 1440
        df["Prep_Delay"] = prep.clip(0, 60)

    # Day of week feature
    if "Order_Date" in df.columns:
        dates = pd.to_datetime(df["Order_Date"], errors="coerce")
        df["Day_Name"] = dates.dt.day_name()

    # Geodesic / Haversine distance
    geo_cols = ["Store_Latitude", "Store_Longitude", "Drop_Latitude", "Drop_Longitude"]
    if all(c in df.columns for c in geo_cols):
        lat1 = np.radians(pd.to_numeric(df["Store_Latitude"], errors="coerce"))
        lon1 = np.radians(pd.to_numeric(df["Store_Longitude"], errors="coerce"))
        lat2 = np.radians(pd.to_numeric(df["Drop_Latitude"], errors="coerce"))
        lon2 = np.radians(pd.to_numeric(df["Drop_Longitude"], errors="coerce"))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        dist_km = 6371 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
        df["Distance_km"] = dist_km.round(1)
        tier_bins = [0, 5, 10, 15, 20, 100000]
        tier_labels = ["0-5 km", "5-10 km", "10-15 km", "15-20 km", "20+ km"]
        df["Distance_Tier"] = pd.cut(df["Distance_km"], bins=tier_bins, labels=tier_labels)

    return df

@st.cache_data(show_spinner="Processing delivery records...")
def load_csv(path: str, mtime: float) -> pd.DataFrame:
    return _clean(Path(path).read_bytes().decode("utf-8", errors="ignore"))

@st.cache_data(show_spinner="Processing uploaded delivery file...")
def clean_upload(raw: str) -> pd.DataFrame:
    return _clean(raw)

def find_csv() -> Path | None:
    for base_p in (Path(__file__).resolve().parent, Path.cwd()):
        p = base_p / DATA_FILE
        if p.exists():
            return p
    return None

# ───────────────────────────── chart builders ─────────────────────────────
def fig_delivery_distribution(t: np.ndarray, scn: np.ndarray, sla: float, tmin: int, tmax: int, show_scn: bool):
    edges = np.linspace(tmin, tmax, 45)
    mid = (edges[:-1] + edges[1:]) / 2
    cnt = np.histogram(t, edges)[0]
    k = int((mid <= sla).sum())
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=mid[:k], y=cnt[:k], mode="lines", name="On time", fill="tozeroy", fillcolor="rgba(47,208,107,.22)",
        line=dict(color=GREEN, width=2.5, shape="spline", smoothing=1.0),
        hovertemplate="%{x:.0f} min: %{y:,} on-time<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=mid[max(k - 1, 0):], y=cnt[max(k - 1, 0):], mode="lines", name="Late", fill="tozeroy", fillcolor="rgba(255,154,31,.26)",
        line=dict(color=AMBER, width=2.5, shape="spline", smoothing=1.0),
        hovertemplate="%{x:.0f} min: %{y:,} late<extra></extra>"
    ))
    if show_scn:
        fig.add_trace(go.Scatter(
            x=mid, y=np.histogram(scn, edges)[0], mode="lines", name="What-if Speedup",
            line=dict(color="#ffffff", width=2, dash="dash", shape="spline", smoothing=1.0),
            hovertemplate="%{x:.0f} min: %{y:,} modeled<extra></extra>"
        ))
    target_line(fig, sla, "x", f"Target {sla:.0f}m")
    base(fig, 280, top=24)
    fig.update_xaxes(range=[tmin, tmax], ticksuffix="m")
    return fig

def fig_hourly_profile(df: pd.DataFrame, sla: float):
    h_df = df.dropna(subset=["Hour"]).groupby("Hour", observed=True).agg(
        avg_time=("Delivery_Time", "mean"),
        orders=("Delivery_Time", "count")
    ).reset_index()
    if h_df.empty:
        return go.Figure()
    
    fig = go.Figure()
    # Bar for volume on primary y
    fig.add_trace(go.Bar(
        x=h_df["Hour"], y=h_df["orders"], name="Shipment Volume",
        marker=dict(color="rgba(255,255,255,.14)", line=dict(color="rgba(255,255,255,.25)", width=1)),
        yaxis="y", hovertemplate="%{x:02d}:00<br>Orders: %{y:,}<extra></extra>"
    ))
    # Line for average time on secondary y
    fig.add_trace(go.Scatter(
        x=h_df["Hour"], y=h_df["avg_time"], name="Avg Duration",
        mode="lines+markers", line=dict(color=AMBER, width=2.5, shape="spline"),
        marker=dict(size=6, color=AMBER, line=dict(color="#fff", width=1.2)),
        yaxis="y2", hovertemplate="%{x:02d}:00<br>Avg time: %{y:.1f} min<extra></extra>"
    ))
    
    base(fig, 280, top=20, showlegend=True,
         legend=dict(orientation="h", x=0, y=1.14, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#cfd4db")))
    fig.update_layout(
        yaxis=dict(title=dict(text="Orders", font=dict(size=11, color=MIST)), side="left", showgrid=False),
        yaxis2=dict(title=dict(text="Avg (min)", font=dict(size=11, color=AMBER)), overlaying="y", side="right",
                    showgrid=False, tickfont=dict(color=AMBER, size=11)),
    )
    fig.update_xaxes(tickmode="array", tickvals=list(range(0, 24, 3)), ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)])
    return fig

def fig_day_performance(df: pd.DataFrame, sla: float):
    if "Day_Name" not in df.columns:
        return go.Figure()
    day_df = df.dropna(subset=["Day_Name"]).groupby("Day_Name", observed=True).agg(
        avg_time=("Delivery_Time", "mean"),
        count=("Delivery_Time", "count"),
        late_pct=("Delivery_Time", lambda s: 100 * (s > sla).mean())
    ).reindex(DAY_ORDER).reset_index()
    
    fig = go.Figure()
    colors = [RED if t > sla else (AMBER if t > 125 else GREEN) for t in day_df["avg_time"]]
    fig.add_trace(go.Bar(
        x=[d[:3] for d in day_df["Day_Name"]], y=day_df["avg_time"],
        marker=dict(color=colors, opacity=0.88, line=dict(color="rgba(255,255,255,.3)", width=1)),
        hovertemplate="%{x}<br>Avg Time: %{y:.1f} min<br>Volume: %{customdata[0]:,}<br>Late Rate: %{customdata[1]:.1f}%<extra></extra>",
        customdata=np.stack([day_df["count"], day_df["late_pct"]], axis=1)
    ))
    target_line(fig, sla, "y")
    base(fig, 280, top=16)
    fig.update_yaxes(ticksuffix="m")
    return fig

def fig_vehicle_comparison(df: pd.DataFrame, sla: float):
    v_df = df.groupby("Vehicle", observed=True).agg(
        avg_time=("Delivery_Time", "mean"),
        count=("Delivery_Time", "count"),
        on_time=("Delivery_Time", lambda s: 100 * (s <= sla).mean())
    ).sort_values("avg_time").reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=v_df["Vehicle"], y=v_df["avg_time"],
        marker=dict(color=BLUE, opacity=0.85, line=dict(color="rgba(255,255,255,.35)", width=1)),
        hovertemplate="%{x}<br>Avg: %{y:.1f} min<br>On-Time: %{customdata[0]:.1f}%<br>Deliveries: %{customdata[1]:,}<extra></extra>",
        customdata=np.stack([v_df["on_time"], v_df["count"]], axis=1)
    ))
    target_line(fig, sla, "y")
    base(fig, 280, top=16)
    fig.update_yaxes(ticksuffix="m")
    return fig

def fig_weather_traffic(df: pd.DataFrame, sla: float, metric: str):
    g = df.groupby(["Weather", "Traffic"], observed=True).agg(
        avg_time=("Delivery_Time", "mean"),
        late_pct=("Delivery_Time", lambda s: 100 * (s > sla).mean()),
        count=("Delivery_Time", "count")
    ).reset_index()

    y_col = "avg_time" if metric == "Average time" else "late_pct"
    colors = {"Low": GREEN, "Medium": AMBER, "High": RED, "Jam": PURPLE}

    fig = go.Figure()
    for trf in TRAFFIC_ORDER:
        sub = g[g["Traffic"] == trf]
        if sub.empty:
            continue
        fig.add_trace(go.Bar(
            x=sub["Weather"], y=sub[y_col], name=trf,
            marker=dict(color=colors.get(trf, MIST), opacity=0.9),
            hovertemplate=f"{trf} Traffic<br>%{{x}}: %{{y:.1f}}{' min' if metric == 'Average time' else '%'}<extra></extra>"
        ))
    fig.update_layout(barmode="group")
    base(fig, 280, top=18, showlegend=True,
         legend=dict(orientation="h", y=1.16, x=0, bgcolor="rgba(0,0,0,0)", font=dict(color="#cfd4db", size=11)))
    fig.update_yaxes(ticksuffix="m" if metric == "Average time" else "%")
    return fig

def fig_regional_heatmap(df: pd.DataFrame, sla: float, tmin: int, tmax: int):
    areas = sorted(df["Area"].unique())
    edges = np.linspace(tmin, tmax, 13)
    mid = (edges[:-1] + edges[1:]) / 2
    counts = np.array([np.histogram(df.loc[df["Area"] == a, "Delivery_Time"], bins=edges)[0] for a in areas])
    share = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1) * 100
    
    hover = [[f"{a}: {edges[j]:.0f} to {edges[j + 1]:.0f} min<br>{share[i, j]:.1f}% of deliveries ({counts[i, j]:,} orders)"
              for i, a in enumerate(areas)] for j in range(len(mid))]
    heat_scale = [[0, "#16191f"], [0.4, "#6b3b12"], [1, AMBER]]
    fig = go.Figure(go.Heatmap(z=share.T, x=areas, y=mid, hovertext=hover, hovertemplate="%{hovertext}<extra></extra>",
                               colorscale=heat_scale, showscale=False, xgap=2, ygap=2))
    target_line(fig, sla, "y")
    base(fig, 280, top=14)
    fig.update_yaxes(showgrid=False, ticksuffix="m")
    return fig

def fig_distance_tiers(df: pd.DataFrame, sla: float):
    if "Distance_Tier" not in df.columns:
        return go.Figure()
    dist_df = df.dropna(subset=["Distance_Tier"]).groupby("Distance_Tier", observed=False).agg(
        avg_time=("Delivery_Time", "mean"),
        count=("Delivery_Time", "count"),
        late_pct=("Delivery_Time", lambda s: 100 * (s > sla).mean())
    ).reset_index()

    colors = [GREEN if l < 10 else (AMBER if l < 25 else RED) for l in dist_df["late_pct"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dist_df["Distance_Tier"].astype(str), y=dist_df["late_pct"],
        marker=dict(color=colors, opacity=0.88, line=dict(color="rgba(255,255,255,.3)", width=1)),
        hovertemplate="%{x}<br>Late Rate: %{y:.1f}%<br>Avg Duration: %{customdata[0]:.1f} min<br>Volume: %{customdata[1]:,} orders<extra></extra>",
        customdata=np.stack([dist_df["avg_time"], dist_df["count"]], axis=1)
    ))
    fig.add_hline(y=15, line=dict(color="rgba(255,255,255,.6)", width=1.2, dash="dash"))
    base(fig, 280, top=16)
    fig.update_yaxes(ticksuffix="%")
    return fig

def fig_category_box(df: pd.DataFrame, sla: float):
    rows = []
    for cat, g in df.groupby("Category", observed=True)["Delivery_Time"]:
        q1, med, q3 = g.quantile([0.25, 0.5, 0.75]).to_numpy()
        iqr = q3 - q1
        rows.append(dict(cat=cat, q1=q1, med=med, q3=q3, n=len(g), mean=g.mean(),
                         lo=g[g >= q1 - 1.5 * iqr].min(), hi=g[g <= q3 + 1.5 * iqr].max()))
    bx = pd.DataFrame(rows).sort_values("med").reset_index(drop=True)
    cats = list(bx["cat"])
    over = (bx["med"] > sla).to_numpy()
    whisk_x, whisk_y = [], []
    for r in bx.itertuples():
        whisk_x += [r.lo, r.hi, None]
        whisk_y += [r.cat, r.cat, None]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=whisk_x, y=whisk_y, mode="lines", hoverinfo="skip",
                             line=dict(color="rgba(255,255,255,.35)", width=1.2)))
    custom = np.stack([bx["lo"], bx["q1"], bx["med"], bx["q3"], bx["hi"], bx["n"]], axis=1)
    fig.add_trace(go.Bar(
        y=cats, x=(bx["q3"] - bx["q1"]).to_numpy(), base=bx["q1"].to_numpy(), orientation="h", width=0.52,
        marker=dict(color=[RED if o else GREEN for o in over], opacity=0.85,
                    line=dict(color="rgba(255,255,255,.3)", width=1)),
        customdata=custom,
        hovertemplate="%{y}<br>Typical range %{customdata[1]:.0f} to %{customdata[3]:.0f} min<br>"
                      "Median: %{customdata[2]:.0f} min<br>Sample: %{customdata[5]:,} deliveries<extra></extra>"
    ))
    fig.add_trace(go.Scatter(x=bx["med"], y=cats, mode="markers", hoverinfo="skip",
                             marker=dict(symbol="line-ns", size=14, color="#ffffff", line=dict(color="#ffffff", width=2.5))))
    target_line(fig, sla, "x")
    base(fig, 280, top=14)
    fig.update_yaxes(categoryorder="array", categoryarray=cats, showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,.06)", ticksuffix="m")
    return fig

def fig_agent_scatter(df: pd.DataFrame, sla: float):
    s = df.sample(min(1400, len(df)), random_state=7)[["Agent_Rating", "Delivery_Time", "Agent_Age"]].copy()
    s["group"] = pd.cut(s["Agent_Age"], bins=[0, 25, 40, 200], labels=["Up to 25", "26 to 40", "Over 40"])

    fig = go.Figure()
    for name, color in zip(["Up to 25", "26 to 40", "Over 40"], [AMBER, GREEN, MIST]):
        d = s[s["group"] == name]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d["Agent_Rating"], y=d["Delivery_Time"], mode="markers", name=name,
            marker=dict(size=5, color=color, opacity=0.6, line=dict(width=0)),
            hovertemplate="Rating %{x:.1f} ★<br>Delivery: %{y:.0f} min<extra>" + name + "</extra>"
        ))
    target_line(fig, sla, "y")
    base(fig, 280, top=26, showlegend=True,
         legend=dict(orientation="h", x=0, y=1.14, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#cfd4db")))
    fig.update_xaxes(title=dict(text="Agent Rating", font=dict(size=11, color=MIST)))
    fig.update_yaxes(ticksuffix="m")
    return fig

def rank_categories_html(df: pd.DataFrame, sla: float) -> str:
    cat_avg = df.groupby("Category", observed=True)["Delivery_Time"].mean().reset_index(name="avg").sort_values("avg", ascending=False).head(8)
    top = max(float(cat_avg["avg"].max()), 1.0)
    rows = "".join(
        f'<div class="rk"><span class="no">{i}</span><span class="nm">{e(r.Category)}</span>'
        f'<span class="bar"><b style="width:{r.avg / top * 100:.0f}%;background:{RED if r.avg > sla else AMBER}"></b></span>'
        f'<span class="val">{r.avg:.0f} min</span></div>'
        for i, r in enumerate(cat_avg.itertuples(), 1)
    )
    return f'<div>{rows}</div>'

def slowest_orders_html(df: pd.DataFrame, sla: float) -> str:
    cols = [c for c in ["Order_ID", "Area", "Vehicle", "Weather", "Traffic", "Agent_Rating", "Delivery_Time"] if c in df.columns]
    slow = df.nlargest(8, "Delivery_Time")[cols]
    head = "".join(f"<th>{e(c.replace('_', ' '))}</th>" for c in cols) + "<th>Status</th>"
    body = ""
    for r in slow.to_dict("records"):
        cells = ""
        for c, v in r.items():
            if c == "Delivery_Time":
                v = f"{v:.0f} min"
            elif c == "Agent_Rating":
                v = f"{v:.1f} ★"
            cells += f"<td>{e(v)}</td>"
        over = r["Delivery_Time"] - sla
        chip = f'<span class="chip late">+{over:.0f}m Late</span>' if over > 0 else '<span class="chip ok">On-Time</span>'
        body += f"<tr>{cells}<td>{chip}</td></tr>"
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def prepare_map(df: pd.DataFrame):
    need = ["Store_Latitude", "Store_Longitude", "Drop_Latitude", "Drop_Longitude"]
    if not all(c in df.columns for c in need):
        return None
    m = df[need + ["Delivery_Time"]].apply(pd.to_numeric, errors="coerce").dropna()
    m = m[(m[need].abs() > 1).all(axis=1) & (m["Drop_Latitude"].abs() < 90) & (m["Drop_Longitude"].abs() < 180)]
    if len(m) < 20:
        return None
    m = m.sample(min(1800, len(m)), random_state=7).round(4)
    lo, hi = np.percentile(m["Delivery_Time"], [5, 95])
    norm = np.clip((m["Delivery_Time"].to_numpy() - lo) / max(hi - lo, 1e-9), 0, 1)
    
    # Gradient: Green to Amber to Red
    rg = [[int(47 + 208 * x), int(208 - 115 * x), int(107 - 14 * x), 210] for x in norm]
    m["color"] = rg
    m = m.rename(columns={"Drop_Latitude": "lat", "Drop_Longitude": "lon", "Store_Latitude": "slat",
                          "Store_Longitude": "slon", "Delivery_Time": "mins"})
    clat = float(m["lat"].median())
    clon = float(m["lon"].median())
    lat_span = np.ptp(np.percentile(m["lat"], [3, 97]))
    lon_span = np.ptp(np.percentile(m["lon"], [3, 97])) * math.cos(math.radians(clat))
    zoom = float(np.clip(math.log2(360 / max(lat_span, lon_span, 0.02)) - 0.9, 2, 12))
    return m, clat, clon, zoom


# ───────────────────────────── initialize data ─────────────────────────────
md(CSS)
csv_path = find_csv()
try:
    if csv_path is not None:
        df = load_csv(str(csv_path), csv_path.stat().st_mtime)
    else:
        with st.container(key="card_upload"):
            md(card_header("Dataset Upload", f"{DATA_FILE} was not found next to app.py"))
            up = st.file_uploader("Upload delivery records CSV", type=["csv"], label_visibility="collapsed")
            if up is None:
                st.stop()
            df = clean_upload(up.getvalue().decode("utf-8", errors="ignore"))
except Exception as exc:
    st.error(f"Error loading dataset: {exc}")
    st.stop()

if df.empty:
    st.error("No usable delivery rows found.")
    st.stop()

tmin = int(math.floor(df["Delivery_Time"].min()))
tmax = int(math.ceil(df["Delivery_Time"].max()))
default_sla = int(np.clip(round(df["Delivery_Time"].mean() + df["Delivery_Time"].std()), tmin, tmax))
OPTIONS = {
    c: sorted(
        [str(v) for v in df[c].dropna().unique() if str(v).lower() != "nan"],
        key=lambda v, c=c: (TRAFFIC_ORDER.index(v) if c == "Traffic" and v in TRAFFIC_ORDER else 99, str(v))
    )
    for c in CAT_COLS
}
FILTERS = [("Weather", "f_weather", "Weather"), ("Traffic", "f_traffic", "Traffic"), ("Vehicle", "f_vehicle", "Vehicle"),
           ("Area", "f_area", "Area"), ("Category", "f_category", "Product Category")]

rlo, rhi = math.floor(df["Agent_Rating"].min() * 10) / 10, math.ceil(df["Agent_Rating"].max() * 10) / 10
alo, ahi = int(df["Agent_Age"].min()), int(df["Agent_Age"].max())

def pick(col: str, words: list[str]) -> list[str]:
    return [o for o in OPTIONS[col] if any(w in o.lower() for w in words)] or OPTIONS[col]

def reset_filters() -> None:
    for col, key, _ in FILTERS:
        st.session_state[key] = []
    st.session_state["f_rating"] = (rlo, rhi)
    st.session_state["f_age"] = (alo, ahi)

def preset(name: str) -> None:
    reset_filters()
    if name == "weather":
        st.session_state["f_weather"] = pick("Weather", ["storm", "sand", "fog"])
    elif name == "traffic":
        st.session_state["f_traffic"] = pick("Traffic", ["jam", "high"])
    elif name == "metro":
        st.session_state["f_area"] = pick("Area", ["metro"])

def reset_deck() -> None:
    st.session_state["sla"] = default_sla
    st.session_state["speedup"] = 0

for col, key, _ in FILTERS:
    st.session_state.setdefault(key, [])
st.session_state.setdefault("f_rating", (rlo, rhi))
st.session_state.setdefault("f_age", (alo, ahi))

# ───────────────────────────── sidebar ─────────────────────────────
with st.sidebar:
    md('<div class="sb-brand">Logistics Filter Panel</div>')
    
    md('<div class="sb-h">Quick Presets</div>')
    q1, q2 = st.columns(2)
    q1.button("All", on_click=preset, args=("all",), key="p_all")
    q2.button("Bad Weather", on_click=preset, args=("weather",), key="p_weather")
    q3, q4 = st.columns(2)
    q3.button("Heavy Traffic", on_click=preset, args=("traffic",), key="p_traffic")
    q4.button("Metro Only", on_click=preset, args=("metro",), key="p_metro")
    
    md('<div class="sb-h">Delivery Conditions</div>')
    for col, key, label in FILTERS:
        if len(OPTIONS[col]) <= 6:
            st.pills(label, OPTIONS[col], selection_mode="multi", key=key)
        else:
            st.multiselect(label, OPTIONS[col], key=key)
            
    md('<div class="sb-h">Courier Agent Profile</div>')
    if rlo < rhi:
        st.slider("Agent Rating", rlo, rhi, step=0.1, key="f_rating", format="%.1f")
    if alo < ahi:
        st.slider("Agent Age", alo, ahi, step=1, key="f_age")
        
    st.button("Reset All Filters", on_click=reset_filters, key="p_reset")
    st.download_button("Export CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="deliveries_export.csv", mime="text/csv", key="dl_csv")

# ───────────────────────────── filter data ─────────────────────────────
mask = np.ones(len(df), dtype=bool)
for col, key, _ in FILTERS:
    if st.session_state[key]:  
        mask &= df[col].isin(st.session_state[key]).to_numpy()
mask &= df["Agent_Rating"].between(*st.session_state["f_rating"]).to_numpy()
mask &= df["Agent_Age"].between(*st.session_state["f_age"]).to_numpy()
fdf = df[mask]

# ───────────────────────────── header ─────────────────────────────
md(H(f"""
<div class="top-header">
  <div class="brand-group">
    <div class="brand-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffb454" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="1" y="3" width="15" height="13" rx="2"/>
        <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
        <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
    </div>
    <div>
      <div class="brand-title">Last-Mile Delivery Operations</div>
      <div class="brand-sub">Real-time throughput, SLA fulfillment, bottleneck diagnostics & fleet dispatch intelligence</div>
    </div>
  </div>
  <div class="badge-count"><b>{len(fdf):,}</b> of {len(df):,} shipments active</div>
</div>
"""))

if fdf.empty:
    with st.container(key="card_empty"):
        md('<div class="empty-box"><b>No shipments match active filter criteria</b><span>Adjust filters or click a quick preset to restore data view.</span></div>')
        st.button("Reset filters", on_click=reset_filters, key="empty_reset")
    st.stop()


# ───────────────────────────── reactive dashboard ─────────────────────────────
@fragment
def dashboard(data: pd.DataFrame, full: pd.DataFrame, tmin: int, tmax: int, default_sla: int) -> None:
    t = data["Delivery_Time"].to_numpy(float)
    full_t = full["Delivery_Time"].to_numpy(float)

    # ---- Row 1: Interactive Target & What-If Control Deck ----
    with st.container(key="card_deck"):
        c1, c2, c3 = st.columns([1.3, 1.3, 1.1], gap="medium")
        with c1:
            md('<div class="deck-title">SLA On-Time Target</div>')
            sla = st.slider("Target Minutes", tmin, tmax, default_sla, 1, key="sla", label_visibility="collapsed")
            md(f'<div class="deck-note">Target threshold: <b>{sla} min</b>. Deliveries exceeding this count as SLA breach.</div>')
        
        with c2:
            md('<div class="deck-title">What-If Speedup Simulator</div>')
            pct = st.slider("Reduction %", 0, 40, 0, 1, key="speedup", label_visibility="collapsed")
            apply_to = st.pills("Apply to traffic", OPTIONS["Traffic"], selection_mode="multi",
                                default=pick("Traffic", ["jam", "high"]), key="apply_to") or []
        
        late = t > sla
        scn = t.copy()
        if pct and apply_to:
            scn[data["Traffic"].isin(apply_to).to_numpy()] *= 1 - pct / 100
        now_rate = 100 * (1 - late.mean())
        after_rate = 100 * (scn <= sla).mean()
        rescued = int(((t > sla) & (scn <= sla)).sum())
        
        with c3:
            if pct > 0 and apply_to:
                md(H(f"""
                <div class="impact-box">
                  <div class="deck-title">Projected Improvement</div>
                  <div class="impact-main">{now_rate:.1f}% <span>➔ {after_rate:.1f}%</span></div>
                  <div class="impact-note"><b>+{after_rate - now_rate:.1f} pts</b> ({rescued:,} shipments rescued)</div>
                </div>
                """))
            else:
                md(H(f"""
                <div class="impact-box">
                  <div class="deck-title">Current SLA Fulfillment</div>
                  <div class="impact-main">{now_rate:.1f}%</div>
                  <div class="impact-note">Adjust speedup slider to simulate traffic intervention</div>
                </div>
                """))
            st.button("Reset Simulator", on_click=reset_deck, key="reset_deck")

    # ---- Row 2: Executive KPI Strip ----
    avg_t = float(t.mean())
    late_rate = 100 * late.mean()
    late_count = int(late.sum())
    avg_rating = float(data["Agent_Rating"].mean())
    rating_4plus = float((data["Agent_Rating"] >= 4.0).mean() * 100)
    sla_diff = avg_t - sla

    md(H(f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">Shipment Volume</div>
        <div class="kpi-val">{len(t):,}</div>
        <div class="kpi-sub"><span class="kpi-badge grn">{len(t)/len(full)*100:.0f}%</span> of fleet in scope</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Delivery Time</div>
        <div class="kpi-val">{avg_t:.0f} min</div>
        <div class="kpi-sub">
          <span class="kpi-badge {'grn' if sla_diff <= 0 else 'red'}">{abs(sla_diff):.0f} min {'under' if sla_diff <= 0 else 'over'} SLA</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">On-Time SLA Rate</div>
        <div class="kpi-val" style="color:{GREEN if now_rate >= 80 else AMBER}">{now_rate:.1f}%</div>
        <div class="kpi-sub">Target benchmark: <b>85.0%</b></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">SLA Breaches (Late)</div>
        <div class="kpi-val" style="color:{RED if late_rate > 20 else AMBER}">{late_rate:.1f}%</div>
        <div class="kpi-sub"><span class="kpi-badge red">{late_count:,}</span> delayed packages</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Fleet Agent Rating</div>
        <div class="kpi-val" style="color:#ffd9a3">{avg_rating:.2f} ★</div>
        <div class="kpi-sub"><span class="kpi-badge grn">{rating_4plus:.0f}%</span> rated ≥ 4.0 ★</div>
      </div>
    </div>
    """))

    scenario_active = bool(pct and apply_to)

    # ---- Row 3: Tabbed Operational Sections ----
    tab_overview, tab_bottlenecks, tab_fleet, tab_geo = st.tabs([
        "Overview & Trends",
        "Delays & Bottlenecks",
        "Fleet & Audit Log",
        "Geospatial Intelligence"
    ])

    components.html("""
    <script>
    (function initLiquidMorph() {
        function setup() {
            try {
                const doc = window.parent.document;
                const tablist = doc.querySelector('div[role="tablist"]');
                if (!tablist) return;

                tablist.classList.add('apple-liquid-tablist');
                let pill = tablist.querySelector('.apple-liquid-pill');
                if (!pill) {
                    pill = doc.createElement('div');
                    pill.className = 'apple-liquid-pill';
                    tablist.prepend(pill);
                }

                function updatePill(animate) {
                    const activeTab = tablist.querySelector('div[data-testid="stTab"][aria-selected="true"], div[role="tab"][aria-selected="true"]');
                    if (!activeTab || !pill) return;

                    const listRect = tablist.getBoundingClientRect();
                    const tabRect = activeTab.getBoundingClientRect();

                    const left = tabRect.left - listRect.left;
                    const top = tabRect.top - listRect.top;
                    const width = tabRect.width;
                    const height = tabRect.height;

                    if (!animate) {
                        pill.style.transition = 'none';
                    } else {
                        pill.style.transition = 'left 0.44s cubic-bezier(0.34, 1.35, 0.64, 1), top 0.44s cubic-bezier(0.34, 1.35, 0.64, 1), width 0.38s cubic-bezier(0.34, 1.35, 0.64, 1), height 0.38s cubic-bezier(0.34, 1.35, 0.64, 1), opacity 0.25s ease, transform 0.2s cubic-bezier(0.34, 1.4, 0.64, 1)';
                    }

                    pill.style.left = left + 'px';
                    pill.style.top = top + 'px';
                    pill.style.width = width + 'px';
                    pill.style.height = height + 'px';
                    pill.style.opacity = '1';
                    tablist.setAttribute('data-pill-active', 'true');
                }

                updatePill(false);
                setTimeout(() => updatePill(true), 60);

                tablist.querySelectorAll('div[data-testid="stTab"], div[role="tab"]').forEach(tab => {
                    if (tab._liquidBound) return;
                    tab._liquidBound = true;
                    tab.addEventListener('click', () => {
                        if (pill) {
                            pill.style.transform = 'scale(0.95, 0.92)';
                            setTimeout(() => {
                                pill.style.transform = 'scale(1, 1)';
                            }, 180);
                        }
                        setTimeout(() => updatePill(true), 20);
                        setTimeout(() => updatePill(true), 120);
                    });
                });

                if (!tablist._liquidObs) {
                    const observer = new MutationObserver(() => updatePill(true));
                    observer.observe(tablist, { attributes: true, subtree: true, attributeFilter: ['aria-selected', 'data-selected'] });
                    tablist._liquidObs = observer;
                }

                window.parent.addEventListener('resize', () => updatePill(false));
            } catch (e) {
                // silent
            }
        }

        setup();
        setTimeout(setup, 200);
        setTimeout(setup, 600);
        setInterval(setup, 1500);
    })();
    </script>
    """, height=0)

    # ──── Tab 1: Overview & Time Trends ────
    with tab_overview:
        r1_c1, r1_c2 = st.columns(2, gap="medium")
        with r1_c1:
            with st.container(key="card_dist"):
                md(card_header("Delivery Duration Distribution", f"SLA Target: {sla} min"))
                show(fig_delivery_distribution(t, scn, sla, tmin, tmax, scenario_active), "fig_dist")
        with r1_c2:
            with st.container(key="card_hour"):
                md(card_header("24-Hour Demand & Delay Cycle", "Orders vs Average Delivery Minutes"))
                show(fig_hourly_profile(data, sla), "fig_hour")

        r2_c1, r2_c2 = st.columns(2, gap="medium")
        with r2_c1:
            with st.container(key="card_day"):
                md(card_header("Day-of-Week Operational Performance", "Average Delivery Time by Day"))
                show(fig_day_performance(data, sla), "fig_day")
        with r2_c2:
            with st.container(key="card_veh"):
                md(card_header("Vehicle Fleet Efficiency", "Average Duration & SLA On-Time %"))
                show(fig_vehicle_comparison(data, sla), "fig_veh")

    # ──── Tab 2: Bottlenecks & Distance Matrix ────
    with tab_bottlenecks:
        b1_c1, b1_c2 = st.columns(2, gap="medium")
        with b1_c1:
            with st.container(key="card_weather_traffic"):
                h_c1, h_c2 = st.columns([1.1, 1], vertical_alignment="center")
                h_c1.markdown(card_header("Weather & Traffic Delay Matrix"), unsafe_allow_html=True)
                with h_c2:
                    delay_m = st.segmented_control("Metric", ["Average time", "Late rate"], default="Average time",
                                                   key="delay_metric", label_visibility="collapsed") or "Average time"
                show(fig_weather_traffic(data, sla, delay_m), "fig_weather_traffic")
        with b1_c2:
            with st.container(key="card_region_heat"):
                md(card_header("Regional Bottlenecks Heatmap", "Share of deliveries by time band"))
                show(fig_regional_heatmap(data, sla, tmin, tmax), "fig_region_heat")

        b2_c1, b2_c2 = st.columns(2, gap="medium")
        with b2_c1:
            with st.container(key="card_distance"):
                md(card_header("Distance Tiers vs SLA Breach Rate", "Critical 10km latency threshold"))
                show(fig_distance_tiers(data, sla), "fig_distance")
        with b2_c2:
            with st.container(key="card_cat_box"):
                md(card_header("Product Category Turnaround Times", "Median and IQR range vs SLA target"))
                show(fig_category_box(data, sla), "fig_cat_box")

    # ──── Tab 3: Fleet & Order Audit Log ────
    with tab_fleet:
        f1_c1, f1_c2 = st.columns(2, gap="medium")
        with f1_c1:
            with st.container(key="card_agent_scatter"):
                md(card_header("Agent Rating & Age vs Delivery Time", "Colored by Age Bracket"))
                show(fig_agent_scatter(data, sla), "fig_agent_scatter")
        with f1_c2:
            with st.container(key="card_cat_rank"):
                md(card_header("Slowest Categories Leaderboard", "Ranked by average turnaround minutes"))
                md(rank_categories_html(data, sla))

        with st.container(key="card_audit_table"):
            md(card_header("Critical Delay Audit Table", "Top bottleneck orders requiring operational triage"))
            md(slowest_orders_html(data, sla))

    # ──── Tab 4: Geospatial Intelligence ────
    with tab_geo:
        M = prepare_map(data)
        if M is not None:
            pts, clat, clon, zoom = M
            with st.container(key="card_geo_map"):
                md(card_header("Live Store-to-Drop Route Paths", "Arc vectors & customer drop-off coordinates"))
                md('<div class="ramp">Faster<i></i>Slower (SLA Breach)</div>')
                deck = pdk.Deck(
                    layers=[
                        pdk.Layer(
                            "ArcLayer",
                            data=pts.head(300),
                            get_source_position="[slon, slat]",
                            get_target_position="[lon, lat]",
                            get_source_color=[255, 154, 31, 75],
                            get_target_color=[47, 208, 107, 120],
                            get_width=1.4,
                        ),
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=pts,
                            get_position="[lon, lat]",
                            get_fill_color="color",
                            get_radius=280,
                            radius_min_pixels=2.5,
                            radius_max_pixels=7,
                            pickable=True,
                            opacity=0.9,
                        ),
                    ],
                    initial_view_state=pdk.ViewState(latitude=clat, longitude=clon, zoom=zoom, pitch=25),
                    map_provider="carto",
                    map_style="dark",
                    tooltip={"html": "<b>{mins} min</b>", "style": {"backgroundColor": "rgba(16,18,22,.92)", "color": "#fff", "fontFamily": "Manrope, sans-serif"}},
                )
                st.pydeck_chart(deck, **({"height": 440} if _DECK_HEIGHT else {}))
        else:
            md('<div class="empty-box"><b>Geospatial coordinates not available for current filter slice</b></div>')


dashboard(fdf, df, tmin, tmax, default_sla)

with st.expander("Operational Calculation Methodology & Definitions"):
    st.markdown(
        "- **SLA Breach (Late)**: Any delivery exceeding the user-configured SLA on-time target (default: $\\mu + 1\\sigma = 177\\text{ min}$).\n"
        "- **Distance Tiers**: Haversine geodesic distance computed directly from store GPS coordinates to customer drop coordinates.\n"
        "- **24-Hour Cycle**: Order timestamp aggregated by hour with dual-axis overlay of shipment density and latency.\n"
        "- **What-If Simulation**: Dynamically models selective speedup improvements across specified traffic categories without reloading raw records."
    )
