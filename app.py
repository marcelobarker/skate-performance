import io
import re
import unicodedata
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Skate Performance", page_icon="🛹", layout="wide")

st.markdown("""
<style>
.stApp {background:#07101f; color:#f4f7fb;}
.block-container {padding-top:1.5rem; max-width:1600px;}
[data-testid="stSidebar"] {background:#0a1426;}
.kpi {
    background:linear-gradient(145deg,#0d1a2f,#101f38);
    border:1px solid #213451; border-radius:16px;
    padding:17px 18px; min-height:112px;
}
.kpi-label {font-size:.78rem;color:#8fa3bf;text-transform:uppercase;letter-spacing:.08em}
.kpi-value {font-size:2rem;font-weight:800;margin-top:6px}
.small {color:#91a3bc;font-size:.86rem}
.athlete {
    background:linear-gradient(145deg,#0c1729,#0b1424);
    border:1px solid #213451;border-radius:18px;padding:18px;
}
div[data-testid="stFileUploader"] {border-radius:14px;}
</style>
""", unsafe_allow_html=True)

def clean_text(x):
    x = str(x).strip()
    x = unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode()
    return re.sub(r"\s+", " ", x).upper()

def read_csv(uploaded):
    raw = uploaded.getvalue()
    attempts = [
        dict(sep=None, engine="python", encoding="utf-8-sig"),
        dict(sep=None, engine="python", encoding="utf-8"),
        dict(sep=None, engine="python", encoding="latin1"),
        dict(sep=",", encoding="utf-8-sig"),
        dict(sep=";", encoding="utf-8-sig"),
        dict(sep="\t", encoding="utf-8-sig"),
    ]
    last = None
    for opts in attempts:
        try:
            df = pd.read_csv(io.BytesIO(raw), **opts)
            if len(df.columns) > 1:
                return df
        except Exception as e:
            last = e
    raise ValueError(f"Não consegui ler {uploaded.name}: {last}")

def normalize_columns(df):
    out = df.copy()
    out.columns = [clean_text(c) for c in out.columns]
    return out

def prefix_totals(df, prefix):
    prefix = clean_text(prefix) + ":"
    vals = {}
    for c in df.columns:
        if c.startswith(prefix):
            label = c.split(":",1)[1].strip()
            s = pd.to_numeric(df[c], errors="coerce").fillna(0).sum()
            if s:
                vals[label] = vals.get(label, 0) + float(s)
    return vals

def find_maneuver_col(df):
    candidates = ["MANOBRA","MANEUVER","TRICK","CODE","CODIGO","NOME"]
    for c in candidates:
        if c in df.columns:
            return c
    # Sportscode normalmente traz a manobra na primeira coluna textual
    for c in df.columns:
        if ":" not in c and df[c].dtype == object:
            return c
    return df.columns[0]

def donut(title, data):
    labels = list(data.keys())
    values = list(data.values())
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=.68,
        textinfo="percent", hovertemplate="<b>%{label}</b><br>%{value:.0f}<br>%{percent}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text=title, x=.04, font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef4ff"), height=300,
        margin=dict(l=10,r=10,t=55,b=10),
        legend=dict(orientation="h", y=-.05, x=0)
    )
    return fig

def kpi(label, value, suffix=""):
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}{suffix}</div></div>',
        unsafe_allow_html=True
    )

st.sidebar.title("🛹 SKATE PERFORMANCE")
athlete_name = st.sidebar.text_input("Nome do atleta", placeholder="Ex.: Wallace Gabriel")
photo = st.sidebar.file_uploader("Foto do atleta", type=["jpg","jpeg","png","webp"])
files = st.sidebar.file_uploader(
    "CSVs dos treinos",
    type=["csv","txt"],
    accept_multiple_files=True,
    help="Cada arquivo é tratado como uma sessão/treino diferente."
)

st.sidebar.caption("Você pode enviar vários CSVs. O dashboard mantém cada arquivo como uma sessão e também cria a visão consolidada.")

if not files:
    st.title("Skate Performance Dashboard")
    st.info("Envie a foto do atleta (opcional) e um ou mais CSVs na barra lateral para gerar o dashboard.")
    st.stop()

frames = []
errors = []
for i, f in enumerate(files, start=1):
    try:
        d = normalize_columns(read_csv(f))
        d["__SESSION__"] = Path(f.name).stem
        d["__SESSION_ORDER__"] = i
        frames.append(d)
    except Exception as e:
        errors.append(str(e))

if errors:
    for e in errors:
        st.warning(e)
if not frames:
    st.stop()

# Une colunas diferentes entre sessões sem perder a origem.
all_df = pd.concat(frames, ignore_index=True, sort=False).fillna(0)
sessions = [Path(f.name).stem for f in files if Path(f.name).stem in set(all_df["__SESSION__"].astype(str))]
session_choice = st.sidebar.selectbox("Sessão", ["TODOS OS TREINOS"] + sessions)

if session_choice == "TODOS OS TREINOS":
    df = all_df.copy()
else:
    df = all_df[all_df["__SESSION__"].astype(str) == session_choice].copy()

hits_dict = prefix_totals(df, "ACERTOS")
hits = hits_dict.get("ACERTO", 0)
errs = hits_dict.get("ERRO", 0)
attempts = hits + errs

# fallback para variações comuns
if attempts == 0:
    for key in ["RESULTADO","RESULT"]:
        r = prefix_totals(df, key)
        if r:
            hits = r.get("ACERTO", r.get("HIT", r.get("MAKE",0)))
            errs = r.get("ERRO", r.get("ERROR", r.get("MISS",0)))
            attempts = hits + errs
            break

rate = (hits / attempts * 100) if attempts else 0
maneuver_col = find_maneuver_col(df)

# quantidade de manobras com alguma tentativa
tmp_attempt = pd.Series(0.0, index=df.index)
for c in df.columns:
    if c in ("ACERTOS:ACERTO","ACERTOS:ERRO"):
        tmp_attempt += pd.to_numeric(df[c], errors="coerce").fillna(0)
maneuvers = df.loc[tmp_attempt.gt(0), maneuver_col].astype(str)
maneuver_count = maneuvers[maneuvers.str.strip().ne("") & maneuvers.ne("0")].nunique()

top1, top2 = st.columns([1.1,4])
with top1:
    st.markdown('<div class="athlete">', unsafe_allow_html=True)
    if photo:
        st.image(Image.open(photo), use_container_width=True)
    else:
        st.markdown("### 📷")
        st.caption("Adicione uma foto na barra lateral")
    st.subheader(athlete_name or "ATLETA")
    st.caption("Todos os treinos" if session_choice == "TODOS OS TREINOS" else session_choice)
    st.markdown('</div>', unsafe_allow_html=True)

with top2:
    st.title("DASHBOARD DE PERFORMANCE")
    st.caption(f"{len(files)} sessão(ões) carregada(s) • filtro atual: {session_choice}")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Tentativas", f"{attempts:.0f}")
    with c2: kpi("Manobras", f"{maneuver_count}")
    with c3: kpi("Acertos", f"{hits:.0f}")
    with c4: kpi("Erros", f"{errs:.0f}")
    with c5: kpi("Taxa de acerto", f"{rate:.1f}", "%")

resultado = {"ACERTO":hits, "ERRO":errs}
difficulty = prefix_totals(df, "DIFICULDADE")
risk = prefix_totals(df, "RISCO")
direction = prefix_totals(df, "DIRECAO")
evaluation = prefix_totals(df, "AVALIACAO")
speed = prefix_totals(df, "VELOCIDADE")
obstacle = prefix_totals(df, "OBSTACULO")
base = prefix_totals(df, "BASE")

charts = [
    ("RESULTADO", resultado),
    ("DIFICULDADE", difficulty),
    ("RISCO", risk),
    ("DIREÇÃO", direction),
]
cols = st.columns(4)
for col, (title, data) in zip(cols, charts):
    with col:
        if sum(data.values()) > 0:
            st.plotly_chart(donut(title,data), use_container_width=True)
        else:
            st.info(f"{title}: sem dados")

st.subheader("MANOBRAS")
if "ACERTOS:ACERTO" in df.columns or "ACERTOS:ERRO" in df.columns:
    work = pd.DataFrame({
        "MANOBRA": df[maneuver_col].astype(str),
        "ACERTOS": pd.to_numeric(df.get("ACERTOS:ACERTO",0), errors="coerce").fillna(0) if "ACERTOS:ACERTO" in df else 0,
        "ERROS": pd.to_numeric(df.get("ACERTOS:ERRO",0), errors="coerce").fillna(0) if "ACERTOS:ERRO" in df else 0,
    })
    table = work.groupby("MANOBRA", as_index=False)[["ACERTOS","ERROS"]].sum()
    table["TOTAL"] = table["ACERTOS"] + table["ERROS"]
    table = table[table["TOTAL"] > 0]
    table["TAXA DE ACERTO"] = (table["ACERTOS"]/table["TOTAL"]*100).round(1).astype(str) + "%"
    table = table.sort_values(["TOTAL","ACERTOS"], ascending=False)
    st.dataframe(table, use_container_width=True, hide_index=True, height=430)
else:
    st.info("Não encontrei as colunas ACERTOS:ACERTO / ACERTOS:ERRO neste CSV.")

st.subheader("OUTROS INDICADORES")
extra = [("AVALIAÇÃO",evaluation),("VELOCIDADE",speed),("OBSTÁCULO / LOCAL",obstacle),("BASE",base)]
ecols = st.columns(4)
for col,(title,data) in zip(ecols,extra):
    with col:
        if sum(data.values()) > 0:
            st.plotly_chart(donut(title,data), use_container_width=True)
        else:
            st.info(f"{title}: sem dados")

# Evolução por sessão
if len(frames) > 1:
    st.subheader("EVOLUÇÃO ENTRE TREINOS")
    rows = []
    for order, one in enumerate(frames, start=1):
        session = str(one["__SESSION__"].iloc[0])
        rr = prefix_totals(one, "ACERTOS")
        h, e = rr.get("ACERTO",0), rr.get("ERRO",0)
        total = h + e
        rows.append({
            "ORDEM": order, "TREINO": session, "TENTATIVAS": total,
            "ACERTOS": h, "ERROS": e,
            "TAXA": (h/total*100 if total else 0)
        })
    evo = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evo["TREINO"], y=evo["TAXA"], mode="lines+markers+text",
        text=[f"{x:.1f}%" for x in evo["TAXA"]], textposition="top center",
        hovertemplate="<b>%{x}</b><br>Taxa de acerto: %{y:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        yaxis_title="Taxa de acerto (%)", xaxis_title="Sessão",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef4ff"), height=360, margin=dict(l=20,r=20,t=30,b=30)
    )
    st.plotly_chart(fig, use_container_width=True)
    evo_show = evo[["TREINO","TENTATIVAS","ACERTOS","ERROS","TAXA"]].copy()
    evo_show["TAXA"] = evo_show["TAXA"].round(1).astype(str) + "%"
    st.dataframe(evo_show, use_container_width=True, hide_index=True)

with st.expander("Dados detectados / conferência"):
    st.write("Sessões:", sessions)
    st.write("Coluna de manobra detectada:", maneuver_col)
    st.write("Resultado:", hits_dict)
    st.write("Dificuldade:", difficulty)
    st.write("Risco:", risk)
    st.write("Direção:", direction)
    st.write("Avaliação:", evaluation)
    st.write("Velocidade:", speed)
    st.write("Obstáculo:", obstacle)
