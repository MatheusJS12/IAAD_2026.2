# Sistema web do Torneio de Robótica (IAAD 2026.2 - 2ª VA)
# Execução: streamlit run app.py
import datetime as dt

import mysql.connector
import plotly.express as px
import streamlit as st

from db import chamar_procedure, consultar, executar, mensagem_erro

st.set_page_config(page_title="Torneio de Robótica", page_icon="🤖", layout="wide",
                   initial_sidebar_state="expanded")

if "tema" not in st.session_state:
    st.session_state.tema = "Escuro"

CATEGORIAS = ["Sumô", "Mini Sumô", "Seguidor de Linha", "Resgate"]
FUNCOES = ["Capitão", "Programador", "Mecânico", "Eletrônica", "Mentor"]
DATA_MIN, DATA_MAX = dt.date(1950, 1, 1), dt.date(2035, 12, 31)


# ---------------------------------------------------------------------
# Tema visual (paleta pastel com violeta, azul e verde-água)
# ---------------------------------------------------------------------

PALETA = ["#8B7CF6", "#68C9C3", "#F4B46A", "#E98BB5", "#78A9E8", "#A8D989"]
ESCALA = ["#D9D1FF", "#8B7CF6", "#5B4FC5"]          # degradê para barras contínuas
SEQ3 = ["#A99DFF", "#68C9C3", "#F4B46A"]            # mínima / média / máxima

ESTILO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #0F172A;
  --surface: #151F33;
  --elevated: #202C43;
  --accent: #8B7CF6;
  --accent-light: #A99DFF;
  --accent-dark: #5B4FC5;
  --on-accent: #FFFFFF;
  --border: rgba(169, 157, 255, .18);
  --border-strong: rgba(169, 157, 255, .42);
  --glow: rgba(139, 124, 246, .30);
  --text: #F7F8FC;
  --muted: #AAB3C2;
  --radius: 12px;
}

/* ---------- Tipografia ---------- */
.stApp, .stApp div, .stApp p, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li {
  font-family: 'Inter', sans-serif !important;
}
.stApp pre, .stApp code, .stApp [data-testid="stCode"] * {
  font-family: 'JetBrains Mono', ui-monospace, monospace !important;
}
.stApp h1, .stApp h2, .stApp h3 { color: var(--text); letter-spacing: -0.02em; font-weight: 700; }
.stApp p, .stApp label { color: #CBD5E1; }
[data-testid="stCaptionContainer"] * { color: var(--muted) !important; }

/* ---------- Fundo e limpeza visual ---------- */
.stApp {
  background:
    radial-gradient(1100px 480px at 85% -10%, rgba(139, 124, 246, .12), transparent 60%),
    var(--bg);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
.block-container { padding-top: 2rem; max-width: 1280px; }
hr { border-color: var(--border) !important; }

/* ---------- Cabeçalho de página ---------- */
.page-head {
  display: flex; align-items: center; gap: 1rem;
  margin: 0 0 1.5rem; padding-bottom: 1.1rem; border-bottom: 1px solid var(--border);
}
.page-icon {
  width: 48px; height: 48px; flex: none; display: grid; place-items: center; font-size: 1.45rem;
  border-radius: 14px; background: rgba(34, 211, 238, .10); border: 1px solid var(--border-strong);
}
.page-title { font-size: 1.7rem; font-weight: 700; color: var(--text); line-height: 1.15; letter-spacing: -0.02em; }
.page-sub { color: var(--muted); font-size: .92rem; margin-top: .2rem; }
.pill {
  display: inline-block; margin-bottom: .55rem; padding: .2rem .75rem; border-radius: 999px;
  background: rgba(34, 211, 238, .10); border: 1px solid var(--border);
  color: var(--accent-light); font-size: .78rem; font-weight: 600;
}
[data-testid="stHeading"] h3 {
  font-size: 1.15rem; padding-left: .75rem; border-left: 3px solid var(--accent-light);
}

/* ---------- Menu lateral ---------- */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
.brand { display: flex; align-items: center; gap: .75rem; padding: .25rem .25rem 1.25rem; }
.brand-logo {
  width: 40px; height: 40px; flex: none; display: grid; place-items: center; font-size: 1.3rem;
  border-radius: 12px; background: linear-gradient(135deg, var(--accent-dark), var(--accent-light));
  box-shadow: 0 6px 18px -6px var(--glow);
}
.brand-title { font-weight: 700; color: var(--text); line-height: 1.1; }
.brand-sub { font-size: .75rem; color: var(--muted); }

[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
  width: 100%; margin: 0; padding: .6rem .95rem; cursor: pointer;
  border-radius: 999px; border: 1px solid transparent;
  transition: background .2s ease, border-color .2s ease, transform .2s ease;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { display: none; }  /* esconde a bolinha */
[data-testid="stSidebar"] label[data-baseweb="radio"] p {
  color: var(--muted); font-weight: 500; white-space: nowrap; transition: color .2s;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
  background: rgba(34, 211, 238, .08); border-color: var(--border); transform: translateX(3px);
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover p { color: var(--text); }
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
  background: linear-gradient(90deg, rgba(6, 182, 212, .30), rgba(6, 182, 212, .08));
  border-color: var(--border-strong);
  box-shadow: inset 3px 0 0 var(--accent-light);
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p { color: #fff; font-weight: 600; }

/* ---------- Cards de métricas ---------- */
[data-testid="stMetric"] {
  background: linear-gradient(180deg, var(--elevated), var(--surface));
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.15rem 1.3rem;
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-3px); border-color: var(--border-strong);
  box-shadow: 0 12px 30px -14px var(--glow);
}
[data-testid="stMetricLabel"] p {
  color: var(--muted); text-transform: uppercase; letter-spacing: .07em; font-size: .72rem; font-weight: 600;
}
[data-testid="stMetricValue"] { color: var(--text); font-weight: 700; }

/* ---------- Abas ---------- */
[data-baseweb="tab-list"] { gap: .25rem; }
button[data-baseweb="tab"] {
  background: transparent; color: var(--muted); padding: .6rem 1.1rem;
  border-radius: 8px 8px 0 0; transition: color .2s, background .2s;
}
button[data-baseweb="tab"]:hover { color: var(--text); background: rgba(34, 211, 238, .06); }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent-light); }
[data-baseweb="tab-highlight"] {
  height: 3px; border-radius: 3px; background: linear-gradient(90deg, var(--accent), var(--accent-light));
}
[data-baseweb="tab-border"] { background: var(--border); }

/* ---------- Formulários e inputs ---------- */
[data-testid="stForm"] {
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem;
}
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: 10px !important; transition: border-color .2s, box-shadow .2s;
}
div[data-baseweb="base-input"] { background: transparent !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within {
  border-color: var(--accent-light) !important; box-shadow: 0 0 0 3px rgba(34, 211, 238, .20) !important;
}
span[data-baseweb="tag"] {
  background: rgba(34, 211, 238, .16) !important; border-radius: 8px !important;
}
span[data-baseweb="tag"] span { color: var(--accent-light) !important; }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul[role="listbox"] {
  background: var(--elevated) !important; border: 1px solid var(--border); border-radius: 10px;
}
li[role="option"]:hover, li[role="option"][aria-selected="true"] { background: rgba(34, 211, 238, .14) !important; }

/* ---------- Botões ---------- */
[data-testid^="stBaseButton-"] {
  border-radius: 10px; font-weight: 600; transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
[data-testid="stBaseButton-secondary"] {
  background: var(--elevated); border: 1px solid var(--border); color: var(--text);
}
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--accent-light); transform: translateY(-1px); }
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="stBaseButton-primaryFormSubmit"] {
  background: linear-gradient(135deg, var(--accent-dark), var(--accent) 55%, var(--accent-light));
  border: none; color: var(--on-accent); box-shadow: 0 8px 20px -10px var(--glow);
}
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-secondaryFormSubmit"] p,
[data-testid="stBaseButton-primaryFormSubmit"] p { color: var(--on-accent) !important; font-weight: 700; }
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-secondaryFormSubmit"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  transform: translateY(-2px); box-shadow: 0 14px 26px -10px var(--glow); filter: brightness(1.08);
}

/* ---------- Tabelas, código, expander ---------- */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--surface);
}
[data-testid="stCode"] { border: 1px solid var(--border); border-radius: 10px; }
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }

/* ---------- Alertas (verde/amarelo/vermelho só para manter o significado) ---------- */
[data-testid="stAlert"] { border-radius: var(--radius); border: 1px solid var(--border); }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: rgba(16,185,129,.10); border-color: rgba(16,185,129,.35); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: rgba(245,158,11,.10); border-color: rgba(245,158,11,.35); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"])   { background: rgba(239,68,68,.10);  border-color: rgba(239,68,68,.35); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"])    { background: rgba(34,211,238,.08); border-color: var(--border); }

/* ---------- Hero e cards da página inicial ---------- */
.hero {
  position: relative; overflow: hidden; padding: 2.6rem 2.6rem; margin-bottom: 1.5rem;
  border-radius: 20px; border: 1px solid var(--border);
  background:
    radial-gradient(600px 240px at 92% 0%, rgba(34, 211, 238, .24), transparent 70%),
    linear-gradient(135deg, #0F172A 0%, #111827 60%, #0B2A36 100%);
}
.hero-badge {
  display: inline-block; padding: .28rem .8rem; border-radius: 999px;
  background: rgba(34, 211, 238, .12); border: 1px solid var(--border-strong);
  color: var(--accent-light); font-size: .74rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
}
.stApp .hero h1 {
  font-size: 2.8rem !important; font-weight: 800 !important; margin: .9rem 0 .4rem !important; padding: 0 !important;
  background: linear-gradient(90deg, #FFFFFF, var(--accent-light));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: var(--muted) !important; font-size: 1.05rem; max-width: 640px; margin: 0; }
.section-label {
  margin: 1.75rem 0 .75rem; color: var(--muted); font-size: .75rem; font-weight: 600;
  letter-spacing: .1em; text-transform: uppercase;
}
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.1rem 1.3rem; transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.card:hover { transform: translateY(-3px); border-color: var(--border-strong); box-shadow: 0 12px 30px -14px var(--glow); }
.card h4 { margin: 0 0 .35rem; color: var(--accent-light); font-size: .95rem; font-weight: 600; }
.card p { margin: 0; color: var(--muted) !important; font-size: .88rem; line-height: 1.5; }
.member-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.6rem; }
.member-card { display:flex; flex-direction:column; align-items:center; text-align:center; gap:.35rem; min-height:100px; padding:.8rem .45rem; border:1px solid var(--border); border-radius:14px; background:var(--surface); color:var(--text)!important; text-decoration:none!important; transition:transform .18s,border-color .18s,box-shadow .18s; }
.member-card:hover { transform:translateY(-3px); border-color:var(--accent-light); box-shadow:0 12px 28px -16px var(--glow); }
.member-card span { font-size:1.2rem; }
.member-card strong { font-size:.76rem; line-height:1.25; }
.member-card small { color:var(--muted); font-size:.7rem; }
.leader-card { min-height:5.35rem; padding:1.15rem 1.3rem; border:1px solid var(--border); border-radius:var(--radius); background:linear-gradient(180deg,var(--elevated),var(--surface)); }
.leader-label { color:var(--muted); text-transform:uppercase; letter-spacing:.07em; font-size:.72rem; font-weight:600; }
.leader-name { color:var(--text); font-size:1.05rem; line-height:1.18; font-weight:700; overflow-wrap:anywhere; margin-top:.55rem; }

/* ---------- Moldura leve inspirada na referência ---------- */
.topbar { display:flex; align-items:center; gap:.65rem; margin:0 0 1.35rem; }
.topbar-status, .profile-chip, .notification-chip {
  min-height:2.55rem; display:flex; align-items:center; justify-content:center;
  border:1px solid var(--border); border-radius:999px; background:var(--surface);
  color:var(--muted); font-size:.78rem; white-space:nowrap;
}
.topbar-status { padding:0 .85rem; color:#68C9C3; }
.notification-chip { width:2.55rem; position:relative; font-size:1rem; }
.notification-chip::after { content:""; position:absolute; top:.45rem; right:.52rem; width:.38rem; height:.38rem; border-radius:50%; background:#E98BB5; }
.profile-chip { padding:.25rem .8rem .25rem .35rem; gap:.45rem; color:var(--text); }
.profile-avatar { width:1.85rem; height:1.85rem; display:grid; place-items:center; border-radius:50%; background:#F4B46A; color:#4C3521; font-weight:800; }
[class*="st-key-topbar-"] .stButton button { min-width:2.55rem; padding:.35rem .5rem; border-radius:999px; border:1px solid var(--border); background:var(--surface); color:var(--text); }
[class*="st-key-topbar-"] .stButton button:hover { border-color:var(--accent-light); background:rgba(139,124,246,.14); }
[class*="st-key-topbar-"] .stButton button p { font-size:1.05rem; line-height:1; }
.dashboard-intro { margin:.25rem 0 1.15rem; }
.dashboard-intro .eyebrow { color:#F4B46A; font-weight:700; font-size:.92rem; }
.dashboard-intro h1 { margin:.35rem 0 .25rem; font-size:2rem; }
.dashboard-intro p { margin:0; color:var(--muted); max-width:780px; }
.story-block { margin:1.55rem 0 .7rem; }
.story-kicker { color:var(--accent-light); font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
.story-title { color:var(--text); font-size:1.18rem; font-weight:700; margin-top:.25rem; }
.story-copy { color:var(--muted); font-size:.88rem; margin-top:.2rem; }
.quick-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; }
.quick-card { display:block; padding:1rem 1.1rem; border:1px solid var(--border); border-radius:14px; background:var(--surface); color:var(--text); text-decoration:none; }
.quick-card:hover { border-color:var(--accent-light); background:var(--elevated); }
.quick-card strong { display:block; margin-bottom:.25rem; }
.quick-card span { color:var(--muted); font-size:.82rem; }
.activity-list { display:grid; gap:.55rem; }
.activity-item { display:flex; align-items:center; gap:.75rem; padding:.7rem .8rem; border:1px solid var(--border); border-radius:12px; background:var(--surface); }
.activity-icon { width:2rem; height:2rem; display:grid; place-items:center; border-radius:10px; background:rgba(139,124,246,.16); }
.activity-item strong { color:var(--text); font-size:.87rem; }
.activity-item small { display:block; color:var(--muted); margin-top:.12rem; }
.period-filter { padding:.8rem 1rem; border:1px solid var(--border); border-radius:14px; background:var(--surface); margin-bottom:1rem; }
.period-label { color:var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; margin-bottom:.35rem; }

/* Streamlit atual usa stRadioOption; o seletor antigo deixava as bolinhas visíveis. */
[data-testid="stSidebar"] label[data-testid="stRadioOption"] { width:100%; margin:0; padding:.58rem .72rem; border-radius:10px; border:1px solid transparent; cursor:pointer; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div:first-child { display:none; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p { color:var(--muted); font-weight:500; white-space:nowrap; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) { background:rgba(139,124,246,.16); border-color:var(--border-strong); box-shadow:inset 3px 0 0 var(--accent-light); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) p { color:var(--text); font-weight:700; }

@media (max-width: 900px) {
  .block-container { padding:1.25rem 1rem 2rem; }
  .topbar { flex-wrap:wrap; }
  .quick-grid { grid-template-columns:1fr; }
  .member-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
  .hero { padding:1.7rem; }
  .stApp .hero h1 { font-size:2rem !important; }
}
@media (max-width: 640px) {
  .topbar-status, .profile-chip { flex:1; }
  .dashboard-intro h1 { font-size:1.55rem; }
  .member-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
</style>
"""
st.markdown(ESTILO, unsafe_allow_html=True)
if st.session_state.tema == "Claro":
    st.markdown("""
<style>
.stApp:has(.theme-light) { --bg:#F7F9FC; --surface:#FFFFFF; --elevated:#F3F0FF; --text:#20263A; --muted:#6E778B; --accent-light:#6B5CCF; --accent:#7B6FE8; --accent-dark:#5B4FC5; --on-accent:#FFFFFF; --border:rgba(72,66,125,.14); --border-strong:rgba(107,92,207,.36); --glow:rgba(123,111,232,.18); background:radial-gradient(900px 400px at 85% -10%,rgba(123,111,232,.10),transparent 60%),var(--bg)!important; }
.stApp:has(.theme-light) p,.stApp:has(.theme-light) label { color:#4F5A70; }
.stApp:has(.theme-light) [data-testid="stMetric"],.stApp:has(.theme-light) [data-testid="stForm"],.stApp:has(.theme-light) [data-testid="stExpander"] { background:#fff; }
.stApp:has(.theme-light) [data-testid="stSidebar"] { background:#FFFFFF; }
.stApp:has(.theme-light) [data-testid="stMetricValue"],.stApp:has(.theme-light) h1,.stApp:has(.theme-light) h2,.stApp:has(.theme-light) h3 { color:#20263A; }
.stApp:has(.theme-light) .hero { background:radial-gradient(600px 240px at 92% 0%,rgba(244,180,106,.22),transparent 70%),linear-gradient(135deg,#fff 0%,#F7F9FC 60%,#F3F0FF 100%); }
.stApp:has(.theme-light) .hero h1 { background:linear-gradient(90deg,#20263A,#6B5CCF);-webkit-background-clip:text;background-clip:text; }
.stApp:has(.theme-light) .hero p,.stApp:has(.theme-light) .card p { color:#6E778B!important; }
.stApp:has(.theme-light) .card { background:#fff; }
.stApp:has(.theme-light) div[data-baseweb="input"],.stApp:has(.theme-light) div[data-baseweb="select"]>div,.stApp:has(.theme-light) div[data-baseweb="textarea"] { background:#fff!important;color:#20263A!important; }
.stApp:has(.theme-light) [data-testid="stAlert"] { color:#303A50; }
.stApp:has(.theme-light) [data-testid="stAlert"] p { color:inherit!important; }
</style>
<div class="theme-light" style="display:none"></div>
""", unsafe_allow_html=True)


def cabecalho(titulo, subtitulo, icone):
    """Cabeçalho padrão das páginas (substitui st.header)."""
    st.markdown(
        f'<div class="page-head"><div class="page-icon">{icone}</div>'
        f'<div><div class="page-title">{titulo}</div>'
        f'<div class="page-sub">{subtitulo}</div></div></div>',
        unsafe_allow_html=True,
    )


def tabela(df, **kw):
    """Mostra um contador de registros e a tabela (mesmos argumentos do st.dataframe)."""
    n = len(df)
    st.markdown(f'<span class="pill">{n} registro{"s" if n != 1 else ""}</span>', unsafe_allow_html=True)
    st.dataframe(df, **kw)


def grafico(fig):
    """Aplica a identidade visual do tema a um gráfico Plotly e o exibe."""
    claro = st.session_state.tema == "Claro"
    cor_texto = "#334A52" if claro else "#CBD5E1"
    cor_hover = "#FFFFFF" if claro else "#1E293B"
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETA,
        font=dict(family="Inter, sans-serif", color=cor_texto, size=13),
        title=dict(font=dict(size=16, color="#172A32" if claro else "#F1F5F9"), x=0, xanchor="left"),
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", title_text=""),
        hoverlabel=dict(bgcolor=cor_hover, bordercolor="#0E8B8D" if claro else "#22D3EE",
                        font=dict(family="Inter, sans-serif", color="#172A32" if claro else "#F1F5F9", size=13)),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.25)",
                     zeroline=False, tickfont=dict(color="#94A3B8"))
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.25)",
                     zeroline=False, tickfont=dict(color="#94A3B8"))
    titulo = (fig.layout.title.text or "grafico").replace(" ", "_")
    pagina = st.session_state.get("pagina_atual", "app")
    evento = st.plotly_chart(fig, width="stretch", theme=None, on_select="rerun",
                            selection_mode="points", key=f"grafico_{pagina}_{titulo}")
    return evento


# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------

def sucesso(msg):
    """Guarda a mensagem e recarrega a página para atualizar as listas."""
    st.session_state["flash"] = msg
    st.rerun()


def rodar(sql, params, msg_ok):
    """Executa um comando e mostra sucesso ou o erro do MySQL."""
    try:
        executar(sql, params)
        sucesso(msg_ok)
    except mysql.connector.Error as e:
        st.error(mensagem_erro(e))


def opcoes_equipes():
    df = consultar("SELECT id_equipe, nome_equipe FROM equipe ORDER BY nome_equipe")
    return {f"{r.nome_equipe} (id {r.id_equipe})": r.id_equipe for r in df.itertuples()}


def opcoes_robos():
    df = consultar("""SELECT ro.id_robo, ro.nome_robo, e.nome_equipe
                        FROM robo ro JOIN equipe e ON e.id_equipe = ro.id_equipe
                       ORDER BY ro.nome_robo""")
    return {f"{r.nome_robo} - {r.nome_equipe} (id {r.id_robo})": r.id_robo for r in df.itertuples()}


def chave_de(dic, valor):
    """Devolve o índice da opção cujo valor é 'valor' (para pré-selecionar)."""
    valores = list(dic.values())
    return valores.index(valor) if valor in valores else 0


def pontos_selecionados(evento):
    """Lê uma seleção do Plotly sem quebrar em versões sem seleção ativa."""
    selecao = getattr(evento, "selection", None)
    return getattr(selecao, "points", []) if selecao else []


def barra_superior(chave):
    """Barra visual comum ao Início e ao Dashboard."""
    with st.container(key=f"topbar-{chave}"):
        busca, status, perfil, tema = st.columns([2.55, 1.15, 1.45, .55])
        with busca:
            return_value = st.text_input("Buscar", placeholder="Buscar equipe, robô ou prova...",
                                         label_visibility="collapsed", key=f"busca_{chave}")
        with status:
            st.markdown('<div class="topbar-status">● Banco local</div>', unsafe_allow_html=True)
        with perfil:
            st.markdown('<div class="profile-chip"><span class="profile-avatar">IA</span> IAAD 2026.2</div>',
                        unsafe_allow_html=True)
        with tema:
            st.button("☀️" if st.session_state.tema == "Claro" else "🌙",
                      key=f"alternar_tema_{chave}", on_click=alternar_tema,
                      help="Alternar tema", use_container_width=True)
    return return_value.strip()


def bloco_historia(kicker, titulo, texto):
    st.markdown(f'<div class="story-block"><div class="story-kicker">{kicker}</div>'
                f'<div class="story-title">{titulo}</div><div class="story-copy">{texto}</div></div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------

def pagina_inicio():
    busca = barra_superior("inicio")
    st.markdown("""<div class="hero">
<span class="hero-badge">🤖 IAAD 2026.2 · Grupo 04 · TORNEIO DE ROBÓTICA</span>
<h1>Bem-vindo ao painel</h1>
<p>Consulte os cadastros, acompanhe os resultados e entenda o desempenho do torneio em um só lugar.</p>
</div>""", unsafe_allow_html=True)
    if busca:
        st.caption(f"A busca será aplicada nos módulos de cadastro e no Dashboard: {busca}")
    c = consultar("""SELECT (SELECT COUNT(*) FROM equipe)     AS equipes,
                            (SELECT COUNT(*) FROM robo)       AS robos,
                            (SELECT COUNT(*) FROM resultado)  AS resultados,
                            (SELECT COUNT(*) FROM integrante) AS integrantes""").iloc[0]
    col = st.columns(4)
    col[0].metric("Equipes", int(c.equipes))
    col[1].metric("Robôs", int(c.robos))
    col[2].metric("Resultados", int(c.resultados))
    col[3].metric("Integrantes", int(c.integrantes))

    bloco_historia("Acompanhamento rápido", "O que precisa de atenção?",
                    "Use o Dashboard para acompanhar a história dos resultados; aqui ficam os sinais operacionais do sistema.")
    sem_resultado = int(consultar("SELECT COUNT(*) AS total FROM vw_robos_sem_resultado").iloc[0].total)
    if sem_resultado:
        st.warning(f"{sem_resultado} robô(s) ainda não possui(em) resultado. Verifique os cadastros antes da apresentação.")
    elif int(c.robos) == 0 or int(c.resultados) == 0:
        st.info("Ainda há poucos dados para compor os indicadores. Cadastre equipes, robôs e resultados para completar a visão.")
    else:
        st.success("Os cadastros principais já possuem dados suficientes para acompanhar o torneio.")

    bloco_historia("Acesso rápido", "Onde continuar",
                    "Os módulos de cadastro mantêm o CRUD; o Dashboard concentra os gráficos e a leitura de desempenho.")
    atalhos = [("Equipes", "👥", "Cadastre e consulte participantes."),
               ("Resultados", "🏆", "Registre pontuações e classificações."),
               ("Dashboard", "📊", "Explore gráficos e filtros do torneio.")]
    cols = st.columns(3)
    for coluna, (pagina, icone, descricao) in zip(cols, atalhos):
        with coluna:
            with st.container(border=True):
                if st.button(f"{icone}  {pagina}", key=f"atalho_{pagina}", use_container_width=True):
                    st.session_state.pagina_menu = pagina
                    st.rerun()
                st.caption(descricao)

    st.markdown('<div class="section-label">Equipe do projeto</div>', unsafe_allow_html=True)
    integrantes_projeto = [
        ("Bruno Rodrigo Silva Lins", "https://github.com/RodrisLins87"),
        ("Guilherme Abraão Teixeira Bezerra", "https://github.com/teixeiraguilherme"),
        ("Thyago Murilo Ferreira dos Santos", "https://github.com/ThyagomMurilo09"),
        ("Danielly Mendonça Nunes", "https://github.com/daniellynuness"),
        ("Matheus Júlio da Silva", None),
        ("Paulo Henrique da Fonseca Bezerra", None),
    ]
    cards = []
    for nome, url in integrantes_projeto:
        tag, destino = ("a", f' href="{url}" target="_blank" rel="noopener noreferrer"') if url else ("div", "")
        cards.append(f'<{tag} class="member-card"{destino}><span>🤖</span><strong>{nome}</strong>'
                     f'<small>{"Abrir perfil no GitHub ↗" if url else "Equipe do projeto"}</small></{tag}>')
    st.markdown('<div class="member-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)


def pagina_equipes():
    cabecalho("Equipes", "Cadastre, consulte e gerencie as equipes participantes", "👥")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        busca = st.text_input("Buscar por nome, escola ou cidade")
        like = f"%{busca}%"
        df = consultar("""SELECT * FROM equipe
                           WHERE nome_equipe LIKE %s OR escola LIKE %s OR cidade LIKE %s
                           ORDER BY id_equipe""", (like, like, like))
        tabela(df, hide_index=True, width="stretch")

    with criar:
        with st.form("form_criar_equipe", clear_on_submit=True):
            nome = st.text_input("Nome da equipe")
            escola = st.text_input("Escola")
            cidade = st.text_input("Cidade")
            if st.form_submit_button("Cadastrar"):
                if not (nome and escola and cidade):
                    st.warning("Preencha todos os campos.")
                else:
                    rodar("INSERT INTO equipe (nome_equipe, escola, cidade) VALUES (%s, %s, %s)",
                          (nome, escola, cidade), f"Equipe '{nome}' cadastrada.")

    with editar:
        opcoes = opcoes_equipes()
        if not opcoes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            id_eq = opcoes[st.selectbox("Equipe", opcoes, key="sel_edit_eq")]
            eq = consultar("SELECT * FROM equipe WHERE id_equipe = %s", (id_eq,)).iloc[0]
            with st.form("form_editar_equipe"):
                novo_id = st.number_input("ID da equipe", value=int(eq.id_equipe), step=1,
                                          key=f"eq_id_{id_eq}",
                                          help="Alterar o ID atualiza em cascata os robôs e integrantes.")
                nome = st.text_input("Nome da equipe", eq.nome_equipe, key=f"eq_nome_{id_eq}")
                escola = st.text_input("Escola", eq.escola, key=f"eq_esc_{id_eq}")
                cidade = st.text_input("Cidade", eq.cidade, key=f"eq_cid_{id_eq}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE equipe SET id_equipe = %s, nome_equipe = %s, escola = %s, cidade = %s
                              WHERE id_equipe = %s""",
                          (int(novo_id), nome, escola, cidade, id_eq), "Equipe atualizada.")

    with excluir:
        opcoes = opcoes_equipes()
        if not opcoes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            rotulo = st.selectbox("Equipe", opcoes, key="sel_del_eq")
            id_eq = opcoes[rotulo]
            dep = consultar("""SELECT (SELECT COUNT(*) FROM robo WHERE id_equipe = %s) AS robos,
                                      (SELECT COUNT(*) FROM resultado r JOIN robo ro ON ro.id_robo = r.id_robo
                                        WHERE ro.id_equipe = %s) AS resultados,
                                      (SELECT COUNT(*) FROM integrante WHERE id_equipe = %s) AS integrantes""",
                            (id_eq, id_eq, id_eq)).iloc[0]
            st.warning(f"Remoção em cascata: também serão apagados {int(dep.robos)} robô(s), "
                       f"{int(dep.resultados)} resultado(s) e {int(dep.integrantes)} integrante(s).")
            if st.checkbox("Confirmo a exclusão", key=f"conf_del_eq_{id_eq}"):
                if st.button("Excluir equipe", type="primary"):
                    rodar("DELETE FROM equipe WHERE id_equipe = %s", (id_eq,), f"Equipe '{rotulo}' excluída.")


def pagina_robos():
    cabecalho("Robôs", "Robôs inscritos, por categoria e equipe", "🤖")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        cats = st.multiselect("Filtrar por categoria", CATEGORIAS)
        sql = """SELECT ro.id_robo, ro.nome_robo, ro.categoria, ro.data_criacao, e.nome_equipe
                   FROM robo ro JOIN equipe e ON e.id_equipe = ro.id_equipe"""
        if cats:
            sql += " WHERE ro.categoria IN (" + ",".join(["%s"] * len(cats)) + ")"
        df = consultar(sql + " ORDER BY ro.id_robo", tuple(cats))
        tabela(df, hide_index=True, width="stretch",
                     column_config={"data_criacao": st.column_config.DateColumn("data_criacao", format="DD/MM/YYYY")})

    with criar:
        equipes = opcoes_equipes()
        with st.form("form_criar_robo", clear_on_submit=True):
            nome = st.text_input("Nome do robô")
            categoria = st.selectbox("Categoria", CATEGORIAS)
            data = st.date_input("Data de criação", dt.date.today(), DATA_MIN, DATA_MAX, format="DD/MM/YYYY")
            equipe = st.selectbox("Equipe", equipes)
            if st.form_submit_button("Cadastrar"):
                if not nome or not equipe:
                    st.warning("Informe o nome e a equipe.")
                else:
                    rodar("""INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe)
                             VALUES (%s, %s, %s, %s)""",
                          (nome, categoria, data, equipes[equipe]), f"Robô '{nome}' cadastrado.")

    with editar:
        robos, equipes = opcoes_robos(), opcoes_equipes()
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            id_r = robos[st.selectbox("Robô", robos, key="sel_edit_robo")]
            r = consultar("SELECT * FROM robo WHERE id_robo = %s", (id_r,)).iloc[0]
            with st.form("form_editar_robo"):
                nome = st.text_input("Nome do robô", r.nome_robo, key=f"r_nome_{id_r}")
                cat_idx = CATEGORIAS.index(r.categoria) if r.categoria in CATEGORIAS else 0
                categoria = st.selectbox("Categoria", CATEGORIAS, cat_idx, key=f"r_cat_{id_r}")
                data = st.date_input("Data de criação", r.data_criacao, DATA_MIN, DATA_MAX,
                                     format="DD/MM/YYYY", key=f"r_data_{id_r}")
                equipe = st.selectbox("Equipe", equipes, chave_de(equipes, r.id_equipe), key=f"r_eq_{id_r}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE robo SET nome_robo = %s, categoria = %s, data_criacao = %s, id_equipe = %s
                              WHERE id_robo = %s""",
                          (nome, categoria, data, equipes[equipe], id_r), "Robô atualizado.")

    with excluir:
        robos = opcoes_robos()
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            rotulo = st.selectbox("Robô", robos, key="sel_del_robo")
            id_r = robos[rotulo]
            n = consultar("SELECT COUNT(*) AS n FROM resultado WHERE id_robo = %s", (id_r,)).iloc[0].n
            st.warning(f"Remoção em cascata: {int(n)} resultado(s) deste robô também serão apagados.")
            if st.checkbox("Confirmo a exclusão", key=f"conf_del_r_{id_r}"):
                if st.button("Excluir robô", type="primary"):
                    rodar("DELETE FROM robo WHERE id_robo = %s", (id_r,), f"Robô '{rotulo}' excluído.")


def pagina_resultados():
    cabecalho("Resultados", "Classificações e pontuações por prova", "🏆")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])
    provas = consultar("SELECT DISTINCT nome_prova FROM resultado ORDER BY nome_prova").nome_prova.tolist()

    with listar:
        prova = st.selectbox("Filtrar por prova", ["Todas"] + provas)
        sql = """SELECT r.nome_prova, r.classificacao, r.pontuacao, ro.nome_robo, e.nome_equipe
                   FROM resultado r
                   JOIN robo ro  ON ro.id_robo  = r.id_robo
                   JOIN equipe e ON e.id_equipe = ro.id_equipe"""
        params = ()
        if prova != "Todas":
            sql += " WHERE r.nome_prova = %s"
            params = (prova,)
        df = consultar(sql + " ORDER BY r.nome_prova, r.classificacao", params)
        tabela(df, hide_index=True, width="stretch")

    with criar:
        robos = opcoes_robos()
        st.caption("Provas existentes: " + ", ".join(provas))
        with st.form("form_criar_resultado", clear_on_submit=True):
            nome_prova = st.text_input("Nome da prova")
            classificacao = st.number_input("Classificação", value=1, step=1)
            pontuacao = st.number_input("Pontuação (0 a 100)", value=0.0, step=0.5, format="%.2f")
            robo = st.selectbox("Robô", robos)
            if st.form_submit_button("Cadastrar"):
                if not nome_prova or not robo:
                    st.warning("Informe a prova e o robô.")
                else:
                    rodar("""INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
                             VALUES (%s, %s, %s, %s)""",
                          (nome_prova, int(classificacao), pontuacao, robos[robo]), "Resultado cadastrado.")

    df_res = consultar("""SELECT r.*, ro.nome_robo FROM resultado r
                          JOIN robo ro ON ro.id_robo = r.id_robo
                          ORDER BY r.nome_prova, r.classificacao""")
    chaves = {f"{r.nome_prova} - {r.classificacao}º lugar ({r.nome_robo})": (r.nome_prova, r.classificacao)
              for r in df_res.itertuples()}

    with editar:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            robos = opcoes_robos()
            prova, clas = chaves[st.selectbox("Resultado", chaves, key="sel_edit_res")]
            r = df_res[(df_res.nome_prova == prova) & (df_res.classificacao == clas)].iloc[0]
            k = f"{prova}_{clas}"
            with st.form("form_editar_resultado"):
                nova_prova = st.text_input("Nome da prova", r.nome_prova, key=f"res_p_{k}")
                nova_clas = st.number_input("Classificação", value=int(r.classificacao), step=1, key=f"res_c_{k}")
                pont = st.number_input("Pontuação (0 a 100)", value=float(r.pontuacao), step=0.5,
                                       format="%.2f", key=f"res_pt_{k}")
                robo = st.selectbox("Robô", robos, chave_de(robos, r.id_robo), key=f"res_r_{k}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE resultado SET nome_prova = %s, classificacao = %s, pontuacao = %s, id_robo = %s
                              WHERE nome_prova = %s AND classificacao = %s""",
                          (nova_prova, int(nova_clas), pont, robos[robo], prova, int(clas)),
                          "Resultado atualizado.")

    with excluir:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            rotulo = st.selectbox("Resultado", chaves, key="sel_del_res")
            prova, clas = chaves[rotulo]
            if st.button("Excluir resultado", type="primary"):
                rodar("DELETE FROM resultado WHERE nome_prova = %s AND classificacao = %s",
                      (prova, int(clas)), f"Resultado '{rotulo}' excluído.")


def pagina_integrantes():
    cabecalho("Integrantes", "Membros das equipes e suas funções", "👤")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        df = consultar("""SELECT i.id_integrante, i.nome_integrante, i.funcao, i.data_nascimento,
                                 TIMESTAMPDIFF(YEAR, i.data_nascimento, CURDATE()) AS idade,
                                 i.email, e.nome_equipe
                            FROM integrante i JOIN equipe e ON e.id_equipe = i.id_equipe
                           ORDER BY e.nome_equipe, i.nome_integrante""")
        tabela(df, hide_index=True, width="stretch",
                     column_config={"data_nascimento": st.column_config.DateColumn("data_nascimento", format="DD/MM/YYYY")})

    with criar:
        equipes = opcoes_equipes()
        with st.form("form_criar_integrante", clear_on_submit=True):
            nome = st.text_input("Nome")
            funcao = st.selectbox("Função", FUNCOES)
            nasc = st.date_input("Data de nascimento", dt.date(2008, 1, 1), DATA_MIN, DATA_MAX, format="DD/MM/YYYY")
            email = st.text_input("E-mail (opcional)")
            equipe = st.selectbox("Equipe", equipes)
            if st.form_submit_button("Cadastrar"):
                if not nome or not equipe:
                    st.warning("Informe o nome e a equipe.")
                else:
                    rodar("""INSERT INTO integrante (nome_integrante, funcao, data_nascimento, email, id_equipe)
                             VALUES (%s, %s, %s, %s, %s)""",
                          (nome, funcao, nasc, email or None, equipes[equipe]), f"Integrante '{nome}' cadastrado.")

    df_int = consultar("SELECT * FROM integrante ORDER BY nome_integrante")
    pessoas = {f"{r.nome_integrante} (id {r.id_integrante})": r.id_integrante for r in df_int.itertuples()}

    with editar:
        if not pessoas:
            st.info("Nenhum integrante cadastrado.")
        else:
            equipes = opcoes_equipes()
            id_i = pessoas[st.selectbox("Integrante", pessoas, key="sel_edit_int")]
            r = df_int[df_int.id_integrante == id_i].iloc[0]
            with st.form("form_editar_integrante"):
                nome = st.text_input("Nome", r.nome_integrante, key=f"i_nome_{id_i}")
                f_idx = FUNCOES.index(r.funcao) if r.funcao in FUNCOES else 0
                funcao = st.selectbox("Função", FUNCOES, f_idx, key=f"i_func_{id_i}")
                nasc = st.date_input("Data de nascimento", r.data_nascimento, DATA_MIN, DATA_MAX,
                                     format="DD/MM/YYYY", key=f"i_nasc_{id_i}")
                email = st.text_input("E-mail", r.email or "", key=f"i_mail_{id_i}")
                equipe = st.selectbox("Equipe", equipes, chave_de(equipes, r.id_equipe), key=f"i_eq_{id_i}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE integrante SET nome_integrante = %s, funcao = %s, data_nascimento = %s,
                                    email = %s, id_equipe = %s
                              WHERE id_integrante = %s""",
                          (nome, funcao, nasc, email or None, equipes[equipe], id_i), "Integrante atualizado.")

    with excluir:
        if not pessoas:
            st.info("Nenhum integrante cadastrado.")
        else:
            rotulo = st.selectbox("Integrante", pessoas, key="sel_del_int")
            if st.button("Excluir integrante", type="primary"):
                rodar("DELETE FROM integrante WHERE id_integrante = %s", (pessoas[rotulo],),
                      f"Integrante '{rotulo}' excluído.")


CONSULTAS = {
    "Desempenho por equipe (JOIN + GROUP BY + SUM/AVG/MAX)":
        "SELECT * FROM vw_desempenho_equipe ORDER BY pontuacao_total DESC",
    "Robôs sem resultado (LEFT JOIN exclusiva)":
        "SELECT * FROM vw_robos_sem_resultado",
    "Idade dos robôs (manipulação de datas)":
        "SELECT * FROM vw_idade_robos ORDER BY idade_dias DESC",
    "Robôs criados por mês (datas + COUNT)":
        "SELECT * FROM vw_robos_por_mes ORDER BY mes",
    "Estatísticas por categoria (MIN/MAX/AVG)":
        "SELECT * FROM vw_estatisticas_categoria",
    "Integrantes e idade média por equipe":
        "SELECT * FROM vw_integrantes_equipe ORDER BY nome_equipe",
}


def pagina_consultas():
    cabecalho("Consultas não triviais", "Views com JOIN, agregações e datas, e a stored procedure", "🔎")
    escolha = st.selectbox("Consulta", CONSULTAS)
    sql = CONSULTAS[escolha]
    view = sql.split("FROM ")[1].split()[0]
    definicao = consultar("""SELECT VIEW_DEFINITION FROM information_schema.VIEWS
                              WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s""", (view,))
    tabela(consultar(sql), hide_index=True, width="stretch")
    if not definicao.empty:
        with st.expander("Ver o SQL da view"):
            st.code(definicao.iloc[0, 0], language="sql")

    st.divider()
    st.subheader("Stored procedure: ranking de uma prova")
    st.code("CALL sp_ranking_prova('<nome da prova>');", language="sql")
    provas = consultar("SELECT DISTINCT nome_prova FROM resultado ORDER BY nome_prova").nome_prova.tolist()
    if provas:
        prova = st.selectbox("Prova", provas)
        tabela(chamar_procedure("sp_ranking_prova", (prova,)), hide_index=True, width="stretch")


def pagina_dashboard():
    busca = barra_superior("dashboard")
    st.markdown("""<div class="dashboard-intro">
      <div class="eyebrow">👋 Olá, somos o Grupo 04!</div>
      <h1>Dashboard do torneio</h1>
      <p>A leitura começa pela liderança, passa pela distribuição dos robôs e termina na consistência das pontuações por prova.</p>
    </div>""", unsafe_allow_html=True)

    res = consultar("""SELECT r.nome_prova, r.classificacao, r.pontuacao,
                            ro.categoria, ro.nome_robo, ro.data_criacao,
                            e.nome_equipe, e.cidade
                       FROM resultado r
                       JOIN robo ro  ON ro.id_robo  = r.id_robo
                       JOIN equipe e ON e.id_equipe = ro.id_equipe""")
    todos_robos = consultar("""SELECT ro.nome_robo, ro.categoria, ro.data_criacao,
                                    e.nome_equipe, e.cidade
                               FROM robo ro JOIN equipe e ON e.id_equipe = ro.id_equipe""")

    filtros = st.columns([1.15, 1.15, 1.15, 1.15])
    with filtros[0]:
        periodo = st.selectbox("Período", ["Todos os dados", "Ano de 2025", "Ano de 2026"], key="dashboard_periodo")
    with filtros[1]:
        provas = ["Todas"] + sorted(res.nome_prova.dropna().unique().tolist()) if not res.empty else ["Todas"]
        filtro_prova = st.selectbox("Prova", provas, key="dashboard_prova")
    with filtros[2]:
        categorias = ["Todas"] + sorted(todos_robos.categoria.dropna().unique().tolist()) if not todos_robos.empty else ["Todas"]
        filtro_categoria = st.selectbox("Categoria", categorias, key="dashboard_categoria")
    with filtros[3]:
        cidades = ["Todas"] + sorted(todos_robos.cidade.dropna().unique().tolist()) if not todos_robos.empty else ["Todas"]
        filtro_cidade = st.selectbox("Cidade", cidades, key="dashboard_cidade")

    if periodo != "Todos os dados":
        ano = periodo[-4:]
        res = res[res.data_criacao.astype(str).str[:4] == ano]
        todos_robos = todos_robos[todos_robos.data_criacao.astype(str).str[:4] == ano]
    if filtro_prova != "Todas":
        res = res[res.nome_prova == filtro_prova]
    if filtro_categoria != "Todas":
        res = res[res.categoria == filtro_categoria]
        todos_robos = todos_robos[todos_robos.categoria == filtro_categoria]
    if filtro_cidade != "Todas":
        res = res[res.cidade == filtro_cidade]
        todos_robos = todos_robos[todos_robos.cidade == filtro_cidade]
    if busca:
        termo = busca.lower()
        colunas_busca = ["nome_prova", "nome_robo", "nome_equipe", "categoria", "cidade"]
        mascara = res[colunas_busca].fillna("").astype(str).apply(lambda coluna: coluna.str.lower().str.contains(termo, regex=False)).any(axis=1)
        res = res[mascara]
        mascara_robos = todos_robos[["nome_robo", "nome_equipe", "categoria", "cidade"]].fillna("").astype(str).apply(lambda coluna: coluna.str.lower().str.contains(termo, regex=False)).any(axis=1)
        todos_robos = todos_robos[mascara_robos]

    if res.empty:
        st.info("Nenhum resultado corresponde aos filtros atuais. Tente ampliar o período ou remover algum filtro.")
    lider = None
    if not res.empty:
        ranking = (res.groupby(["nome_equipe", "cidade"], as_index=False)
                     .agg(qtd_participacoes=("nome_prova", "count"),
                          pontuacao_total=("pontuacao", "sum"),
                          pontuacao_media=("pontuacao", "mean"),
                          melhor_pontuacao=("pontuacao", "max"))
                     .sort_values("pontuacao_total", ascending=False))
        lider = ranking.iloc[0]
    else:
        ranking = res

    cards = st.columns(5)
    cards[0].metric("Equipes com resultado", int(ranking.nome_equipe.nunique()) if not ranking.empty else 0)
    cards[1].metric("Robôs avaliados", int(res.nome_robo.nunique()) if not res.empty else 0)
    cards[2].metric("Provas", int(res.nome_prova.nunique()) if not res.empty else 0)
    cards[3].metric("Média geral", f"{res.pontuacao.mean():.2f}" if not res.empty else "-")
    with cards[4]:
        nome_lider = lider.nome_equipe if lider is not None else "-"
        st.markdown(
            f'<div class="leader-card"><div class="leader-label">Líder atual</div>'
            f'<div class="leader-name">{nome_lider}</div></div>',
            unsafe_allow_html=True,
        )

    bloco_historia("01 · Liderança", "Quem está liderando?",
                    "Somamos as pontuações dos resultados filtrados. A equipe no topo é a referência para a próxima leitura.")
    if not ranking.empty:
        c1, c2 = st.columns([1.45, 1])
        with c1:
            fig = px.bar(ranking.sort_values("pontuacao_total"), x="pontuacao_total", y="nome_equipe",
                         orientation="h", title="Pontuação total por equipe", labels={"pontuacao_total": "Pontos", "nome_equipe": ""},
                         color="pontuacao_total", color_continuous_scale=ESCALA,
                         custom_data=["cidade", "qtd_participacoes", "pontuacao_media", "melhor_pontuacao"])
            fig.update_coloraxes(showscale=False)
            fig.update_traces(marker_line_width=0, hovertemplate="<b>%{y}</b><br>%{x:.1f} pontos<extra>Clique para detalhes</extra>")
            evento = grafico(fig)
            pontos = pontos_selecionados(evento)
            if pontos:
                p = pontos[0]
                d = p.get("customdata", [])
                st.info(f"**{p.get('y', 'Equipe')}** · {d[0]} · {int(d[1])} participação(ões) · média {float(d[2]):.2f} · melhor {float(d[3]):.2f} pontos.")
        with c2:
            cat = todos_robos.groupby("categoria", as_index=False).size().rename(columns={"size": "qtd"}) if not todos_robos.empty else res.groupby("categoria", as_index=False).size().rename(columns={"size": "qtd"})
            if not cat.empty:
                fig = px.pie(cat, names="categoria", values="qtd", hole=.58, title="Robôs por categoria", color_discrete_sequence=PALETA)
                fig.update_traces(marker=dict(line=dict(color="#0F172A", width=3)), hovertemplate="<b>%{label}</b><br>%{value} robô(s)<extra>Clique para detalhes</extra>")
                evento = grafico(fig)
                pontos = pontos_selecionados(evento)
                if pontos:
                    p = pontos[0]
                    st.info(f"Categoria **{p.get('label', 'selecionada')}**: {p.get('value', 0)} robô(s).")

    bloco_historia("02 · Alcance", "Onde o torneio está acontecendo?",
                    "A comparação entre cidades mostra a distribuição das equipes e dos robôs que sustentam a competição.")
    cid = (todos_robos.groupby("cidade", as_index=False)
           .agg(robos=("nome_robo", "count"), equipes=("nome_equipe", "nunique"))
           .sort_values("robos", ascending=False)) if not todos_robos.empty else res.groupby("cidade", as_index=False).agg(robos=("nome_robo", "count"), equipes=("nome_equipe", "nunique"))
    if not cid.empty:
        fig = px.bar(cid, x="cidade", y=["equipes", "robos"], barmode="group", title="Equipes e robôs por cidade",
                     labels={"cidade": "", "value": "Quantidade", "variable": ""}, color_discrete_sequence=["#68C9C3", "#F4B46A"])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(bargap=.25)
        grafico(fig)

    bloco_historia("03 · Consistência", "Em quais provas o desempenho se sustenta?",
                    "A média indica o desempenho típico; a distribuição revela se os resultados são consistentes ou dependem de poucos picos.")
    if not res.empty:
        c3, c4 = st.columns(2)
        with c3:
            fig = px.box(res, x="nome_prova", y="pontuacao", points="all", hover_data=["nome_robo", "nome_equipe"],
                         title="Distribuição das pontuações por prova", labels={"nome_prova": "", "pontuacao": "Pontuação"},
                         color_discrete_sequence=[PALETA[0]])
            fig.update_traces(fillcolor="rgba(139,124,246,.16)", line=dict(width=1.5), marker=dict(size=6, opacity=.85))
            grafico(fig)
        with c4:
            est = (res.groupby("categoria", as_index=False)
                   .agg(menor_pontuacao=("pontuacao", "min"), media_pontuacao=("pontuacao", "mean"), maior_pontuacao=("pontuacao", "max")))
            fig = px.bar(est, x="categoria", y=["menor_pontuacao", "media_pontuacao", "maior_pontuacao"], barmode="group",
                         title="Pontuação por categoria", labels={"categoria": "", "value": "Pontuação", "variable": ""}, color_discrete_sequence=SEQ3)
            fig.update_traces(marker_line_width=0)
            fig.update_layout(bargap=.25)
            grafico(fig)

        bloco_historia("04 · Detalhamento", "Quais registros formam o resultado?",
                        "A tabela abaixo liga prova, robô, equipe e classificação para facilitar a conferência antes da apresentação.")
        tabela(res.sort_values(["nome_prova", "classificacao"])[["nome_prova", "classificacao", "pontuacao", "nome_robo", "categoria", "nome_equipe", "cidade"]].head(12), hide_index=True, width="stretch")


def pagina_integridade():
    cabecalho("Integridade referencial e trigger", "Chaves estrangeiras, cascata e trigger de validação", "⚡")

    st.subheader("1. Violação de chave estrangeira")
    st.write("Tenta cadastrar um robô ligado a uma equipe que não existe.")
    id_falso = st.number_input("ID da equipe", value=999, step=1)
    if st.button("Inserir robô com esse ID de equipe"):
        rodar("INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES (%s, %s, %s, %s)",
              ("Robô Teste FK", "Sumô", dt.date.today(), int(id_falso)),
              f"Robô inserido (a equipe {int(id_falso)} existe).")

    st.subheader("2. Atualização e remoção em cascata")
    st.write("Use as abas **Editar** (alterando o ID) e **Excluir** da página **Equipes**. "
             "O sistema mostra antes quantos registros dependentes serão afetados.")

    st.subheader("3. Trigger de validação de resultados")
    trig = consultar("""SELECT TRIGGER_NAME, EVENT_MANIPULATION AS evento, ACTION_TIMING AS momento,
                               EVENT_OBJECT_TABLE AS tabela
                          FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE()""")
    tabela(trig, hide_index=True, width="stretch")
    st.write("Regras: pontuação entre 0 e 100, classificação 1 ou maior "
             "e robô com data de criação futura não pode ter resultado.")
    robos = opcoes_robos()
    with st.form("form_trigger"):
        prova = st.text_input("Prova", "Teste Trigger")
        clas = st.number_input("Classificação", value=1, step=1)
        pont = st.number_input("Pontuação", value=150.0, step=0.5, format="%.2f")
        robo = st.selectbox("Robô", robos)
        if st.form_submit_button("Inserir resultado"):
            rodar("INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES (%s, %s, %s, %s)",
                  (prova, int(clas), pont, robos[robo]), "Resultado aceito pela trigger.")


# ---------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------

PAGINAS = {
    "Início": pagina_inicio,
    "Equipes": pagina_equipes,
    "Robôs": pagina_robos,
    "Resultados": pagina_resultados,
    "Integrantes": pagina_integrantes,
    "Consultas": pagina_consultas,
    "Dashboard": pagina_dashboard,
    "Integridade e Trigger": pagina_integridade,
}

ICONES = {
    "Início": "🏠", "Equipes": "👥", "Robôs": "🤖", "Resultados": "🏆",
    "Integrantes": "👤", "Consultas": "🔎", "Dashboard": "📊", "Integridade e Trigger": "⚡",
}

st.markdown("""<style>
[data-testid="stSidebar"] .stButton button { border-radius:10px; border-color:var(--border); background:transparent; color:var(--muted); }
[data-testid="stSidebar"] .stButton button:hover { border-color:var(--accent-light); color:var(--text); background:rgba(139,124,246,.10); }
[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] { background:rgba(139,124,246,.18); color:var(--text); border-color:var(--border-strong); box-shadow:inset 3px 0 0 var(--accent-light); }
[data-testid="stSidebar"][data-collapsed="true"] {
  display:block!important; visibility:visible!important; opacity:1!important;
  width:300px!important; min-width:300px!important; max-width:300px!important;
  transform:none!important;
}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarContent"] {
  display:block!important; visibility:visible!important; opacity:1!important;
}
[data-testid="stSidebar"][data-collapsed="true"] + * { margin-left:0!important; }
[data-testid="stSidebarCollapseButton"] { display:none!important; }
[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] { display:none!important; }
[data-testid="stSidebar"] .stButton button[aria-label="Alternar tema"] { width:2.55rem; min-width:2.55rem; padding:.35rem; font-size:1.15rem; }
</style>""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="brand"><div class="brand-logo">🤖</div><div>'
    '<div class="brand-title">Torneio de Robótica</div>'
    '<div class="brand-sub">Painel de gestão</div></div></div>',
    unsafe_allow_html=True,
)
def alternar_tema():
    st.session_state.tema = "Escuro" if st.session_state.tema == "Claro" else "Claro"


def selecionar_pagina(pagina):
    st.session_state.pagina_menu = pagina


if "pagina_menu" not in st.session_state:
    st.session_state.pagina_menu = "Início"
for pagina in PAGINAS:
    rotulo = f"{ICONES[pagina]}  {pagina}"
    st.sidebar.button(rotulo, key=f"menu_{pagina.lower().replace(' ', '_')}",
                      type="primary" if st.session_state.pagina_menu == pagina else "secondary",
                      on_click=selecionar_pagina, args=(pagina,), use_container_width=True)
escolha = st.session_state.pagina_menu
st.session_state.pagina_atual = escolha

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

try:
    PAGINAS[escolha]()
except mysql.connector.Error as e:
    if e.errno == 1045:
        st.error("A conexão foi recusada por usuário ou senha (MySQL 1045). Defina a senha correta em DB_PASSWORD; nenhum volume foi alterado.")
    elif e.errno == 2003:
        st.error("Não foi possível alcançar o MySQL. Confirme se o container está ativo e se DB_HOST=127.0.0.1 e DB_PORT=3307 apontam para a porta publicada.")
    elif e.errno == 1049:
        st.error("O banco torneio_robotica não existe nessa instância. O script principal pode recriar o banco; faça backup e confirme antes de executá-lo.")
    elif e.errno == 1146:
        st.error("Uma ou mais tabelas esperadas não existem no banco torneio_robotica. Verifique o schema antes de carregar o script principal, que recria o banco.")
    else:
        st.error("Não foi possível acessar o banco de dados. Confira a conexão e o schema local.")
    st.code(str(e))
