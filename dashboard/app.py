import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import locale

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="E-commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ──────────────────────────────────────────────
# COLOR PALETTE
# ──────────────────────────────────────────────
COLORS = {
    "primary": "#6C5CE7",
    "secondary": "#00CEC9",
    "accent": "#FD79A8",
    "success": "#00B894",
    "danger": "#E17055",
    "warning": "#FDCB6E",
    "dark": "#2D3436",
    "light": "#DFE6E9",
    "bg_card": "rgba(45,52,54,0.6)",
}

PLOTLY_PALETTE = [
    "#6C5CE7", "#00CEC9", "#FD79A8", "#FDCB6E",
    "#00B894", "#E17055", "#74B9FF", "#A29BFE",
    "#55EFC4", "#FF7675",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#DFE6E9"),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=PLOTLY_PALETTE,
    xaxis=dict(gridcolor="rgba(223,230,233,0.1)"),
    yaxis=dict(gridcolor="rgba(223,230,233,0.1)"),
)


# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ---- Global ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0c0c1d 0%, #1a1a2e 40%, #16213e 100%);
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #111128 50%, #0d0d20 100%);
    border-right: 1px solid rgba(108,92,231,0.15);
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Hide default radio buttons entirely */
section[data-testid="stSidebar"] .stRadio {
    display: none !important;
}

/* ---- Sidebar nav button styling ---- */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    border: none;
    border-radius: 12px;
    color: #8B8BA7;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    padding: 14px 18px;
    text-align: left;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 12px;
    letter-spacing: 0.01em;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(108, 92, 231, 0.08);
    color: #C8C8E0;
    transform: translateX(4px);
    border: none;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none;
    border: none;
    outline: none;
}
section[data-testid="stSidebar"] .stButton > button:active {
    background: rgba(108, 92, 231, 0.12);
    border: none;
}

/* ---- KPI cards ---- */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(108,92,231,0.15) 0%, rgba(0,206,201,0.10) 100%);
    border: 1px solid rgba(108,92,231,0.25);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(108,92,231,0.3);
}
div[data-testid="stMetric"] label {
    color: #A29BFE !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ---- Section titles ---- */
h1 { color: #FFFFFF !important; font-weight: 800 !important; }
h2 { color: #DFE6E9 !important; font-weight: 700 !important; }
h3 { color: #A29BFE !important; font-weight: 600 !important; }

/* ---- Dataframe ---- */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* ---- Divider ---- */
hr { border-color: rgba(108,92,231,0.2) !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATABASE HELPER
# ──────────────────────────────────────────────
@st.cache_resource
def get_connection():
    """Return a reusable psycopg2 connection."""
    url = os.getenv("POSTGRES_URL", "")
    if not url:
        return None
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        st.error(f"❌ Falha na conexão com o banco: {e}")
        return None


def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL and return a DataFrame. Reconnects on stale connection."""
    conn = get_connection()
    if conn is None:
        st.error("⚠️ Sem conexão com o banco de dados. Verifique as credenciais no .env")
        return pd.DataFrame()
    try:
        return pd.read_sql(sql, conn)
    except Exception as e:
        # Connection might be stale – clear cache and retry once
        st.cache_resource.clear()
        conn = get_connection()
        if conn is None:
            st.error(f"⚠️ Erro ao executar query: {e}")
            return pd.DataFrame()
        try:
            return pd.read_sql(sql, conn)
        except Exception as e2:
            st.error(f"⚠️ Erro ao executar query: {e2}")
            return pd.DataFrame()


# ──────────────────────────────────────────────
# FORMATTING HELPERS
# ──────────────────────────────────────────────
def fmt_brl(value: float) -> str:
    """Format number as Brazilian Real currency."""
    if pd.isna(value):
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(value) -> str:
    """Format integer with dot thousands separator."""
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def fmt_pct(value: float) -> str:
    """Format percentage with sign."""
    if pd.isna(value):
        return "0,0%"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")


def apply_plotly_style(fig):
    """Apply consistent dark theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ──────────────────────────────────────────────
# SVG ICONS (inline, lightweight)
# ──────────────────────────────────────────────
SVG_LOGO = """
<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#6C5CE7"/>
      <stop offset="100%" stop-color="#00CEC9"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="44" height="44" rx="12" fill="url(#logoGrad)" opacity="0.15"/>
  <rect x="2" y="2" width="44" height="44" rx="12" stroke="url(#logoGrad)" stroke-width="1.5" fill="none"/>
  <rect x="10" y="28" width="6" height="12" rx="2" fill="#00CEC9"/>
  <rect x="21" y="20" width="6" height="20" rx="2" fill="#6C5CE7"/>
  <rect x="32" y="12" width="6" height="28" rx="2" fill="#A29BFE"/>
  <circle cx="13" cy="16" r="2.5" fill="#00CEC9" opacity="0.8"/>
  <circle cx="24" cy="11" r="2.5" fill="#6C5CE7" opacity="0.8"/>
  <circle cx="35" cy="8" r="2.5" fill="#A29BFE" opacity="0.8"/>
  <line x1="13" y1="16" x2="24" y2="11" stroke="#6C5CE7" stroke-width="1.2" opacity="0.5"/>
  <line x1="24" y1="11" x2="35" y2="8" stroke="#A29BFE" stroke-width="1.2" opacity="0.5"/>
</svg>
"""

ICON_VENDAS = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>"""

ICON_CLIENTES = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>"""

ICON_PRICING = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>"""


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
NAV_ITEMS = [
    {"key": "Vendas", "label": "Vendas", "icon": ICON_VENDAS},
    {"key": "Clientes", "label": "Clientes", "icon": ICON_CLIENTES},
    {"key": "Pricing", "label": "Pricing", "icon": ICON_PRICING},
]

# Initialise page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Vendas"

with st.sidebar:
    # ── Logo area ──
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem 1.5rem 1.5rem;
    ">
        <div style="display:inline-block;">{SVG_LOGO}</div>
        <h1 style="
            font-size: 1.25rem;
            margin: 0.75rem 0 0;
            background: linear-gradient(135deg, #6C5CE7 0%, #00CEC9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -0.02em;
        ">E-commerce Analytics</h1>
        <p style="
            color: #5A5A7A;
            font-size: 0.72rem;
            margin-top: 6px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        ">Dashboard Executivo</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Separator ──
    st.markdown("""
    <div style="
        margin: 0.25rem 1.5rem 1rem;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(108,92,231,0.3) 50%, transparent 100%);
    "></div>
    """, unsafe_allow_html=True)

    # ── Navigation label ──
    st.markdown("""
    <p style="
        color: #4A4A6A;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 0 1.2rem;
        margin-bottom: 0.5rem;
    ">Menu Principal</p>
    """, unsafe_allow_html=True)

    # ── Navigation buttons ──
    for item in NAV_ITEMS:
        is_active = st.session_state.current_page == item["key"]

        # Active item gets special inline style injected via markdown before the button
        if is_active:
            st.markdown(f"""
            <style>
                /* Active state for {item["key"]} */
                section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div:has(> div > button[kind="secondary"]):has(button:contains("{item["label"]}")) button {{
                    background: linear-gradient(135deg, rgba(108,92,231,0.18) 0%, rgba(0,206,201,0.10) 100%) !important;
                    color: #FFFFFF !important;
                    font-weight: 600 !important;
                    border-left: 3px solid #6C5CE7 !important;
                    border-radius: 0 12px 12px 0 !important;
                }}
            </style>
            """, unsafe_allow_html=True)

        # Render the button with icon + label
        icon_color = "#FFFFFF" if is_active else "#8B8BA7"
        colored_icon = item["icon"].replace('stroke="currentColor"', f'stroke="{icon_color}"')

        # Use a container to render icon alongside button text
        btn_label = f"{item['label']}"
        if st.button(
            btn_label,
            key=f"nav_{item['key']}",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.current_page = item["key"]
            st.rerun()

    # ── Bottom separator ──
    st.markdown("""
    <div style="
        margin: 1.5rem 1.5rem 1rem;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(108,92,231,0.2) 50%, transparent 100%);
    "></div>
    """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("""
    <div style="
        padding: 0 1.2rem;
        margin-top: 0.5rem;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 14px;
            background: rgba(108,92,231,0.06);
            border-radius: 10px;
            border: 1px solid rgba(108,92,231,0.1);
        ">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5A5A7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
            <span style="
                color: #5A5A7A;
                font-size: 0.7rem;
                font-weight: 500;
            ">Supabase · Gold Layer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Get current page
page = st.session_state.current_page


# ══════════════════════════════════════════════
# PAGE 1: VENDAS
# ══════════════════════════════════════════════
if page == "Vendas":
    st.markdown("## 📈 Vendas — Diretor Comercial")

    # Load data
    df_vendas = run_query("SELECT * FROM public_gold_sales.vendas_temporais")

    if df_vendas.empty:
        st.warning("Nenhum dado de vendas encontrado.")
        st.stop()

    # ── Month filter ──
    meses_disponiveis = sorted(df_vendas["mes_venda"].unique())
    mes_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    opcoes_mes = ["Todos os meses"] + [f"{mes_nomes.get(m, m)} ({m})" for m in meses_disponiveis]
    sel_mes = st.selectbox("Filtrar por mês", opcoes_mes, key="vendas_mes")

    if sel_mes != "Todos os meses":
        mes_num = meses_disponiveis[opcoes_mes.index(sel_mes) - 1]
        df_vendas = df_vendas[df_vendas["mes_venda"] == mes_num]

    # ── KPIs ──
    receita_total = df_vendas["receita_total"].sum()
    total_vendas = df_vendas["total_vendas"].sum()
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    clientes_unicos = df_vendas.groupby("data_venda")["total_clientes_unicos"].max().sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Receita Total", fmt_brl(receita_total))
    k2.metric("Total de Vendas", fmt_int(total_vendas))
    k3.metric("Ticket Médio", fmt_brl(ticket_medio))
    k4.metric("Clientes Únicos", fmt_int(clientes_unicos))

    st.markdown("---")

    # ── Chart 1: Receita Diária (line) ──
    df_diaria = (
        df_vendas.groupby("data_venda", as_index=False)["receita_total"]
        .sum()
        .sort_values("data_venda")
    )
    fig1 = px.line(
        df_diaria, x="data_venda", y="receita_total",
        title="Receita Diária",
        labels={"data_venda": "Data", "receita_total": "Receita (R$)"},
    )
    fig1.update_traces(
        line=dict(width=3, color=COLORS["primary"]),
        fill="tozeroy",
        fillcolor="rgba(108,92,231,0.12)",
    )
    apply_plotly_style(fig1)
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)

    # ── Chart 2: Receita por Dia da Semana (bar) ──
    dia_order = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    df_dia_semana = (
        df_vendas.groupby("dia_semana_nome", as_index=False)["receita_total"]
        .sum()
    )
    df_dia_semana["dia_semana_nome"] = pd.Categorical(
        df_dia_semana["dia_semana_nome"], categories=dia_order, ordered=True
    )
    df_dia_semana = df_dia_semana.sort_values("dia_semana_nome")

    fig2 = px.bar(
        df_dia_semana, x="dia_semana_nome", y="receita_total",
        title="Receita por Dia da Semana",
        labels={"dia_semana_nome": "Dia", "receita_total": "Receita (R$)"},
        color_discrete_sequence=[COLORS["secondary"]],
    )
    apply_plotly_style(fig2)
    c1.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Vendas por Hora (bar) ──
    df_hora = (
        df_vendas.groupby("hora_venda", as_index=False)["total_vendas"]
        .sum()
        .sort_values("hora_venda")
    )
    fig3 = px.bar(
        df_hora, x="hora_venda", y="total_vendas",
        title="Volume de Vendas por Hora",
        labels={"hora_venda": "Hora", "total_vendas": "Total Vendas"},
        color_discrete_sequence=[COLORS["accent"]],
    )
    apply_plotly_style(fig3)
    c2.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 2: CLIENTES
# ══════════════════════════════════════════════
elif page == "Clientes":
    st.markdown("## 👥 Clientes — Diretora de Customer Success")

    df_clientes = run_query("SELECT * FROM public_gold.clientes_segmentacao")

    if df_clientes.empty:
        st.warning("Nenhum dado de clientes encontrado.")
        st.stop()

    # ── KPIs (always from full dataset) ──
    total_clientes = len(df_clientes)
    clientes_vip = len(df_clientes[df_clientes["segmento_cliente"] == "VIP"])
    receita_vip = df_clientes.loc[df_clientes["segmento_cliente"] == "VIP", "receita_total"].sum()
    ticket_medio_geral = df_clientes["ticket_medio"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Clientes", fmt_int(total_clientes))
    k2.metric("Clientes VIP", fmt_int(clientes_vip))
    k3.metric("Receita VIP", fmt_brl(receita_vip))
    k4.metric("Ticket Médio Geral", fmt_brl(ticket_medio_geral))

    st.markdown("---")

    c1, c2 = st.columns(2)

    # ── Chart 1: Distribuição por Segmento (pie/donut) ──
    df_seg_count = df_clientes.groupby("segmento_cliente", as_index=False).size()
    df_seg_count.columns = ["segmento_cliente", "total"]
    fig1 = px.pie(
        df_seg_count, names="segmento_cliente", values="total",
        title="Distribuição de Clientes por Segmento",
        hole=0.45,
        color_discrete_sequence=PLOTLY_PALETTE,
    )
    apply_plotly_style(fig1)
    c1.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Receita por Segmento (bar) ──
    df_seg_receita = (
        df_clientes.groupby("segmento_cliente", as_index=False)["receita_total"].sum()
    )
    fig2 = px.bar(
        df_seg_receita, x="segmento_cliente", y="receita_total",
        title="Receita por Segmento",
        labels={"segmento_cliente": "Segmento", "receita_total": "Receita (R$)"},
        color="segmento_cliente",
        color_discrete_sequence=PLOTLY_PALETTE,
    )
    apply_plotly_style(fig2)
    fig2.update_layout(showlegend=False)
    c2.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    # ── Chart 3: Top 10 Clientes por Receita (horizontal bar) ──
    df_top10 = df_clientes.nsmallest(10, "ranking_receita")
    fig3 = px.bar(
        df_top10.sort_values("receita_total"),
        y="nome_cliente", x="receita_total",
        title="Top 10 Clientes",
        labels={"nome_cliente": "Cliente", "receita_total": "Receita (R$)"},
        orientation="h",
        color_discrete_sequence=[COLORS["primary"]],
    )
    apply_plotly_style(fig3)
    c3.plotly_chart(fig3, use_container_width=True)

    # ── Chart 4: Clientes por Estado (bar) ──
    df_estado = (
        df_clientes.groupby("estado", as_index=False)
        .size()
        .rename(columns={"size": "total"})
        .sort_values("total", ascending=False)
    )
    fig4 = px.bar(
        df_estado, x="estado", y="total",
        title="Clientes por Estado",
        labels={"estado": "UF", "total": "Clientes"},
        color_discrete_sequence=[COLORS["secondary"]],
    )
    apply_plotly_style(fig4)
    c4.plotly_chart(fig4, use_container_width=True)

    # ── Detail Table ──
    st.markdown("---")
    st.markdown("### 📋 Tabela Detalhada de Clientes")
    seg_options = ["Todos"] + sorted(df_clientes["segmento_cliente"].unique().tolist())
    seg_filter = st.selectbox("Filtrar por segmento", seg_options, key="cli_seg")
    if seg_filter != "Todos":
        df_show = df_clientes[df_clientes["segmento_cliente"] == seg_filter]
    else:
        df_show = df_clientes
    st.dataframe(df_show.reset_index(drop=True), use_container_width=True, height=400)


# ══════════════════════════════════════════════
# PAGE 3: PRICING
# ══════════════════════════════════════════════
elif page == "Pricing":
    st.markdown("## 💲 Pricing — Diretor de Pricing")

    df_pricing = run_query("SELECT * FROM public_gold.precos_competitividade")

    if df_pricing.empty:
        st.warning("Nenhum dado de pricing encontrado.")
        st.stop()

    # ── Category filter ──
    categorias = sorted(df_pricing["categoria"].unique().tolist())
    sel_categorias = st.multiselect("Filtrar por categoria", categorias, default=categorias, key="pricing_cat")
    if sel_categorias:
        df_pricing = df_pricing[df_pricing["categoria"].isin(sel_categorias)]

    # ── KPIs ──
    total_produtos = len(df_pricing)
    mais_caros = len(df_pricing[df_pricing["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"])
    mais_baratos = len(df_pricing[df_pricing["classificacao_preco"] == "MAIS_BARATO_QUE_TODOS"])
    dif_media = df_pricing["diferenca_percentual_vs_media"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Produtos Monitorados", fmt_int(total_produtos))
    k2.metric("Mais Caros que Todos", fmt_int(mais_caros))
    k3.metric("Mais Baratos que Todos", fmt_int(mais_baratos))
    k4.metric("Dif. Média vs Mercado", fmt_pct(dif_media))

    st.markdown("---")

    c1, c2 = st.columns(2)

    # ── Chart 1: Distribuição por Classificação (pie) ──
    df_class_count = (
        df_pricing.groupby("classificacao_preco", as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
    fig1 = px.pie(
        df_class_count, names="classificacao_preco", values="total",
        title="Posicionamento de Preço vs Concorrência",
        hole=0.45,
        color_discrete_sequence=PLOTLY_PALETTE,
    )
    apply_plotly_style(fig1)
    c1.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Diferença % Média por Categoria (bar, verde/vermelho) ──
    df_cat_dif = (
        df_pricing.groupby("categoria", as_index=False)["diferenca_percentual_vs_media"]
        .mean()
        .sort_values("diferenca_percentual_vs_media", ascending=False)
    )
    df_cat_dif["cor"] = df_cat_dif["diferenca_percentual_vs_media"].apply(
        lambda v: COLORS["danger"] if v > 0 else COLORS["success"]
    )
    fig2 = go.Figure(
        go.Bar(
            x=df_cat_dif["categoria"],
            y=df_cat_dif["diferenca_percentual_vs_media"],
            marker_color=df_cat_dif["cor"],
        )
    )
    fig2.update_layout(title="Competitividade por Categoria",
                       xaxis_title="Categoria", yaxis_title="Dif. % vs Média")
    apply_plotly_style(fig2)
    c2.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Scatter – Preço vs Volume ──
    fig3 = px.scatter(
        df_pricing,
        x="diferenca_percentual_vs_media",
        y="quantidade_total",
        color="classificacao_preco",
        size="receita_total",
        size_max=40,
        title="Competitividade × Volume de Vendas",
        labels={
            "diferenca_percentual_vs_media": "Dif. % vs Média",
            "quantidade_total": "Quantidade Vendida",
            "classificacao_preco": "Classificação",
            "receita_total": "Receita",
        },
        color_discrete_sequence=PLOTLY_PALETTE,
        hover_data=["nome_produto", "categoria"],
    )
    apply_plotly_style(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Alert table ──
    st.markdown("---")
    st.markdown("### 🚨 Produtos em Alerta (mais caros que todos os concorrentes)")
    df_alerta = df_pricing[df_pricing["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"][
        [
            "produto_id", "nome_produto", "categoria",
            "nosso_preco", "preco_maximo_concorrentes",
            "diferenca_percentual_vs_media",
        ]
    ].sort_values("diferenca_percentual_vs_media", ascending=False)

    if df_alerta.empty:
        st.success("✅ Nenhum produto mais caro que todos os concorrentes nesta seleção.")
    else:
        st.dataframe(df_alerta.reset_index(drop=True), use_container_width=True, height=350)
