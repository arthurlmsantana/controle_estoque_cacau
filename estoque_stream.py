import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------------------------
# HEADER
# ---------------------------
st.title("📦 Dashboard de Estoque de Cacau")
st.subheader(":necktie: Portfólio - Arthur Lima Machado de Santana")
st.caption("LinkedIn: https://www.linkedin.com/in/arthur-santana-68167994/")

# ---------------------------
# LOAD DATA
# ---------------------------
df = pd.read_csv("estoque_cacau.csv")
df["data"] = pd.to_datetime(df["data"])

# ---------------------------
# FILTROS
# ---------------------------
st.sidebar.header("Filtros")

# Datas
min_data = df["data"].min().to_pydatetime()
max_data = df["data"].max().to_pydatetime()

periodo = st.sidebar.slider(
    "📅 Período",
    min_value=min_data,
    max_value=max_data,
    value=(min_data, max_data),
    format="DD/MM/YYYY"
)

data_inicio, data_fim = periodo
data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

# Depósitos
depositos = st.sidebar.multiselect(
    "🏭 Depósitos",
    options=df["deposito"].unique(),
    default=df["deposito"].unique()
)

# ✅ SKU
skus = st.sidebar.multiselect(
    "🌱 Tipo de Cacau (SKU)",
    options=df["sku"].unique(),
    default=df["sku"].unique()
)

# ---------------------------
# FILTRAR DADOS
# ---------------------------
df_filtrado = df[
    (df["deposito"].isin(depositos)) &
    (df["sku"].isin(skus)) &
    (df["data"] >= data_inicio) &
    (df["data"] <= data_fim)
]

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

# indicadores
entrada_total = df_filtrado["entrada"].sum()
saida_total = df_filtrado["saida"].sum()
estoque_total = entrada_total - saida_total
umidade_media = df_filtrado["umidade_entrada"].mean()

col1.metric("📦 Estoque Atual", f"{estoque_total:,.0f}")
col2.metric("⬆️ Entradas", f"{entrada_total:,.0f}")
col3.metric("⬇️ Saídas", f"{saida_total:,.0f}")
col4.metric("🌡️ Umidade Média", f"{umidade_media:.2f}%")

# ---------------------------
# ABA PRINCIPAL
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📈 Estoque", "🌱 Mix SKU", "🌡️ Qualidade"])

# ---------------------------
# TAB 1 - ESTOQUE
# ---------------------------
with tab1:
    st.subheader("📈 Evolução do Estoque")

    df_filtrado["movimento"] = df_filtrado["entrada"] - df_filtrado["saida"]

    df_estoque = (
    df_filtrado
    .groupby(["deposito", "data"])["movimento"]
    .sum()
    .groupby(level=0)
    .cumsum()
    .reset_index(name="estoque_calculado")
    )

    fig = px.line(
        df_estoque,
        x="data",
        y="estoque_calculado",
        color="deposito",
        title="Estoque por Depósito"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # TABELA DETALHADA POR DIA E SKU
    # ---------------------------
    st.subheader("📊 Entradas e Saídas por Dia e Tipo de Cacau")

    df_mov_dia = (
        df_filtrado
        .groupby(["data", "sku"])[["entrada", "saida"]]
        .sum()
        .reset_index()
        .sort_values(by="data", ascending=False)
    )

    df_mov_dia["data_formatada"] = df_mov_dia["data"].dt.strftime("%d/%m/%Y")

    
    st.dataframe(
        df_mov_dia[["data_formatada", "sku", "entrada", "saida"]],
        use_container_width=True
    )


# ---------------------------
# TAB 2 - SKU
# ---------------------------
with tab2:
    st.subheader("🌱 Distribuição por Tipo de Cacau")

    df_mix = df_filtrado.groupby("sku")["estoque"].sum().reset_index()

    fig2 = px.pie(
        df_mix,
        names="sku",
        values="estoque",
        title="Participação no Estoque",
        hole = 0.4
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Evolução por SKU
    df_sku = df_filtrado.groupby(["data", "sku"])["estoque"].sum().reset_index()

    fig3 = px.line(
        df_sku,
        x="data",
        y="estoque",
        color="sku",
        title="Evolução por SKU"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# TAB 3 - QUALIDADE
# ---------------------------
with tab3:
    st.subheader("🌡️ Análise de Umidade")

    # Boxplot (muito profissional)
    fig4 = px.box(
        df_filtrado,
        x="sku",
        y="umidade_entrada",
        color="sku",
        title="Distribuição de Umidade por SKU"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # Média de umidade
    df_umidade = df_filtrado.groupby("sku")[["umidade_entrada"]].mean().reset_index()

    fig5 = px.bar(
        df_umidade,
        x="sku",
        y="umidade_entrada",
        color="sku",
        title="Umidade Média por SKU"
    )

    st.plotly_chart(fig5, use_container_width=True)


