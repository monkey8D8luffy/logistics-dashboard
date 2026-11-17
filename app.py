"""
Last-mile delivery dashboard, liquid-glass edition (Rubric Compliant + Sleek Sidebar).

Run locally:   streamlit run app.py
Deploy:        push app.py, requirements.txt, .streamlit/config.toml and
               "Last mile Delivery Data.csv" to the same repo folder.
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

st.set_page_config(
    page_title="Last-mile delivery",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────── tokens ─────────────────────────────
AMBER, GREEN, RED, MIST = "#ff9a1f", "#2fd06b", "#ff5d5d", "#dfe6f0"
FONT = "Manrope, system-ui, -apple-system, 'Segoe UI', sans-serif"
DATA_FILE = "Last mile Delivery Data.csv"
CAT_COLS = ["Weather", "Traffic", "Vehicle", "Area", "Category"]
NUM_COLS = ["Delivery_Time", "Agent_Age", "Agent_Rating"]
TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam"]
OK_AT, WATCH_AT = 85, 60
HEAT = [[0, "#1d1a17"], [0.45, "#7a4310"], [1, AMBER]]
PLOT_CFG = {"displayModeBar": False}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#090b0e;--tx:#f4f5f7;--mute:#9ba3ae;--amber:#ff9a1f;--green:#2fd06b;--red:#ff5d5d}

html,body{background:var(--ink)}
.stApp{
  background:
    radial-gradient(44vw 36vh at 3% 0%, rgba(255,138,0,.46), transparent 72%),
    radial-gradient(38vw 38vh at 88% 2%, rgba(34,197,94,.36), transparent 72%),
    radial-gradient(32vw 32vh at 100% 56%, rgba(255,138,0,.24), transparent 72%),
    radial-gradient(40vw 36vh at 0% 100%, rgba(34,197,94,.30), transparent 72%),
    var(--ink);
  background-attachment:fixed;color:var(--tx);-webkit-font-smoothing:antialiased;
}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{background:transparent!important}
.stApp,.stApp p,.stApp label,.stApp li,.stApp input,.stApp button,.stApp textarea,.stApp table,
[data-baseweb],[data-testid="stMarkdownContainer"] *{font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif!important}
[data-testid="stIconMaterial"]{font-family:'Material Symbols Rounded'!important}
.block-container{max-width:1480px;padding:2rem 2.2rem 4rem!important}
footer,[data-testid="stDeployButton"],[data-testid="stStatusWidget"]{display:none!important}
[data-stale="true"]{opacity:1!important;transition:none!important}
::selection{background:rgba(255,154,31,.35)}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:9px;border:2px solid transparent;background-clip:padding-box}

[class*="st-key-card"]{
  padding:1.1rem 1.3rem 1.2rem!important;gap:.6rem!important;border-radius:24px;
  background:
    radial-gradient(130% 70% at 0% 0%, rgba(255,255,255,.13), transparent 55%),
    linear-gradient(150deg, rgba(255,255,255,.10) 0%, rgba(255,255,255,.035) 40%, rgba(255,255,255,.03) 62%, rgba(255,255,255,.075) 100%);
  border:1px solid rgba(255,255,255,.12);border-top-color:rgba(255,255,255,.30);border-left-color:rgba(255,255,255,.2);
  -webkit-backdrop-filter:blur(26px) saturate(165%);backdrop-filter:blur(26px) saturate(165%);
  box-shadow:0 18px 48px -14px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.26),inset 0 0 30px rgba(255,255,255,.025);
}
[data-testid="stHorizontalBlock"]{align-items:stretch!important}
[data-testid="stColumn"] :is(div):has([class*="st-key-card"]):not([class*="st-key-card"] *){flex:1 1 auto;display:flex;flex-direction:column}
[data-testid="stColumn"] [class*="st-key-card"]{flex:1 1 auto}

/* Clean sidebar */
[data-testid="stSidebar"]{background:rgba(12,14,18,.5)!important;-webkit-backdrop-filter:blur(30px) saturate(150%);backdrop-filter:blur(30px) saturate(150%);border-right:1px solid rgba(255,255,255,.09)}
[data-testid="stSidebar"]>div:first-child,[data-testid="stSidebarContent"]{background:transparent!important}
.sb-h{font-size:12.5px;font-weight:700;color:#cfd4db;margin:.9rem 0 .35rem}
.sb-brand{display:flex;align-items:center;gap:.6rem;font-weight:800;font-size:16px;letter-spacing:-.01em;margin-bottom:1rem;}

[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{color:#aab2bd!important;font-size:12.5px!important;font-weight:600!important}
[data-baseweb="select"]>div{background:rgba(255,255,255,.055)!important;border:1px solid rgba(255,255,255,.13)!important;border-radius:12px!important}
[data-baseweb="select"]>div:focus-within{border-color:rgba(255,154,31,.7)!important;box-shadow:0 0 0 3px rgba(255,154,31,.16)}

/* Force amber theme on standard multiselect chips */
span[data-baseweb="tag"] {background-color:rgba(255,154,31,.16)!important;border:1px solid rgba(255,154,31,.35)!important;border-radius:6px!important;}
span[data-baseweb="tag"] span {color:#ffd9a3!important;font-weight:600!important;}
span[data-baseweb="tag"] span[data-baseweb="delete-icon"] svg {fill:#ffd9a3!important;}
span[data-baseweb="tag"] span[data-baseweb="delete-icon"]:hover {background-color:rgba(255,154,31,.3)!important;}

[data-baseweb="popover"]>div,[data-baseweb="menu"]{background:rgba(20,22,27,.92)!important;-webkit-backdrop-filter:blur(22px);backdrop-filter:blur(22px);border:1px solid rgba(255,255,255,.13);border-radius:14px!important}
[data-baseweb="menu"] li:hover{background:rgba(255,154,31,.14)!important}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 5px rgba(255,154,31,.26),0 0 22px rgba(255,154,31,.65)!important}
[data-testid="stSliderThumbValue"]{color:#ffd9a3!important;font-weight:700!important}
[data-testid="stSliderTickBarMin"],[data-testid="stSliderTickBarMax"]{color:var(--mute)!important;font-size:11.5px}
.stButton>button,.stDownloadButton>button{width:100%;background:rgba(255,255,255,.07);color:#eef0f3;border:1px solid rgba(255,255,255,.16);border-radius:12px;font-weight:600;font-size:13px;padding:.42rem .8rem;transition:background .2s,border-color .2s,box-shadow .2s}
.stButton>button:hover,.stDownloadButton>button:hover{background:rgba(255,154,31,.16);border-color:rgba(255,154,31,.6);color:#fff;box-shadow:0 0 22px rgba(255,154,31,.22)}
.stButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
[data-testid="stBaseButton-pills"],[data-testid="stBaseButton-segmented_control"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.14)!important;color:#d6dae0!important;border-radius:999px!important;font-weight:600!important;font-size:12.5px!important}
[data-testid="stBaseButton-pillsActive"],[data-testid="stBaseButton-segmented_controlActive"]{background:rgba(255,154,31,.22)!important;border:1px solid rgba(255,154,31,.7)!important;color:#ffd9a3!important;border-radius:999px!important;font-weight:700!important;font-size:12.5px!important;box-shadow:0 0 18px rgba(255,154,31,.25)}
[data-testid="stExpander"]{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12)!important;border-radius:18px;-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}
[data-testid="stFileUploaderDropzone"]{background:rgba(255,255,255,.05);border:1px dashed rgba(255,255,255,.25);border-radius:16px}
[data-testid="stAlert"]{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:16px}
[data-testid="stDeckGlJsonChart"],[data-testid="stDeckGlJsonChart"] iframe{border-radius:16px;overflow:hidden}

.top{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin:0 0 .4rem}
.brand{display:flex;align-items:center;gap:.9rem}
.logo{width:46px;height:46px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(145deg,rgba(255,154,31,.38),rgba(255,154,31,.08));border:1px solid rgba(255,154,31,.55);box-shadow:0 0 28px rgba(255,154,31,.28),inset 0 1px 0 rgba(255,255,255,.3)}
.brand .t{font-size:26px;font-weight:800;letter-spacing:-.025em;line-height:1.15}
.brand .s{font-size:13.5px;color:var(--mute);font-weight:500;margin-top:.1rem}
.pill{padding:.5rem .95rem;border-radius:999px;font-size:13px;font-weight:600;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}
.pill b{color:#ffd9a3}

.ct{display:flex;align-items:baseline;justify-content:space-between;gap:.75rem}
.ct b{font-size:15.5px;font-weight:700;color:#fff;letter-spacing:-.005em}
.ct span{font-size:12.5px;color:var(--mute);font-weight:500}
.dl{display:flex;align-items:flex-end;justify-content:space-between;gap:.8rem}
.dl b{display:block;font-size:15px;font-weight:700}
.dl span{display:block;font-size:12.5px;color:var(--mute);margin-top:.1rem}
.dl em{font-style:normal;font-size:22px;font-weight:800;color:#ffd9a3;font-variant-numeric:tabular-nums;white-space:nowrap}
.impact .k{font-size:12.5px;color:var(--mute);font-weight:600}
.impact .v{font-size:36px;font-weight:800;letter-spacing:-.03em;line-height:1.1;font-variant-numeric:tabular-nums}
.impact .to{font-size:14px;color:var(--mute);font-weight:600;margin:0 .55rem}
.impact .g{color:var(--green)}
.impact .s{font-size:13px;color:#cfd4db;margin-top:.25rem;line-height:1.45}
.stats{display:flex;flex-wrap:wrap;gap:1rem 0;margin:.1rem 0 .2rem}
.stat{padding:0 1.5rem;border-left:1px solid rgba(255,255,255,.14)}
.stat:first-child{padding-left:0;border-left:0}
.stat .k{font-size:12.5px;color:var(--mute);font-weight:600}
.stat .v{font-size:27px;font-weight:700;letter-spacing:-.02em;line-height:1.15;font-variant-numeric:tabular-nums}
.stat .v.big{font-size:42px;font-weight:800;letter-spacing:-.03em}
.stat .v.amb{color:var(--amber)}
.stat .v.grn{color:var(--green)}
.delta{font-size:12px;font-weight:700;margin-left:.5rem;white-space:nowrap}
.delta.good{color:var(--green)}.delta.bad{color:var(--red)}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;font-size:12.5px;color:#cfd4db;font-weight:500}
.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:.45rem;vertical-align:baseline}
.legend i.dash{border-radius:2px;width:14px;height:0;border-top:2px dashed #fff;vertical-align:middle}
.note{font-size:12px;color:var(--mute);line-height:1.5}

.rings{display:flex;flex-direction:column;gap:.8rem;justify-content:space-around;height:100%}
.ringrow{display:flex;align-items:center;gap:1.1rem}
.ringrow svg{flex:none;overflow:visible}
.ringrow .fg{transition:stroke-dasharray .6s cubic-bezier(.2,.8,.2,1)}
.ringrow .k{font-size:12.5px;color:var(--mute);font-weight:600}
.ringrow .v{font-size:28px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.rk{display:grid;grid-template-columns:1.4rem minmax(0,1.1fr) minmax(0,1fr) 3.6rem;align-items:center;gap:.6rem;padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.08);font-size:13.5px}
.rk:last-child{border-bottom:0}
.rk .no{color:var(--mute);font-weight:600}
.rk .nm{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rk .bar{height:6px;border-radius:9px;background:rgba(255,255,255,.1);overflow:hidden}
.rk .bar b{display:block;height:100%;border-radius:9px;transition:width .55s cubic-bezier(.2,.8,.2,1)}
.rk .val{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
.tw{overflow-x:auto}
.tbl{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}
.tbl th{font-weight:600;color:var(--mute);text-align:left;padding:.55rem .7rem;border-bottom:1px solid rgba(255,255,255,.18);font-size:12.5px;white-space:nowrap}
.tbl td{padding:.7rem .7rem;border-bottom:1px solid rgba(255,255,255,.08);white-space:nowrap}
.tbl tr:last-child td{border-bottom:0}
.chip{display:inline-block;padding:.14rem .6rem;border-radius:99px;font-size:12px;font-weight:700}
.chip.late{background:rgba(255,93,93,.16);color:#ffa3a3;border:1px solid rgba(255,93,93,.4)}
.chip.ok{background:rgba(47,208,107,.16);color:#8ff0b3;border:1px solid rgba(47,208,107,.4)}
.ramp{display:flex;align-items:center;gap:.6rem;font-size:12.5px;color:#cfd4db}
.ramp i{display:block;width:120px;height:8px;border-radius:9px;background:linear-gradient(90deg,#2fd06b,#ff9a1f,#ff5d5d)}
.empty{padding:2.2rem 1rem;text-align:center}
.empty b{display:block;font-size:20px;font-weight:800;margin-bottom:.3rem}
.empty span{color:var(--mute);font-size:14px}
@media (max-width:900px){.block-container{padding:1rem!important}.stat{padding:0 1rem}.stat .v.big{font-size:34px}}
@media (prefers-reduced-motion:reduce){.rk .bar b,.ringrow .fg{transition:none}}
</style>
"""

# ───────────────────────────── helpers ─────────────────────────────
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

def card_title(title: str, sub: str = "") -> str:
    return f'<div class="ct"><b>{e(title)}</b><span>{e(sub)}</span></div>'

# ───────────────────────────── data ─────────────────────────────
def _clean(raw: str) -> pd.DataFrame:
    start = raw.find("Order")
    df = pd.read_csv(io.StringIO(raw[max(start, 0):]))
    df.columns = [c.replace("\\", "").replace('"', "").strip() for c in df.columns]
    missing = [c for c in CAT_COLS + NUM_COLS if c not in df.columns]
    if missing:
        raise ValueError("The CSV is missing these columns: " + ", ".join(missing))
    df = df.dropna()
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=NUM_COLS).reset_index(drop=True)
    for c in CAT_COLS:
        df[c] = df[c].astype(str).str.replace("\\", "", regex=False).str.strip().str.title()
    df["Area"] = df["Area"].replace({"Metropolitian": "Metropolitan"})
    if "Order_Time" in df.columns:
        secs = pd.to_timedelta(df["Order_Time"].astype(str).str.strip(), errors="coerce").dt.total_seconds()
        hour = (secs // 3600).where(lambda s: s.between(0, 23))
        if hour.notna().mean() > 0.5 and hour.nunique() >= 4:
            df["Hour"] = hour
    return df

@st.cache_data(show_spinner="Reading delivery data...")
def load_csv(path: str, mtime: float) -> pd.DataFrame:
    return _clean(Path(path).read_bytes().decode("utf-8", errors="ignore"))

@st.cache_data(show_spinner="Reading delivery data...")
def clean_upload(raw: str) -> pd.DataFrame:
    return _clean(raw)

def find_csv() -> Path | None:
    for base in (Path(__file__).resolve().parent, Path.cwd()):
        p = base / DATA_FILE
        if p.exists():
            return p
    return None

def group(df: pd.DataFrame, cols: list[str]):
    g = df.groupby(cols, sort=True, observed=True)
    keys = g.size().reset_index(name="n")
    codes = g.ngroup().to_numpy()
    t = df["Delivery_Time"].to_numpy(float)
    keys["avg"] = np.bincount(codes, weights=t, minlength=len(keys)) / keys["n"].to_numpy()
    return keys, codes

def late_pct(codes: np.ndarray, k: int, t: np.ndarray, sla: float) -> np.ndarray:
    n = np.bincount(codes, minlength=k)
    return 100 * np.bincount(codes, weights=(t > sla).astype(float), minlength=k) / np.maximum(n, 1)

def prepare(df: pd.DataFrame, tmin: int, tmax: int) -> dict:
    P: dict = {"t": df["Delivery_Time"].to_numpy(float)}
    P["wt"] = group(df, ["Weather", "Traffic"])
    P["veh"] = group(df, ["Vehicle"])
    P["cat"] = group(df, ["Category"])[0]

    edges = np.linspace(tmin, tmax, 13)
    areas = sorted(df["Area"].unique())
    counts = np.array([np.histogram(df.loc[df["Area"] == a, "Delivery_Time"], bins=edges)[0] for a in areas])
    P["region"] = (areas, edges, counts)

    rows = []
    for cat, g in df.groupby("Category")["Delivery_Time"]:
        q1, med, q3 = g.quantile([0.25, 0.5, 0.75]).to_numpy()
        iqr = q3 - q1
        rows.append(dict(cat=cat, q1=q1, med=med, q3=q3, n=len(g), mean=g.mean(),
                         lo=g[g >= q1 - 1.5 * iqr].min(), hi=g[g <= q3 + 1.5 * iqr].max()))
    P["box"] = pd.DataFrame(rows).sort_values("med").reset_index(drop=True)

    s = df.sample(min(1500, len(df)), random_state=7)[["Agent_Rating", "Delivery_Time", "Agent_Age"]].copy()
    s["group"] = pd.cut(s["Agent_Age"], bins=[0, 25, 40, 200], labels=["Up to 25", "26 to 40", "Over 40"])
    P["scatter"] = s

    if "Hour" in df.columns:
        P["hour"] = df.dropna(subset=["Hour"]).groupby("Hour")["Delivery_Time"].agg(["mean", "size"]).reset_index()

    cols = [c for c in ["Order_ID", "Area", "Vehicle", "Weather", "Traffic", "Agent_Rating", "Delivery_Time"] if c in df.columns]
    P["slow"] = df.nlargest(8, "Delivery_Time")[cols]
    return P

def ramp(x: np.ndarray) -> np.ndarray:
    xs = [0, 0.5, 1]
    ch = [np.interp(x, xs, c) for c in ([47, 255, 255], [208, 154, 93], [107, 31, 93])]
    return np.stack(ch, axis=1).astype(int)

def prepare_map(df: pd.DataFrame):
    need = ["Store_Latitude", "Store_Longitude", "Drop_Latitude", "Drop_Longitude"]
    if not all(c in df.columns for c in need):
        return None
    m = df[need + ["Delivery_Time"]].apply(pd.to_numeric, errors="coerce").dropna()
    m = m[(m[need].abs() > 1).all(axis=1) & (m["Drop_Latitude"].abs() < 90) & (m["Drop_Longitude"].abs() < 180)]
    if len(m) < 20:
        return None
    m = m.sample(min(1500, len(m)), random_state=7).round(4)
    lo, hi = np.percentile(m["Delivery_Time"], [5, 95])
    x = np.clip((m["Delivery_Time"].to_numpy() - lo) / max(hi - lo, 1e-9), 0, 1)
    m["color"] = [list(map(int, c)) + [215] for c in ramp(x)]
    m = m.rename(columns={"Drop_Latitude": "lat", "Drop_Longitude": "lon", "Store_Latitude": "slat",
                          "Store_Longitude": "slon", "Delivery_Time": "mins"})
    lat_span = np.ptp(np.percentile(m["lat"], [3, 97]))
    lon_span = np.ptp(np.percentile(m["lon"], [3, 97])) * math.cos(math.radians(float(m["lat"].median())))
    zoom = float(np.clip(math.log2(360 / max(lat_span, lon_span, 0.02)) - 0.9, 2, 12))
    return m, float(m["lat"].median()), float(m["lon"].median()), zoom

# ───────────────────────────── html pieces ─────────────────────────────
def delta_tag(cur: float, base: float, lower_is_better: bool, unit: str) -> str:
    d = cur - base
    if abs(d) < 0.05:
        return ""
    good = (d < 0) == lower_is_better
    return f'<span class="delta {"good" if good else "bad"}">{"▲" if d > 0 else "▼"} {abs(d):.1f}{unit}</span>'

def stat(label: str, value: str, extra: str = "", cls: str = "") -> str:
    return f'<div class="stat"><div class="k">{label}</div><div class="v {cls}">{value}{extra}</div></div>'

def deck_label(title: str, value: str, hint: str) -> str:
    return f'<div class="dl"><div><b>{e(title)}</b><span>{e(hint)}</span></div><em>{e(value)}</em></div>'

def impact_html(now: float, after: float, rescued: int, pct: int, has_traffic: bool) -> str:
    if pct == 0 or not has_traffic:
        hint = ("Move the speed-up slider to see how many more deliveries land inside the target."
                if pct == 0 else "Pick at least one traffic level to apply the speed-up to.")
        return (f'<div class="impact"><div class="k">On-time rate</div><div class="v">{now:.1f}%</div>'
                f'<div class="s">{hint}</div></div>')
    return (f'<div class="impact"><div class="k">On-time rate with the speed-up</div>'
            f'<div class="v">{now:.1f}%<span class="to">to</span><b class="g">{after:.1f}%</b></div>'
            f'<div class="s"><b class="g">{after - now:+.1f} points</b>, {rescued:,} more deliveries on time</div></div>')

def ring_html(frac: float, color: str, big: str, small: str) -> str:
    r = 38
    c = 2 * math.pi * r
    frac = float(np.clip(frac, 0, 1))
    return (f'<div class="ringrow"><svg width="92" height="92" viewBox="0 0 100 100">'
            f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="9"/>'
            f'<circle class="fg" cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" '
            f'transform="rotate(-90 50 50)" style="stroke-dasharray:{c * frac:.1f} {c:.1f};filter:drop-shadow(0 0 5px {color})"/>'
            f'</svg><div><div class="k">{small}</div><div class="v">{big}</div></div></div>')

def rank_html(cat_keys: pd.DataFrame, sla: float) -> str:
    d = cat_keys.sort_values("avg", ascending=False).head(6)
    top = max(float(d["avg"].max()), 1.0)
    rows = "".join(
        f'<div class="rk"><span class="no">{i}</span><span class="nm">{e(r.Category)}</span>'
        f'<span class="bar"><b style="width:{r.avg / top * 100:.0f}%;background:{AMBER if r.avg > sla else GREEN}"></b></span>'
        f'<span class="val">{r.avg:.0f} min</span></div>'
        for i, r in enumerate(d.itertuples(), 1))
    return f'<div>{rows}</div>'

def table_html(df: pd.DataFrame, sla: float) -> str:
    names = {"Order_ID": "Order", "Agent_Rating": "Agent rating", "Delivery_Time": "Time"}
    head = "".join(f"<th>{e(names.get(c, c))}</th>" for c in df.columns) + "<th>Status</th>"
    body = ""
    for r in df.to_dict("records"):
        cells = ""
        for c, v in r.items():
            if c == "Delivery_Time":
                v = f"{v:.0f} min"
            elif c == "Agent_Rating":
                v = f"{v:.1f} ★"
            cells += f"<td>{e(v)}</td>"
        over = r["Delivery_Time"] - sla
        chip = f'<span class="chip late">+{over:.0f} min over target</span>' if over > 0 else '<span class="chip ok">On time</span>'
        body += f"<tr>{cells}<td>{chip}</td></tr>"
    return f'<div class="tw"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

# ───────────────────────────── figures ─────────────────────────────
def base(fig, h: int, top: int = 8, **layout):
    cfg = dict(
        height=h, margin=dict(l=4, r=4, t=top, b=4), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color="#c9ced6", size=12),
        hoverlabel=dict(bgcolor="rgba(16,18,22,.94)", bordercolor="rgba(255,255,255,.2)", font=dict(family=FONT, color="#fff", size=12)),
    )
    cfg.update(layout)
    fig.update_layout(**cfg)
    fig.update_xaxes(zeroline=False, showgrid=False, linecolor="rgba(255,255,255,.14)", ticks="",
                     tickfont=dict(color="#9ba3ae", size=11), automargin=True)
    fig.update_yaxes(zeroline=False, gridcolor="rgba(255,255,255,.07)", linecolor="rgba(0,0,0,0)", ticks="",
                     tickfont=dict(color="#9ba3ae", size=11), automargin=True)
    return fig

def target_line(fig, sla: float, axis: str = "y") -> None:
    line = dict(color="rgba(255,255,255,.75)", width=1.3, dash="dot")
    fig.add_hline(y=sla, line=line) if axis == "y" else fig.add_vline(x=sla, line=line)

def fig_dist(t, scn, sla, tmin, tmax, show_scn):
    edges = np.linspace(tmin, tmax, 45)
    mid = (edges[:-1] + edges[1:]) / 2
    cnt = np.histogram(t, edges)[0]
    k = int((mid <= sla).sum())
    fig = go.Figure()

    def area(x, y, color, fill, name):
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", name=name, fill="tozeroy", fillcolor=fill,
            line=dict(color=color, width=2.5, shape="spline", smoothing=1.0),
            hovertemplate="%{x:.0f} min: %{y:,} deliveries<extra>" + name + "</extra>"))

    area(mid[:k], cnt[:k], GREEN, "rgba(47,208,107,.20)", "On time")
    area(mid[max(k - 1, 0):], cnt[max(k - 1, 0):], AMBER, "rgba(255,154,31,.26)", "Late")
    if show_scn:
        fig.add_trace(go.Scatter(x=mid, y=np.histogram(scn, edges)[0], mode="lines", name="What-if",
                                 line=dict(color="#ffffff", width=2, dash="dash", shape="spline", smoothing=1.0),
                                 hovertemplate="%{x:.0f} min: %{y:,} deliveries<extra>What-if</extra>"))
    target_line(fig, sla, "x")
    fig.add_annotation(x=sla, y=1, yref="paper", yanchor="bottom", showarrow=False,
                       text=f"Target {sla} min", font=dict(color="#ffffff", size=11.5))
    base(fig, 300, top=26)
    fig.update_xaxes(range=[tmin, tmax], ticksuffix="m")
    return fig

def fig_hour(hour: pd.DataFrame, sla):
    fig = go.Figure(go.Scatter(
        x=hour["Hour"], y=hour["mean"], mode="lines+markers", customdata=hour["size"],
        line=dict(color=AMBER, width=3, shape="spline", smoothing=1.0), fill="tozeroy", fillcolor="rgba(255,154,31,.18)",
        marker=dict(size=7, color=AMBER, line=dict(color="#ffffff", width=1.5)),
        hovertemplate="%{x:.0f}:00, avg %{y:.0f} min<br>%{customdata:,} deliveries<extra></extra>"))
    target_line(fig, sla)
    lo, hi = float(hour["mean"].min()), float(max(hour["mean"].max(), sla))
    base(fig, 300, top=16)
    fig.update_yaxes(range=[max(lo * 0.8, 0), hi * 1.12], ticksuffix="m")
    fig.update_xaxes(tickmode="array", tickvals=list(range(0, 24, 3)), ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)])
    return fig

def fig_delay_bar(keys, codes, t, sla, metric):
    keys = keys.assign(late=late_pct(codes, len(keys), t, sla))
    y_col = "avg" if metric == "Average time" else "late"
    
    fig = go.Figure()
    colors = {"Low": GREEN, "Medium": AMBER, "High": RED, "Jam": "#a855f7"}
    
    for trf in set(keys["Traffic"]).union(TRAFFIC_ORDER):
        d = keys[keys["Traffic"] == trf]
        if d.empty:
            continue
        fig.add_trace(go.Bar(
            x=d["Weather"], y=d[y_col], name=trf,
            marker=dict(color=colors.get(trf, MIST), opacity=0.95),
            hovertemplate=f"{trf} Traffic<br>%{{y:.0f}}{'%' if metric != 'Average time' else ' min'}<extra></extra>"
        ))
    
    fig.update_layout(barmode='group')
    base(fig, 300, top=16, showlegend=True, 
         legend=dict(orientation="h", y=1.18, x=0, bgcolor="rgba(0,0,0,0)", font=dict(color="#cfd4db", size=11)))
    fig.update_yaxes(ticksuffix="%" if metric != "Average time" else "m")
    return fig

def fig_region(P, sla):
    areas, edges, counts = P["region"]
    share = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1) * 100
    mid = (edges[:-1] + edges[1:]) / 2
    hover = [[f"{a}: {edges[j]:.0f} to {edges[j + 1]:.0f} min<br>{share[i, j]:.1f}% of its deliveries<br>{counts[i, j]:,} deliveries"
              for i, a in enumerate(areas)] for j in range(len(mid))]
    fig = go.Figure(go.Heatmap(z=share.T, x=areas, y=mid, hovertext=hover, hovertemplate="%{hovertext}<extra></extra>",
                               colorscale=HEAT, showscale=False, xgap=3, ygap=3))
    target_line(fig, sla)
    base(fig, 300, top=6)
    fig.update_yaxes(showgrid=False, ticksuffix="m")
    return fig

def fig_scatter(s, sla):
    fig = go.Figure()
    for name, color in zip(["Up to 25", "26 to 40", "Over 40"], [AMBER, GREEN, MIST]):
        d = s[s["group"] == name]
        fig.add_trace(go.Scatter(x=d["Agent_Rating"], y=d["Delivery_Time"], mode="markers", name=name,
                                 marker=dict(size=6, color=color, opacity=0.65, line=dict(width=0)),
                                 hovertemplate="Rating %{x:.1f}, %{y:.0f} min<extra>" + name + "</extra>"))
    target_line(fig, sla)
    base(fig, 296, top=34, showlegend=True,
         legend=dict(orientation="h", x=0, y=1.14, bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#cfd4db")))
    fig.update_xaxes(title=dict(text="Agent rating", font=dict(size=11.5, color="#9ba3ae")))
    fig.update_yaxes(ticksuffix="m")
    return fig

def fig_vehicle_bar(keys):
    d = keys.sort_values("avg")
    fig = go.Figure(go.Bar(
        x=d["Vehicle"], 
        y=d["avg"],
        marker=dict(color=AMBER, opacity=0.85, line=dict(color="rgba(255,255,255,.4)", width=1)),
        hovertemplate="%{x}<br>Avg: %{y:.0f} min<br>%{customdata:,} deliveries<extra></extra>",
        customdata=d["n"]
    ))
    base(fig, 340, top=20)
    fig.update_yaxes(ticksuffix="m")
    return fig

def fig_box(bx, sla):
    cats = list(bx["cat"])
    over = (bx["med"] > sla).to_numpy()
    whisk_x, whisk_y = [], []
    for r in bx.itertuples():
        whisk_x += [r.lo, r.hi, None]
        whisk_y += [r.cat, r.cat, None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=whisk_x, y=whisk_y, mode="lines", hoverinfo="skip",
                             line=dict(color="rgba(255,255,255,.4)", width=1.4)))
    custom = np.stack([bx["lo"], bx["q1"], bx["med"], bx["q3"], bx["hi"], bx["n"]], axis=1)
    fig.add_trace(go.Bar(
        y=cats, x=(bx["q3"] - bx["q1"]).to_numpy(), base=bx["q1"].to_numpy(), orientation="h", width=0.55,
        marker=dict(color=[AMBER if o else GREEN for o in over], opacity=0.85,
                    line=dict(color="rgba(255,255,255,.4)", width=1)),
        customdata=custom,
        hovertemplate="%{y}<br>Typical range %{customdata[1]:.0f} to %{customdata[3]:.0f} min<br>"
                      "Median %{customdata[2]:.0f} min<br>Fastest %{customdata[0]:.0f}, slowest %{customdata[4]:.0f} min"
                      "<br>%{customdata[5]:,.0f} deliveries<extra></extra>"))
    fig.add_trace(go.Scatter(x=bx["med"], y=cats, mode="markers", hoverinfo="skip",
                             marker=dict(symbol="line-ns", size=17, color="#ffffff", line=dict(color="#ffffff", width=3))))
    target_line(fig, sla, "x")
    base(fig, max(280, 27 * len(cats) + 36), top=6)
    fig.update_yaxes(categoryorder="array", categoryarray=cats, showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,.07)", ticksuffix="m")
    return fig


# ───────────────────────────── load data ─────────────────────────────
md(CSS)
csv_path = find_csv()
try:
    if csv_path is not None:
        df = load_csv(str(csv_path), csv_path.stat().st_mtime)
    else:
        with st.container(key="card_upload"):
            md(card_title("Add your delivery data", f"{DATA_FILE} was not found next to app.py"))
            up = st.file_uploader("Upload the delivery CSV", type=["csv"], label_visibility="collapsed")
        if up is None:
            st.stop()
        df = clean_upload(up.getvalue().decode("utf-8", errors="ignore"))
except ValueError as exc:
    st.error(str(exc))
    st.stop()
if df.empty:
    st.error("No usable rows were found in the CSV after cleaning.")
    st.stop()

tmin, tmax = int(math.floor(df["Delivery_Time"].min())), int(math.ceil(df["Delivery_Time"].max()))
default_sla = int(np.clip(round(df["Delivery_Time"].mean() + df["Delivery_Time"].std()), tmin, tmax))
OPTIONS = {c: sorted(df[c].unique(), key=lambda v, c=c: (TRAFFIC_ORDER.index(v) if c == "Traffic" and v in TRAFFIC_ORDER else 99, v))
           for c in CAT_COLS}
FILTERS = [("Weather", "f_weather", "Weather"), ("Traffic", "f_traffic", "Traffic"), ("Vehicle", "f_vehicle", "Vehicle"),
           ("Area", "f_area", "Area"), ("Category", "f_category", "Product category")]
rlo, rhi = math.floor(df["Agent_Rating"].min() * 10) / 10, math.ceil(df["Agent_Rating"].max() * 10) / 10
alo, ahi = int(df["Agent_Age"].min()), int(df["Agent_Age"].max())
rmax = 5.0 if df["Agent_Rating"].max() <= 5 else float(math.ceil(df["Agent_Rating"].max()))

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
    md('<div class="sb-brand">Filter Data</div>')
    
    md('<div class="sb-h">Quick views</div>')
    q1, q2 = st.columns(2)
    q1.button("All", on_click=preset, args=("all",), key="p_all")
    q2.button("Bad weather", on_click=preset, args=("weather",), key="p_weather")
    q3, q4 = st.columns(2)
    q3.button("Heavy traffic", on_click=preset, args=("traffic",), key="p_traffic")
    q4.button("Metro only", on_click=preset, args=("metro",), key="p_metro")
    
    md('<div class="sb-h">Conditions</div>')
    for col, key, label in FILTERS:
        # Use Sleek Pills for short lists, customized amber multiselect for long lists
        if len(OPTIONS[col]) <= 6:
            st.pills(label, OPTIONS[col], selection_mode="multi", key=key)
        else:
            st.multiselect(label, OPTIONS[col], key=key)
            
    md('<div class="sb-h">Agents</div>')
    if rlo < rhi:
        st.slider("Agent rating", rlo, rhi, step=0.1, key="f_rating", format="%.1f")
    if alo < ahi:
        st.slider("Agent age", alo, ahi, step=1, key="f_age")
        
    md('<br>')
    st.button("Reset all filters", on_click=reset_filters, key="p_reset")

mask = np.ones(len(df), dtype=bool)
for col, key, _ in FILTERS:
    if st.session_state[key]:  # Only apply filter if the user selected something
        mask &= df[col].isin(st.session_state[key]).to_numpy()
mask &= df["Agent_Rating"].between(*st.session_state["f_rating"]).to_numpy()
mask &= df["Agent_Age"].between(*st.session_state["f_age"]).to_numpy()
fdf = df[mask]

with st.sidebar:
    md('<br>')
    st.download_button("Download filtered data (CSV)", fdf.to_csv(index=False).encode("utf-8"),
                       file_name="deliveries_filtered.csv", mime="text/csv", key="dl_csv")

# ───────────────────────────── header ─────────────────────────────
md(H(f"""
<div class="top"><div class="brand">
<div class="logo"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffb454" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="6" r="2.2"/><path d="M7 18h6a3.5 3.5 0 0 0 0-7h-2a3.5 3.5 0 0 1 0-7h6"/></svg></div>
<div><div class="t">Last-mile delivery</div><div class="s">How fast, how reliably, and where deliveries slow down</div></div></div>
<div class="pill"><b>{len(fdf):,}</b> of {len(df):,} deliveries in view</div></div>
"""))

if fdf.empty:
    with st.container(key="card_empty"):
        md('<div class="empty"><b>No deliveries match these filters</b><span>Widen a filter or pick a quick view to bring the data back.</span></div>')
        st.button("Reset all filters", on_click=reset_filters, key="empty_reset")
    st.stop()


# ───────────────────────────── realtime dashboard ─────────────────────────────
@fragment
def dashboard(data: pd.DataFrame, full: pd.DataFrame, P: dict, meta: dict) -> None:
    t = P["t"]
    tmin, tmax = meta["tmin"], meta["tmax"]

    # ---- control deck ----
    with st.container(key="card_deck"):
        d1, d2, d3 = st.columns([1.3, 1.3, 1.05], gap="large")
        with d1:
            ph1 = st.empty()
            sla = st.slider("On-time target in minutes", tmin, tmax, meta["sla"], 1, key="sla", label_visibility="collapsed")
            ph1.markdown(deck_label("On-time target", f"{sla} min", "Deliveries slower than this count as late."), unsafe_allow_html=True)
            md(f'<div class="note">Starts at {meta["sla"]} min: the average delivery time plus one standard deviation.</div>')
        with d2:
            ph2 = st.empty()
            pct = st.slider("Speed-up in percent", 0, 40, 0, 1, key="speedup", label_visibility="collapsed")
            ph2.markdown(deck_label("What if we were faster?", f"{pct}% less time" if pct else "Off", "Test a speed-up on the traffic levels you pick."),
                         unsafe_allow_html=True)
            apply_to = st.pills("Apply the speed-up to traffic", meta["traffic"], selection_mode="multi",
                                default=meta["jam"], key="apply_to") or []

        late = t > sla
        scn = t.copy()
        if pct and apply_to:
            scn[data["Traffic"].isin(apply_to).to_numpy()] *= 1 - pct / 100
        now = 100 * (1 - late.mean())
        after = 100 * (scn <= sla).mean()
        rescued = int(((t > sla) & (scn <= sla)).sum())
        with d3:
            md(impact_html(now, after, rescued, pct, bool(apply_to)))
            st.button("Reset target and speed-up", on_click=reset_deck, key="reset_deck")

    # ---- hero + fleet ----
    full_t = full["Delivery_Time"].to_numpy(float)
    full_late = 100 * (full_t > sla).mean()
    late_rate = 100 * late.mean()
    avg_t = float(t.mean())
    scenario_on = bool(pct and apply_to)

    a, b = st.columns([1.75, 1], gap="medium")
    with a, st.container(key="card_hero"):
        h1, h2 = st.columns([1.1, 1], vertical_alignment="center")
        h1.markdown(card_title("Delivery analytics", f"Target {sla} min"), unsafe_allow_html=True)
        views = ["Distribution"] + (["By hour"] if "hour" in P else [])
        with h2:
            view = (st.segmented_control("Chart view", views, default=views[0], key="hero_view", label_visibility="collapsed")
                    if len(views) > 1 else views[0]) or views[0]
        md(H("<div class='stats'>" +
             stat("Total deliveries", f"{len(t):,}", cls="big") +
             stat("Average time", f"{avg_t:.0f} min", delta_tag(avg_t, full_t.mean(), True, " min")) +
             stat("On time", f"{now:.1f}%", delta_tag(now, 100 - full_late, False, " pts"), "grn") +
             stat("Late", f"{late_rate:.1f}%", delta_tag(late_rate, full_late, True, " pts"), "amb") +
             "</div>"))
        if view == "By hour":
            show(fig_hour(P["hour"], sla), "fig_hero")
        else:
            show(fig_dist(t, scn, sla, tmin, tmax, scenario_on), "fig_hero")
        legend = (f'<span><i style="background:{GREEN}"></i>On time {now:.1f}%</span>'
                  f'<span><i style="background:{AMBER}"></i>Late {late_rate:.1f}%</span>')
        if scenario_on and view != "By hour":
            legend += f'<span><i class="dash"></i>What-if: {after:.1f}% on time</span>'
        md(f'<div class="legend">{legend}</div>')

    with b, st.container(key="card_fleet"):
        md(card_title("Vehicle Performance", "Average delivery time"))
        vk, vc = P["veh"]
        show(fig_vehicle_bar(vk), "fig_vehicles")

    # ---- drivers ----
    c, d = st.columns(2, gap="medium")
    with c, st.container(key="card_delay"):
        k1, k2 = st.columns([1, 1], vertical_alignment="center")
        k1.markdown(card_title("Weather and traffic", "Where delays start"), unsafe_allow_html=True)
        with k2:
            metric = st.segmented_control("Metric", ["Average time", "Late rate"], default="Average time",
                                          key="delay_metric", label_visibility="collapsed") or "Average time"
        wk, wc = P["wt"]
        show(fig_delay_bar(wk, wc, t, sla, metric), "fig_delay")

    with d, st.container(key="card_region"):
        md(card_title("Regional bottlenecks", "Share of each area's deliveries by time band"))
        show(fig_region(P, sla), "fig_region")

    # ---- people ----
    e1, e2 = st.columns([1.5, 1], gap="medium")
    with e1, st.container(key="card_agents"):
        md(card_title("Agent performance", "Rating against delivery time"))
        show(fig_scatter(P["scatter"], sla), "fig_agents")
    with e2, st.container(key="card_rings"):
        md(card_title("Performance metrics"))
        avg_rating = float(data["Agent_Rating"].mean())
        md(H("<div class='rings'>" +
             ring_html(now / 100, GREEN, f"{now:.1f}%", "On-time rate") +
             ring_html(avg_rating / meta["rmax"], AMBER, f"{avg_rating:.2f} ★", f"Average agent rating, out of {meta['rmax']:.0f}") +
             ring_html(min(avg_t / sla, 1), GREEN if avg_t <= sla else RED, f"{avg_t:.0f} min", f"Average time against the {sla} min target") +
             "</div>"))

    # ---- products ----
    f1, f2 = st.columns([1.5, 1], gap="medium")
    with f1, st.container(key="card_box"):
        md(card_title("Product categories", "Typical delivery time, green when the median is inside the target"))
        show(fig_box(P["box"], sla), "fig_box")
    with f2, st.container(key="card_rank"):
        md(card_title("Slowest categories", "Average time"))
        md(rank_html(P["cat"], sla))

    # ---- detail ----
    with st.container(key="card_table"):
        md(card_title("Slowest deliveries", "The 8 longest in the current view"))
        md(table_html(P["slow"], sla))


P = prepare(fdf, tmin, tmax)
dashboard(fdf, df, P, dict(tmin=tmin, tmax=tmax, sla=default_sla, rmax=rmax, traffic=OPTIONS["Traffic"],
                           jam=pick("Traffic", ["jam", "high"])))

# ───────────────────────────── map (static, so it never resets while sliding) ─────────────────────────────
M = prepare_map(fdf)
if M is not None:
    pts, clat, clon, zoom = M
    with st.container(key="card_map"):
        md(card_title("Delivery map", "Store to drop-off, coloured by delivery time"))
        md('<div class="ramp">Faster<i></i>Slower</div>')
        deck = pdk.Deck(
            layers=[
                pdk.Layer("ArcLayer", data=pts.head(250), get_source_position="[slon, slat]", get_target_position="[lon, lat]",
                          get_source_color=[255, 154, 31, 70], get_target_color=[47, 208, 107, 110], get_width=1.2),
                pdk.Layer("ScatterplotLayer", data=pts, get_position="[lon, lat]", get_fill_color="color", get_radius=300,
                          radius_min_pixels=2.5, radius_max_pixels=7, pickable=True, opacity=0.9),
            ],
            initial_view_state=pdk.ViewState(latitude=clat, longitude=clon, zoom=zoom, pitch=30),
            map_provider="carto", map_style="dark",
            tooltip={"html": "<b>{mins} min</b>", "style": {"backgroundColor": "rgba(16,18,22,.92)", "color": "#fff", "fontFamily": "Manrope, sans-serif"}},
        )
        st.pydeck_chart(deck, **({"height": 420} if _DECK_HEIGHT else {}))

with st.expander("How these numbers are calculated"):
    st.markdown(
        "- **Late** means a delivery took longer than the on-time target. The target starts at the average delivery time plus one standard deviation, as in the original analysis.\n"
        "- **Deltas** next to the headline numbers compare the current view with all deliveries at the same target.\n"
        "- **What-if** shortens delivery time by the chosen percentage for the traffic levels you pick, then recounts how many land inside the target. It is a simple model, not a forecast.\n"
        "- **Scatter plot** shows a fixed random sample of 1,500 deliveries so it stays fast and does not jump around.\n"
        "- Vehicle status colours use the thresholds shown under the fleet tiles."
    )
