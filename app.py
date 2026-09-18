import io, re, unicodedata
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

st.set_page_config(page_title="Skate Performance", page_icon="🛹", layout="wide")

st.markdown("""
<style>
:root{--bg:#06111f;--panel:#09192b;--panel2:#0c2035;--line:#173a58;--blue:#1398ff;--cyan:#5bc0ff;--green:#12dc8c;--red:#ff4050;--text:#f5f8ff;--muted:#89a5bf}
.stApp{background:radial-gradient(circle at 75% 0%,#0a1a2b 0,#06111f 42%,#050e1a 100%);color:var(--text)}
.block-container{max-width:1700px;padding-top:1.2rem;padding-bottom:3rem}
[data-testid="stHeader"]{display:none!important}
[data-testid="stToolbar"]{display:none!important}
#MainMenu{visibility:hidden!important}
footer{visibility:hidden!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stSidebar"]{background:#071522;border-right:1px solid #173a58}
[data-testid="stSidebar"] .block-container{padding-top:1.2rem}
h1,h2,h3{letter-spacing:.02em}
div[data-testid="stMetric"]{background:#09192b;border:1px solid #1b4567;border-radius:12px;padding:14px 16px}
.kpi{height:122px;background:linear-gradient(145deg,#0b1d31,#091827);border:1px solid #1b4567;border-radius:12px;padding:16px}
.klabel{font-size:12px;color:#9bb2c8;letter-spacing:.08em;font-weight:700}
.kvalue{font-size:34px;font-weight:850;margin-top:10px}.ksub{font-size:13px;margin-top:3px;color:#55bfff}
.hero{background:linear-gradient(145deg,#0b1d31,#081725);border:1px solid #1b4567;border-radius:14px;padding:14px}
.section{font-size:21px;font-weight:850;margin:22px 0 8px;letter-spacing:.03em}
.session-pill{display:inline-block;background:#0b2a45;border:1px solid #1b5d8c;color:#67c5ff;border-radius:999px;padding:5px 10px;font-size:12px;margin:2px 3px 2px 0}
.table-wrap{border:1px solid #1a4566;border-radius:12px;overflow:hidden;background:#071522}
.sk-table{width:100%;border-collapse:collapse;font-size:13px}
.sk-table th{background:#0d2237;color:#9cb4ca;text-align:left;padding:12px;border-bottom:1px solid #1b4567}
.sk-table td{padding:11px 12px;border-bottom:1px solid #112d45;color:#e9f3ff}
.sk-table tr:last-child td{border-bottom:none}.sk-table tr:hover td{background:#0a1d30}
.hit{color:#18df91!important;font-weight:800}.err{color:#ff4c5b!important;font-weight:800}.rate{color:#51bdff!important;font-weight:800}
.smallnote{color:#819db6;font-size:12px}
[data-testid="stFileUploaderDropzone"]{background:#09192b!important;border-color:#245071!important}
[data-testid="stFileUploaderDropzone"] *{color:#dcecff!important}
[data-testid="stFileUploaderFile"]{background:#0b1d31!important;color:#dcecff!important}
[data-testid="stFileUploaderFile"] *{color:#dcecff!important}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span{color:#b9cee0!important}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] strong{color:#eef7ff!important}
.stSelectbox div[data-baseweb="select"]>div,.stTextInput input{background:#09192b!important;border-color:#245071!important;color:#eef7ff!important}
div[data-baseweb="popover"],ul[role="listbox"]{background:#09192b!important}
div[role="option"]{color:#eef7ff!important}
.site-header{display:flex;align-items:center;justify-content:space-between;
background:linear-gradient(100deg,#081827,#0a2136);border:1px solid #1b4567;
border-radius:15px;padding:18px 24px;margin:2px 0 22px 0;box-shadow:0 10px 30px rgba(0,0,0,.2)}
.brand{font-size:29px;font-weight:950;font-style:italic;letter-spacing:.04em;color:#fff;line-height:1}
.brand span{color:#43b8ff}.tag{font-size:11px;color:#7fa3c0;letter-spacing:.18em;margin-top:7px}
.header-right{text-align:right}.header-right b{color:#5dc3ff;font-size:12px;letter-spacing:.12em}.header-right div{color:#7795ae;font-size:11px;margin-top:4px}

/* V4.4 - contraste dos controles */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"]{
    background:#0b1d31 !important;
    color:#eaf6ff !important;
    border-color:#245071 !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder{color:#7894ad !important;}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *{color:#dcecff !important;}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button{
    background:#102c49 !important;color:#f2f8ff !important;border:1px solid #245071 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button *{color:#f2f8ff !important;}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"]{
    background:#081827 !important;border:1px solid #245071 !important;
}
div[role="option"]{background:#081827 !important;color:#eaf6ff !important;}
div[role="option"] *{color:#eaf6ff !important;}
div[role="option"]:hover, div[role="option"][aria-selected="true"]{
    background:#0d8df0 !important;color:white !important;
}
div[role="option"]:hover *, div[role="option"][aria-selected="true"] *{color:white !important;}
[data-testid="stDownloadButton"] button{
    background:#0d2a43 !important;color:#eef8ff !important;border:1px solid #1c6b9e !important;
}
[data-testid="stDownloadButton"] button *{color:#eef8ff !important;}


/* V4.5 — correção pontual de contraste dos componentes claros do Streamlit */
[data-testid="stFileUploaderFile"]{
    background:#f1f4f8 !important;
    border:1px solid #d7e0e8 !important;
}
[data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] p{
    color:#173047 !important;
    opacity:1 !important;
}
[data-testid="stFileUploaderFile"] svg{
    color:#173047 !important;
    fill:#173047 !important;
}
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button *{
    color:#173047 !important;
}
[data-testid="stFileUploaderDropzone"] button{
    background:#f4f6f9 !important;
    color:#173047 !important;
    border:1px solid #d8e1e9 !important;
}
[data-testid="stFileUploaderDropzone"] button *{color:#173047 !important}

/* Select fechado e menu aberto: fundo claro = texto escuro */
[data-baseweb="select"] > div{
    background:#f5f6f8 !important;
    color:#15283a !important;
}
[data-baseweb="select"] > div *{color:#15283a !important}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"]{
    background:#f5f6f8 !important;
}
div[role="option"], div[role="option"] *{
    color:#15283a !important;
}
div[role="option"]:hover, div[role="option"][aria-selected="true"]{
    background:#dce9f4 !important;
}
div[role="option"]:hover *, div[role="option"][aria-selected="true"] *{
    color:#10283d !important;
}

/* Downloads permanecem dark e legíveis */
[data-testid="stDownloadButton"] button{
    background:#0d2a43 !important;
    border:1px solid #178bd1 !important;
    color:#eef8ff !important;
}
[data-testid="stDownloadButton"] button *{color:#eef8ff !important}


/* Impressão/PDF pelo navegador: preserva o dashboard inteiro como visto */
@media print{
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  html,body,.stApp{background:#06111f!important}
  [data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important}
  .block-container{max-width:none!important;padding:10mm!important}
  [data-testid="stSidebar"]{position:relative!important;width:280px!important;min-width:280px!important}
  [data-testid="stSidebarCollapseButton"]{display:none!important}
  [data-testid="stDownloadButton"]{display:none!important}
  iframe{display:none!important}
  .element-container,.stPlotlyChart,.table-wrap{break-inside:avoid!important}
}


/* V4.7 — ajustes finais de contraste */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div{
  background:#eef2f6!important;border-color:#d3dde6!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div{
  color:#10283d!important;opacity:1!important;-webkit-text-fill-color:#10283d!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg{
  color:#10283d!important;fill:#10283d!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button{
  color:#10283d!important;background:transparent!important;
}

/* Cabeçalho de KPIs */
.kpi-shell{background:linear-gradient(135deg,#081827,#0a1e32);border:1px solid #1b4567;
border-radius:16px;padding:17px 18px 18px;margin-top:2px;box-shadow:0 12px 28px rgba(0,0,0,.18)}
.kpi-title{font-size:25px;font-weight:900;color:#f6fbff;letter-spacing:.02em;margin-bottom:2px}
.kpi-subtitle{font-size:11px;color:#6dbfff;letter-spacing:.13em;margin-bottom:13px}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.kpi2{background:linear-gradient(145deg,#0c2138,#09192b);border:1px solid #205275;border-radius:11px;
padding:12px 13px;min-height:82px}
.kpi2-label{font-size:10px;color:#8baac3;font-weight:800;letter-spacing:.09em}
.kpi2-value{font-size:27px;color:#f6fbff;font-weight:950;margin-top:5px;line-height:1}
.kpi2-sub{font-size:10px;color:#49b9ff;margin-top:6px}
.kpi2-error .kpi2-value,.kpi2-error .kpi2-sub{color:#ff5260}
@media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(3,1fr)}}


/* V4.8 — controles 100% dark */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] section {
    background:#0b1d31 !important;
    border-color:#245071 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div {
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg {
    color:#8ed1ff !important;
    fill:#8ed1ff !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button * {
    background:#102b45 !important;
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}

/* select fechado */
div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background:#0b1d31 !important;
    border-color:#245071 !important;
    color:#eaf6ff !important;
}
div[data-baseweb="select"] > div *,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div * {
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}

/* menu do select aberto */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {
    background:#081827 !important;
    border-color:#245071 !important;
}
div[role="option"],
div[role="option"] *,
li[role="option"],
li[role="option"] * {
    background:#081827 !important;
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}
div[role="option"]:hover,
div[role="option"][aria-selected="true"],
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background:#123a5a !important;
}
div[role="option"]:hover *,
div[role="option"][aria-selected="true"] *,
li[role="option"]:hover *,
li[role="option"][aria-selected="true"] * {
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
}


/* V4.9 — uploader e select totalmente dark */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"]{
 background:#0a2034!important;border:1px solid #245071!important;border-radius:9px!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div > div{
 background:transparent!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div{
 color:#e9f6ff!important;-webkit-text-fill-color:#e9f6ff!important;opacity:1!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button{
 background:#102b45!important;border-color:#3b6d90!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg{
 color:#9bd7ff!important;fill:#9bd7ff!important;
}
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] label *,
[data-testid="stSelectbox"] > label p{
 color:#b9d7ec!important;-webkit-text-fill-color:#b9d7ec!important;opacity:1!important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div{
 background:#0a2034!important;border:1px solid #245071!important;color:#f2f9ff!important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div *{
 color:#f2f9ff!important;-webkit-text-fill-color:#f2f9ff!important;
}
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="menu"]{
 background:#081827!important;border:1px solid #245071!important;
}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] [role="option"] *{
 background:#081827!important;color:#eaf6ff!important;-webkit-text-fill-color:#eaf6ff!important;
}
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [role="option"][aria-selected="true"]{
 background:#123a5a!important;
}

</style>
""", unsafe_allow_html=True)

def norm(s):
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+"," ",s.strip()).upper()

def read_csv(f):
    raw=f.getvalue()
    for enc in ("utf-8-sig","utf-8","latin1"):
        for sep in (None,",",";","\t"):
            try:
                kw={"encoding":enc}
                if sep is None: kw.update(sep=None,engine="python")
                else: kw["sep"]=sep
                d=pd.read_csv(io.BytesIO(raw),**kw)
                if len(d.columns)>1:return d
            except: pass
    raise ValueError("Formato CSV não reconhecido")

def is_aggregate(d):
    return any(":" in str(c) for c in d.columns)

def empty_session(name):
    return {"name":name,"attempts":0,"hits":0,"errors":0,"maneuvers":{},
            "cats":{k:{} for k in ["AVALIACAO","DIFICULDADE","RISCO","DIRECAO","VELOCIDADE","OBSTACULO","BASE"]}}

def add(dic,key,n=1):
    key=norm(key)
    if key and key not in ("NAN","0","NONE"):
        dic[key]=dic.get(key,0)+float(n)

def parse_raw(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    # Sportscode raw export: Row = maneuver, ACERTOS = result
    mcol="ROW" if "ROW" in d.columns else next((c for c in ["MANOBRA","TRICK","CODE"] if c in d.columns),None)
    for _,r in d.iterrows():
        result=norm(r.get("ACERTOS",""))
        valid=result in ("ACERTO","ERRO")
        if valid:
            s["attempts"]+=1
            s["hits"]+=result=="ACERTO"; s["errors"]+=result=="ERRO"
            man=norm(r.get(mcol,"")) if mcol else ""
            if man and man!="NAN":
                if man not in s["maneuvers"]:s["maneuvers"][man]=[0,0]
                s["maneuvers"][man][0 if result=="ACERTO" else 1]+=1
        # categories can exist even on rows without result; count only valid attempts for consistency
        if valid:
            for cat in s["cats"]:
                val=r.get(cat,"")
                if pd.isna(val):continue
                # direction may contain "FRONTSIDE, REVERSE"
                vals=[v.strip() for v in str(val).split(",")]
                for v in vals:add(s["cats"][cat],v)
    return s

def parse_aggregate(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    mcol=d.columns[0]
    # first column is maneuver name in pivoted Sportscode CSV
    for _,r in d.iterrows():
        h=float(pd.to_numeric(r.get("ACERTOS:ACERTO",0),errors="coerce") or 0)
        e=float(pd.to_numeric(r.get("ACERTOS:ERRO",0),errors="coerce") or 0)
        man=norm(r.get(mcol,""))
        if h+e>0 and man not in ("","NAN","0"):
            s["maneuvers"][man]=[h,e]
        s["hits"]+=h;s["errors"]+=e
        for cat in s["cats"]:
            pref=cat+":"
            for c in d.columns:
                if c.startswith(pref):
                    v=pd.to_numeric(r.get(c,0),errors="coerce")
                    if pd.notna(v) and float(v)!=0:add(s["cats"][cat],c.split(":",1)[1],float(v))
    s["attempts"]=s["hits"]+s["errors"]
    return s

def merge_sessions(ss):
    out=empty_session("TODOS OS TREINOS")
    for s in ss:
        for k in ("attempts","hits","errors"):out[k]+=s[k]
        for m,(h,e) in s["maneuvers"].items():
            if m not in out["maneuvers"]:out["maneuvers"][m]=[0,0]
            out["maneuvers"][m][0]+=h;out["maneuvers"][m][1]+=e
        for cat in out["cats"]:
            for k,v in s["cats"][cat].items():add(out["cats"][cat],k,v)
    return out

PALETTE=["#0d8df0","#6bc1f7","#ff3f4d","#16d98b","#f4cf43","#a46cff","#ff8b3d"]
def donut(title,data):
    data={k:v for k,v in data.items() if v>0}
    chart_colors=(["#1398ff","#ff4050"] if title=="RESULTADO" else PALETTE[:len(data)])
    fig=go.Figure(go.Pie(labels=list(data),values=list(data.values()),hole=.66,
        marker=dict(colors=chart_colors,line=dict(color="#071522",width=1)),
        textinfo="percent",textfont=dict(size=14,color="#f5f8ff",family="Arial Black"),
        hovertemplate="<b>%{label}</b><br>%{value:.0f} • %{percent}<extra></extra>"))
    if title=="OBSTÁCULO":
        fig.update_traces(domain=dict(x=[0.18,0.82],y=[0.43,1.0]))
        fig.update_layout(title=dict(text=title,x=.04,font=dict(size=15,color="#f5f8ff")),
            height=455,margin=dict(l=8,r=8,t=45,b=195),paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
            legend=dict(orientation="h",y=-.17,x=0,xanchor="left",yanchor="top",
                        font=dict(size=9,color="#d9e9f7"),itemsizing="constant",
                        entrywidth=105,entrywidthmode="pixels"))
    else:
        fig.update_layout(title=dict(text=title,x=.04,font=dict(size=15,color="#f5f8ff")),
            height=300,margin=dict(l=8,r=8,t=45,b=75),paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
            legend=dict(orientation="h",y=-.18,x=0,font=dict(size=10,color="#d9e9f7")))
    return fig

def kpi(label,value,sub=""):
    st.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div><div class="ksub">{sub}</div></div>',unsafe_allow_html=True)

def make_pdf(athlete, cur, sessions, choice):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import mm

    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("T",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=22,textColor=colors.HexColor("#0D4E7A"),alignment=TA_LEFT,spaceAfter=5)
    h=ParagraphStyle("H",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=13,textColor=colors.HexColor("#0D4E7A"),spaceBefore=8,spaceAfter=6)
    body=ParagraphStyle("B",parent=styles["BodyText"],fontSize=9,textColor=colors.HexColor("#263746"))
    story=[Paragraph("SKATE PERFORMANCE",title),
           Paragraph(f"{athlete or 'ATLETA'} - {choice}",body),Spacer(1,6)]
    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    kdata=[["TENTATIVAS","ACERTOS","ERROS","TAXA DE ACERTO","TREINOS"],
           [f'{cur["attempts"]:.0f}',f'{cur["hits"]:.0f}',f'{cur["errors"]:.0f}',f'{rate:.1f}%',str(len(sessions))]]
    kt=Table(kdata,colWidths=[50*mm]*5,rowHeights=[8*mm,13*mm])
    kt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0D4E7A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#EDF5FA")),("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#102536")),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),("FONTSIZE",(0,1),(-1,1),16),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#A9C7DA"))
    ]))
    story += [kt,Spacer(1,8),Paragraph("MANOBRAS",h)]
    rows=[["MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]]
    for m,(hh,ee) in sorted(cur["maneuvers"].items(),key=lambda x:sum(x[1]),reverse=True):
        tt=hh+ee; rr=hh/tt*100 if tt else 0
        rows.append([m,f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr:.1f}%"])
    if len(rows)==1: rows.append(["Sem dados","0","0","0","0.0%"])
    mt=Table(rows,colWidths=[110*mm,32*mm,32*mm,32*mm,35*mm],repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
        ("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#1D2D3A")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),
        ("ALIGN",(1,1),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")
    ]))
    story.append(mt)
    if len(sessions)>1:
        story += [PageBreak(),Paragraph("EVOLUCAO ENTRE TREINOS",title)]
        ev=[["TREINO","TENTATIVAS","ACERTOS","ERROS","TAXA","DIFICULDADE ALTA"]]
        for s in sessions:
            rr=s["hits"]/s["attempts"]*100 if s["attempts"] else 0
            alta=s["cats"]["DIFICULDADE"].get("ALTA",0)
            ev.append([s["name"],f'{s["attempts"]:.0f}',f'{s["hits"]:.0f}',f'{s["errors"]:.0f}',f"{rr:.1f}%",f"{alta:.0f}"])
        et=Table(ev,colWidths=[105*mm,30*mm,30*mm,30*mm,30*mm,40*mm],repeatRows=1)
        et.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
            ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),("FONTSIZE",(0,0),(-1,-1),8),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ALIGN",(1,1),(-1,-1),"CENTER")
        ]))
        story.append(et)
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def make_visual_pdf(athlete, cur, sessions, choice, photo_file=None):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    import math

    buf=io.BytesIO(); W,H=landscape(A3)
    bg=colors.HexColor("#06111f"); panel=colors.HexColor("#0b1d31")
    panel2=colors.HexColor("#0d243b"); white=colors.HexColor("#f5f8ff")
    muted=colors.HexColor("#9bb2c8"); blue=colors.HexColor("#1398ff")
    lightblue=colors.HexColor("#6bc1f7"); red=colors.HexColor("#ff4050")
    green=colors.HexColor("#16d98b"); yellow=colors.HexColor("#f4cf43")
    purple=colors.HexColor("#a46cff"); orange=colors.HexColor("#ff8b3d")
    palette=[blue,lightblue,red,green,yellow,purple,orange]
    c=canvas.Canvas(buf,pagesize=(W,H))

    def page_bg():
        c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)

    def header(sub="PERFORMANCE ANALYSIS • TRAINING INTELLIGENCE"):
        c.setFillColor(panel); c.roundRect(10*mm,H-31*mm,W-20*mm,20*mm,4*mm,fill=1,stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-BoldOblique",19); c.drawString(17*mm,H-22*mm,"SKATE")
        c.setFillColor(blue); c.drawString(39*mm,H-22*mm,"PERFORMANCE")
        c.setFillColor(white); c.setFont("Helvetica-Bold",10); c.drawString(88*mm,H-22*mm,"• TIME BRASIL")
        c.setFillColor(lightblue); c.setFont("Helvetica",7); c.drawString(17*mm,H-27*mm,sub)
        c.setFillColor(blue); c.setFont("Helvetica-Bold",8); c.drawRightString(W-17*mm,H-21*mm,"SPORTSCODE ANALYTICS")
        c.setFillColor(muted); c.setFont("Helvetica",6.5); c.drawRightString(W-17*mm,H-26*mm,"TRAINING DATA DASHBOARD")

    def section(title,y):
        c.setFillColor(white); c.setFont("Helvetica-Bold",12); c.drawString(12*mm,y,title)

    def card(x,y,w,h,label,value,sub="",value_color=None):
        c.setFillColor(panel2); c.roundRect(x,y,w,h,3*mm,fill=1,stroke=0)
        c.setStrokeColor(colors.HexColor("#245071")); c.roundRect(x,y,w,h,3*mm,fill=0,stroke=1)
        c.setFillColor(muted); c.setFont("Helvetica-Bold",7); c.drawString(x+4*mm,y+h-7*mm,label)
        c.setFillColor(value_color or white); c.setFont("Helvetica-Bold",18); c.drawString(x+4*mm,y+8*mm,str(value))
        if sub:
            c.setFillColor(lightblue if value_color is None else value_color); c.setFont("Helvetica",6.5); c.drawString(x+4*mm,y+3.5*mm,sub)

    def donut(x,y,r,title,data,colorset=None):
        vals=[(str(k),float(v)) for k,v in data.items() if float(v)>0]
        total=sum(v for _,v in vals)
        c.setFillColor(white); c.setFont("Helvetica-Bold",9); c.drawCentredString(x,y+r+9*mm,title)
        if not vals or total<=0:
            c.setFillColor(muted); c.setFont("Helvetica",8); c.drawCentredString(x,y,"SEM DADOS"); return
        cols=colorset or palette
        angle=90
        for i,(lab,v) in enumerate(vals):
            extent=360*v/total
            c.setFillColor(cols[i%len(cols)])
            c.wedge(x-r,y-r,x+r,y+r,angle,angle+extent,fill=1,stroke=0)
            angle+=extent
        c.setFillColor(bg); c.circle(x,y,r*.58,fill=1,stroke=0)
        # legend below, 2 columns max
        ly=y-r-7*mm; colw=36*mm
        for i,(lab,v) in enumerate(vals[:8]):
            row=i//2; col=i%2; lx=x-r+col*colw
            c.setFillColor(cols[i%len(cols)]); c.rect(lx,ly-row*5*mm,2.5*mm,2.5*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",5.8)
            pct=v/total*100
            c.drawString(lx+4*mm,ly-row*5*mm,f"{lab[:16]}  {pct:.1f}%")

    def line_chart(x,y,w,h,title,values,color=blue,suffix=""):
        c.setFillColor(white); c.setFont("Helvetica-Bold",9); c.drawString(x,y+h+5*mm,title)
        c.setStrokeColor(colors.HexColor("#173047")); c.setLineWidth(.5)
        for j in range(5):
            gy=y+j*h/4; c.line(x,gy,x+w,gy)
        if not values:return
        mx=max(max(values),1); pts=[]
        for i,v in enumerate(values):
            xx=x+w*(i/max(1,len(values)-1)); yy=y+h*(v/mx*.88); pts.append((xx,yy))
        c.setStrokeColor(color); c.setLineWidth(2)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for i,(xx,yy) in enumerate(pts):
            c.setFillColor(color); c.circle(xx,yy,1.7*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",6); c.drawCentredString(xx,yy+3*mm,f"{values[i]:.1f}{suffix}")
            c.setFillColor(muted); c.setFont("Helvetica",5.3); c.drawCentredString(xx,y-4*mm,sessions[i]["name"][:24])

    # PAGE 1
    page_bg(); header()
    # Athlete/photo block
    px,py,pw,ph=12*mm,H-92*mm,55*mm,54*mm
    c.setFillColor(panel); c.roundRect(px,py,pw,ph,3*mm,fill=1,stroke=0)
    if photo_file is not None:
        try:
            photo_file.seek(0); im=ImageReader(photo_file)
            iw,ih=im.getSize(); scale=min((pw-4*mm)/iw,(ph-4*mm)/ih)
            dw,dh=iw*scale,ih*scale
            c.drawImage(im,px+(pw-dw)/2,py+(ph-dh)/2,dw,dh,preserveAspectRatio=True,mask='auto')
        except Exception: pass
    c.setFillColor(white); c.setFont("Helvetica-Bold",15); c.drawString(12*mm,H-101*mm,(athlete or "ATLETA").upper())
    c.setFillColor(muted); c.setFont("Helvetica",7); c.drawString(12*mm,H-107*mm,f"{len(sessions)} treino(s) • {choice}")

    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    vals=[("TENTATIVAS",f'{cur["attempts"]:.0f}',"volume total",None),
          ("MANOBRAS",str(len(cur["maneuvers"])),"diferentes",None),
          ("ACERTOS",f'{cur["hits"]:.0f}',f"{rate:.1f}% de acerto",None),
          ("ERROS",f'{cur["errors"]:.0f}',f"{100-rate:.1f}%",red),
          ("TREINOS",str(len(sessions)),"CSVs importados",None)]
    kx=73*mm; ky=H-78*mm; gap=3*mm; kw=(W-kx-12*mm-gap*4)/5
    for i,(lab,val,sub,col) in enumerate(vals): card(kx+i*(kw+gap),ky,kw,28*mm,lab,val,sub,col)

    section("DISTRIBUIÇÕES GERAIS",H-123*mm)
    cy=H-169*mm; rr=25*mm
    ds=[("RESULTADO",{"ACERTO":cur["hits"],"ERRO":cur["errors"]},[blue,red]),
        ("DIFICULDADE",cur["cats"]["DIFICULDADE"],None),
        ("RISCO",cur["cats"]["RISCO"],None),
        ("DIREÇÃO",cur["cats"]["DIRECAO"],None)]
    centers=[58*mm,150*mm,242*mm,334*mm]
    for xx,(t,d,cc) in zip(centers,ds): donut(xx,cy,rr,t,d,cc)

    # Maneuver table lower
    section("MANOBRAS",H-221*mm)
    tx=12*mm; ty=H-232*mm; widths=[11*mm,95*mm,28*mm,28*mm,28*mm,34*mm]
    headers=["#","MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]
    c.setFillColor(colors.HexColor("#0d2237")); c.rect(tx,ty-8*mm,sum(widths),8*mm,fill=1,stroke=0)
    c.setFillColor(muted); c.setFont("Helvetica-Bold",6.5); xx=tx
    for h,w in zip(headers,widths): c.drawString(xx+2*mm,ty-5*mm,h); xx+=w
    yy=ty-15*mm
    for idx,(m,(hh,ee)) in enumerate(sorted(cur["maneuvers"].items(),key=lambda z:sum(z[1]),reverse=True)[:8],1):
        tt=hh+ee; rr2=hh/tt*100 if tt else 0
        row=[str(idx),m[:35],f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr2:.1f}%"]
        c.setFillColor(panel if idx%2 else panel2); c.rect(tx,yy,sum(widths),6.7*mm,fill=1,stroke=0)
        xx=tx
        for j,(v,w) in enumerate(zip(row,widths)):
            c.setFillColor(red if j==3 else (blue if j in (2,5) else white)); c.setFont("Helvetica-Bold" if j in (1,2,3,5) else "Helvetica",6.3)
            c.drawString(xx+2*mm,yy+2.2*mm,v); xx+=w
        yy-=7.2*mm
    c.showPage()

    # PAGE 2: evolution + details
    page_bg(); header("SESSION EVOLUTION • PERFORMANCE DISTRIBUTION")
    section("EVOLUÇÃO ENTRE TREINOS",H-45*mm)
    rates=[ss["hits"]/ss["attempts"]*100 if ss["attempts"] else 0 for ss in sessions]
    line_chart(18*mm,H-105*mm,W-36*mm,45*mm,"TAXA DE ACERTO",rates,blue,"%")
    section("EVOLUÇÃO DA DIFICULDADE",H-125*mm)
    chartw=(W-42*mm)/3
    for i,(dif,col) in enumerate([("ALTA",red),("MEDIA",blue),("BAIXA",lightblue)]):
        vv=[ss["cats"]["DIFICULDADE"].get(dif,0) for ss in sessions]
        line_chart(14*mm+i*(chartw+7*mm),H-180*mm,chartw,35*mm,dif,vv,col,"")
    section("DETALHES",H-201*mm)
    details=[("AVALIAÇÃO",cur["cats"]["AVALIACAO"]),("VELOCIDADE",cur["cats"]["VELOCIDADE"]),
             ("OBSTÁCULO",cur["cats"]["OBSTACULO"]),("BASE",cur["cats"]["BASE"])]
    for xx,(t,d) in zip(centers,details): donut(xx,H-246*mm,22*mm,t,d,None)
    c.save(); buf.seek(0); return buf.getvalue()

def table_html(mans):
    rows=[]
    items=sorted(mans.items(),key=lambda x:sum(x[1]),reverse=True)
    for i,(m,(h,e)) in enumerate(items,1):
        t=h+e;r=(h/t*100 if t else 0)
        rows.append(f"<tr><td>{i}</td><td><b>{m}</b></td><td class='hit'>{h:.0f}</td><td class='err'>{e:.0f}</td><td>{t:.0f}</td><td class='rate'>{r:.1f}%</td></tr>")
    if not rows: rows=["<tr><td colspan='6'>Nenhuma manobra detectada nesta sessão.</td></tr>"]
    return ('<div class="table-wrap"><table class="sk-table"><thead><tr>'
            '<th>#</th><th>MANOBRA</th><th>ACERTOS</th><th>ERROS</th><th>TOTAL</th><th>TAXA DE ACERTO</th>'
            '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')

st.markdown("""
<div class="site-header">
  <div>
    <div class="brand">SKATE <span>PERFORMANCE</span> <span style="color:#f5f8ff;font-size:.62em;font-style:normal">• TIME BRASIL</span></div>
    <div class="tag">PERFORMANCE ANALYSIS • TRAINING INTELLIGENCE</div>
  </div>
  <div class="header-right">
    <b>SPORTSCODE ANALYTICS</b>
    <div>TRAINING DATA DASHBOARD</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🛹 SKATE **PERFORMANCE**")
athlete=st.sidebar.text_input("ATLETA",placeholder="Ex.: Wallace Gabriel")
photo=st.sidebar.file_uploader("FOTO DO ATLETA",type=["jpg","jpeg","png","webp"])
files=st.sidebar.file_uploader("ARQUIVOS CSV (TREINOS)",type=["csv","txt"],accept_multiple_files=True)
if not files:
    st.title("SKATE PERFORMANCE")
    st.info("Envie um ou mais CSVs do Sportscode. A V3 reconhece tanto o CSV bruto quanto o CSV agregado/pivotado.")
    st.stop()

sessions=[];problems=[]
for f in files:
    try:
        d=read_csv(f)
        sessions.append(parse_aggregate(d,Path(f.name).stem) if is_aggregate(d) else parse_raw(d,Path(f.name).stem))
    except Exception as e:problems.append(f"{f.name}: {e}")
for p in problems:st.sidebar.warning(p)

names=[s["name"] for s in sessions]
choice=st.sidebar.selectbox("SESSÃO",["TODOS OS TREINOS"]+names)
cur=merge_sessions(sessions) if choice=="TODOS OS TREINOS" else next(s for s in sessions if s["name"]==choice)
st.sidebar.success(f"{len(sessions)} CSV(s) importado(s)")
for n in names:st.sidebar.markdown(f'<span class="session-pill">✓ {n}</span>',unsafe_allow_html=True)

head1,head2=st.columns([1.05,4.5])
with head1:
    st.markdown('<div class="hero">',unsafe_allow_html=True)
    if photo:st.image(Image.open(photo),use_container_width=True)
    else:st.markdown("### 📷 FOTO")
    st.markdown(f"### {athlete or 'ATLETA'}")
    st.caption(f"{len(sessions)} treino(s) carregado(s)")
    st.markdown("</div>",unsafe_allow_html=True)
with head2:
    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    st.markdown(f"""
    <div class="kpi-shell">
      <div class="kpi-title">{(athlete.upper() if athlete else "DASHBOARD DE PERFORMANCE")}</div>
      <div class="kpi-subtitle">SKATEBOARDING • ANÁLISE DE PERFORMANCE • {choice}</div>
      <div class="kpi-grid">
        <div class="kpi2"><div class="kpi2-label">TENTATIVAS</div><div class="kpi2-value">{cur["attempts"]:.0f}</div><div class="kpi2-sub">volume total</div></div>
        <div class="kpi2"><div class="kpi2-label">MANOBRAS</div><div class="kpi2-value">{len(cur["maneuvers"])}</div><div class="kpi2-sub">manobras diferentes</div></div>
        <div class="kpi2"><div class="kpi2-label">ACERTOS</div><div class="kpi2-value">{cur["hits"]:.0f}</div><div class="kpi2-sub">{rate:.1f}% de acerto</div></div>
        <div class="kpi2 kpi2-error"><div class="kpi2-label">ERROS</div><div class="kpi2-value">{cur["errors"]:.0f}</div><div class="kpi2-sub">{100-rate:.1f}%</div></div>
        <div class="kpi2"><div class="kpi2-label">TREINOS</div><div class="kpi2-value">{len(sessions)}</div><div class="kpi2-sub">CSVs importados</div></div>
      </div>
    </div>
    """,unsafe_allow_html=True)

st.markdown('<div class="section">DISTRIBUIÇÕES GERAIS</div>',unsafe_allow_html=True)
plots=[("RESULTADO",{"ACERTO":cur["hits"],"ERRO":cur["errors"]}),
       ("DIFICULDADE",cur["cats"]["DIFICULDADE"]),("RISCO",cur["cats"]["RISCO"]),("DIREÇÃO",cur["cats"]["DIRECAO"])]
cols=st.columns(4)
for col,(title,data) in zip(cols,plots):
    with col:
        if sum(data.values()):st.plotly_chart(donut(title,data),use_container_width=True,config={"displayModeBar":False})
        else:st.info(f"{title}: sem dados")

st.markdown('<div class="section">MANOBRAS</div>',unsafe_allow_html=True)
st.markdown(table_html(cur["maneuvers"]),unsafe_allow_html=True)

if len(sessions)>1:
    st.markdown('<div class="section">EVOLUÇÃO ENTRE TREINOS</div>',unsafe_allow_html=True)
    x=[s["name"] for s in sessions]
    y=[s["hits"]/s["attempts"]*100 if s["attempts"] else 0 for s in sessions]
    fig=go.Figure(go.Scatter(x=x,y=y,mode="lines+markers+text",
        line=dict(color="#1398ff",width=3),marker=dict(size=9,color="#1398ff"),
        text=[f"{v:.1f}%" for v in y],textposition="top center"))
    fig.update_layout(height=350,yaxis=dict(title="Taxa de acerto (%)",range=[0,max(100,max(y)+10)],
        gridcolor="#173047"),xaxis=dict(title="Sessão",gridcolor="#173047"),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
        margin=dict(l=30,r=20,t=30,b=40))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    evrows="".join(f"<tr><td>{s['name']}</td><td>{s['attempts']:.0f}</td><td class='hit'>{s['hits']:.0f}</td><td class='err'>{s['errors']:.0f}</td><td class='rate'>{(s['hits']/s['attempts']*100 if s['attempts'] else 0):.1f}%</td></tr>" for s in sessions)
    st.markdown('<div class="table-wrap"><table class="sk-table"><thead><tr><th>TREINO</th><th>TENTATIVAS</th><th>ACERTOS</th><th>ERROS</th><th>TAXA</th></tr></thead><tbody>' + evrows + '</tbody></table></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">EVOLUÇÃO DA DIFICULDADE</div>',unsafe_allow_html=True)
    difficulty_choice=st.selectbox("Dificuldade para acompanhar",["ALTA","MEDIA","BAIXA"],index=0,key="difficulty_evolution")
    yd=[s["cats"]["DIFICULDADE"].get(difficulty_choice,0) for s in sessions]
    difficulty_colors={"ALTA":"#ff4c5b","MEDIA":"#1398ff","BAIXA":"#6bc1f7"}
    dc=difficulty_colors[difficulty_choice]
    figd=go.Figure(go.Scatter(x=x,y=yd,mode="lines+markers+text",
        line=dict(color=dc,width=3),marker=dict(size=9,color=dc),
        text=[f"{v:.0f}" for v in yd],textposition="top center"))
    figd.update_layout(height=350,yaxis=dict(title=f"Manobras / tentativas de dificuldade {difficulty_choice}",rangemode="tozero",
        gridcolor="#173047"),xaxis=dict(title="Sessão",gridcolor="#173047"),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#d9e9f7"),
        margin=dict(l=30,r=20,t=30,b=40))
    st.plotly_chart(figd,use_container_width=True,config={"displayModeBar":False})

st.markdown('<div class="section">DETALHES</div>',unsafe_allow_html=True)
extra=[("AVALIAÇÃO",cur["cats"]["AVALIACAO"]),("VELOCIDADE",cur["cats"]["VELOCIDADE"]),("OBSTÁCULO",cur["cats"]["OBSTACULO"]),("BASE",cur["cats"]["BASE"])]
cols=st.columns(4)
for col,(title,data) in zip(cols,extra):
    with col:
        if sum(data.values()):st.plotly_chart(donut(title,data),use_container_width=True,config={"displayModeBar":False})
        else:st.info(f"{title}: sem dados")


st.markdown('<div class="section">EXPORTAR</div>',unsafe_allow_html=True)
pdf_bytes=make_pdf(athlete,cur,sessions,choice)
safe_name=re.sub(r"[^A-Za-z0-9_-]+","_",athlete.strip() if athlete else "atleta")
ex1,ex2=st.columns(2)
with ex1:
    st.download_button("⬇ BAIXAR RELATÓRIO EM PDF", data=pdf_bytes,
        file_name=f"skate_performance_relatorio_{safe_name}.pdf", mime="application/pdf", use_container_width=True)
with ex2:
    visual_pdf=make_visual_pdf(athlete,cur,sessions,choice,photo)
    st.download_button("⬇ BAIXAR DASHBOARD VISUAL EM PDF", data=visual_pdf,
        file_name=f"skate_performance_dashboard_visual_{safe_name}.pdf", mime="application/pdf", use_container_width=True)

