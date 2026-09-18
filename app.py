
import io
import re
import unicodedata
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Skate Performance", page_icon="🛹", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 30% 0%, #08202c 0%, #031019 38%, #020b11 100%); color:#f5f7fa;}
.block-container {max-width: 1800px; padding-top: 1.2rem;}
[data-testid="stMetric"] {background:#061720; border:1px solid #244352; border-radius:10px; padding:14px;}
[data-testid="stMetricLabel"] {color:#aebdca;}
[data-testid="stMetricValue"] {color:#fff;}
div[data-testid="stFileUploader"] {background:#061720; border:1px solid #244352; border-radius:10px; padding:12px;}
h1,h2,h3 {letter-spacing:.02em;}
.panel {background:#061720;border:1px solid #244352;border-radius:10px;padding:14px 16px;margin-bottom:12px;}
.small {color:#9fb0bc;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()

def load_csv(file):
    raw = file.getvalue()
    for enc in ("utf-8-sig","utf-8","latin1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except Exception:
            pass
    raise ValueError("Não consegui ler o CSV.")

def prefix_totals(df, prefix):
    out = {}
    p = norm(prefix) + ":"
    for col in df.columns:
        c = norm(col)
        if c.startswith(p):
            label = c.split(":",1)[1]
            out[label] = int(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
    return {k:v for k,v in out.items() if v > 0}

def donut(title, values, center=None):
    labels = list(values.keys())
    vals = list(values.values())
    fig = go.Figure(go.Pie(
        labels=labels, values=vals, hole=.68,
        textinfo="none", hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"
    ))
    total = sum(vals)
    fig.update_layout(
        title=dict(text=title, x=.03, y=.97),
        height=300, margin=dict(l=15,r=15,t=48,b=10),
        paper_bgcolor="#061720", plot_bgcolor="#061720",
        font=dict(color="#f4f7fa"),
        legend=dict(orientation="v", y=.5, x=1.0),
        annotations=[dict(text=f"<b>{center or total}</b><br><span style='font-size:11px'>CLASSIFICADOS</span>",
                          x=.5,y=.5,showarrow=False,font=dict(size=23,color="white"))]
    )
    return fig

st.title("🛹 SKATE PERFORMANCE")
st.caption("Dashboard automático a partir do CSV exportado do Sportscode")

uploaded = st.file_uploader("ARRASTE O CSV DO SPORTSCODE", type=["csv"])

if not uploaded:
    st.info("Envie um CSV para gerar o dashboard.")
    st.stop()

try:
    df = load_csv(uploaded)
except Exception as e:
    st.error(str(e))
    st.stop()

# First column is normally the maneuver name in the Sportscode export.
first_col = df.columns[0]
maneuver = df[first_col].fillna("").astype(str).str.strip()
df = df.loc[maneuver.ne("")].copy()
df.rename(columns={first_col:"MANOBRA"}, inplace=True)

acertos = prefix_totals(df, "ACERTOS")
avaliacao = prefix_totals(df, "AVALIACAO")
dificuldade = prefix_totals(df, "DIFICULDADE")
risco = prefix_totals(df, "RISCO")
direcao = prefix_totals(df, "DIRECAO")
velocidade = prefix_totals(df, "VELOCIDADE")
obstaculo = prefix_totals(df, "OBSTACULO")
base = prefix_totals(df, "BASE")
evento = prefix_totals(df, "EVENTO")

hits = acertos.get("ACERTO", 0)
errors = acertos.get("ERRO", 0)
attempts = hits + errors
rate = (hits / attempts * 100) if attempts else 0

# Athlete/event hints from EVENTO columns.
event_cols = [c for c in df.columns if norm(c).startswith("EVENTO:")]
event_labels = [norm(c).split(":",1)[1] for c in event_cols]
athlete = next((x.title() for x in event_labels if "WALLACE" in x), "Atleta")
session = next((x.title() for x in event_labels if "TREINO" in x or "TRAINING" in x), "Sessão")

left, right = st.columns([1.05, 4.2])
with left:
    st.markdown(f"## {athlete.upper()}")
    st.markdown("**SKATEBOARDING PERFORMANCE**")
    st.markdown(f"<div class='panel'><b>EVENTO</b><br>{session}<br><br><b>BASE / FASE</b><br>Todos</div>", unsafe_allow_html=True)

with right:
    st.subheader("PERFORMANCE GERAL")
    a,b,c,d,e = st.columns(5)
    a.metric("TOTAL DE REGISTROS", attempts)
    b.metric("MANOBRAS", int(df["MANOBRA"].nunique()))
    c.metric("ACERTOS", hits)
    d.metric("ERROS", errors)
    e.metric("TAXA DE ACERTO", f"{rate:.1f}%".replace(".",","))

st.divider()

charts = st.columns(4)
with charts[0]:
    st.plotly_chart(donut("RESULTADO", {"Acertos":hits, "Erros":errors}, attempts), use_container_width=True)
with charts[1]:
    if dificuldade: st.plotly_chart(donut("DIFICULDADE", dificuldade), use_container_width=True)
    else: st.markdown("<div class='panel'><h3>DIFICULDADE</h3><p>Sem dados na planilha para exibir.</p></div>", unsafe_allow_html=True)
with charts[2]:
    if risco: st.plotly_chart(donut("RISCO", risco), use_container_width=True)
    else: st.markdown("<div class='panel'><h3>RISCO</h3><p>Sem dados na planilha para exibir.</p></div>", unsafe_allow_html=True)
with charts[3]:
    if direcao: st.plotly_chart(donut("DIREÇÃO", direcao), use_container_width=True)
    else: st.markdown("<div class='panel'><h3>DIREÇÃO</h3><p>Sem dados na planilha para exibir.</p></div>", unsafe_allow_html=True)

st.subheader("DESEMPENHO POR MANOBRA")
ac_col = next((c for c in df.columns if norm(c)=="ACERTOS:ACERTO"), None)
er_col = next((c for c in df.columns if norm(c)=="ACERTOS:ERRO"), None)

if ac_col and er_col:
    perf = pd.DataFrame({
        "MANOBRA": df["MANOBRA"].astype(str),
        "ACERTOS": pd.to_numeric(df[ac_col], errors="coerce").fillna(0).astype(int),
        "ERROS": pd.to_numeric(df[er_col], errors="coerce").fillna(0).astype(int),
    })
    perf["TENTATIVAS"] = perf["ACERTOS"] + perf["ERROS"]
    perf = perf[perf["TENTATIVAS"] > 0]
    perf["TAXA DE ACERTO"] = (perf["ACERTOS"] / perf["TENTATIVAS"] * 100).round(1)
    perf = perf[["MANOBRA","TENTATIVAS","ACERTOS","ERROS","TAXA DE ACERTO"]].sort_values("TENTATIVAS", ascending=False)
    st.dataframe(
        perf,
        use_container_width=True,
        hide_index=True,
        column_config={"TAXA DE ACERTO": st.column_config.ProgressColumn("TAXA DE ACERTO", min_value=0, max_value=100, format="%.1f%%")}
    )

c1,c2,c3 = st.columns(3)
with c1:
    if avaliacao: st.plotly_chart(donut("AVALIAÇÃO", avaliacao), use_container_width=True)
with c2:
    if velocidade: st.plotly_chart(donut("VELOCIDADE", velocidade), use_container_width=True)
with c3:
    if obstaculo: st.plotly_chart(donut("LOCAL / OBSTÁCULO", obstaculo), use_container_width=True)

with st.expander("Ver todos os dados detectados no CSV"):
    st.write("**Avaliação:**", avaliacao or "Sem dados")
    st.write("**Dificuldade:**", dificuldade or "Sem dados")
    st.write("**Risco:**", risco or "Sem dados")
    st.write("**Direção:**", direcao or "Sem dados")
    st.write("**Velocidade:**", velocidade or "Sem dados")
    st.write("**Obstáculos:**", obstaculo or "Sem dados")
    st.write("**Base:**", base or "Sem dados")
