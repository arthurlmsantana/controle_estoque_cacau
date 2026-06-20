import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📦 Dashboard de Estoque de Cacau")
st.subheader(":necktie: Portifólio - Arthur Lima Machado de Santana")
st.caption("Linkedin: https://www.linkedin.com/in/arthur-santana-68167994/?skipRedirect=true")

# Carregar dados
df = pd.read_csv("data\estoque_cacau.csv")
df["data"] = pd.to_datetime(df["data"])

# 📊 Evolução do estoque
st.subheader("📈 Evolução do Estoque ao Longo do Tempo")

# filtro temporal
min_data = df["data"].min().to_pydatetime()
max_data = df["data"].max().to_pydatetime()

periodo = st.slider(
    "Selecione o período",
    min_value=min_data,
    max_value=max_data,
    value=(min_data, max_data)
)

data_inicio, data_fim = periodo

# garantir tipo correto
data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)


# Sidebar filtros
st.sidebar.header("Filtros")

depositos = st.sidebar.multiselect(
    "Selecione o(s) depósito(s)",
    options=df["deposito"].unique(),
    default=df["deposito"].unique()
)

# Aplicar filtros
df_filtrado = df[
    (df["deposito"].isin(depositos)) &
    (df["data"] >= pd.to_datetime(data_inicio)) &
    (df["data"] <= pd.to_datetime(data_fim))
]


# KPIs
col1, col2, col3 = st.columns(3)

estoque_total = df_filtrado.groupby("data")["estoque"].sum().iloc[-1]
entrada_total = df_filtrado["entrada"].sum()
saida_total = df_filtrado["saida"].sum()

col1.metric("Estoque Atual Total", f"{estoque_total:,.0f} sacas")
col2.metric("Entradas no Período", f"{entrada_total:,.0f}")
col3.metric("Saídas no Período", f"{saida_total:,.0f}")



df_estoque = df_filtrado.groupby(["data", "deposito"])["estoque"].mean().reset_index()

fig = px.line(
    df_estoque,
    x="data",
    y="estoque",
    color="deposito",
    title="Estoque por Depósito ao Longo do Tempo"
)

st.plotly_chart(fig, use_container_width=True)

# 📦 Comparação entre depósitos
st.subheader("🏭 Estoque Médio por Depósito")

df_media = df_filtrado.groupby("deposito")["estoque"].mean().reset_index()

fig2 = px.bar(
    df_media,
    x="deposito",
    y="estoque",
    color="deposito",
    title="Estoque Médio por Depósito"
)

st.plotly_chart(fig2, use_container_width=True)

# 🔄 Fluxo (entradas x saídas)
st.subheader("🔄 Fluxo de Movimento")

df_fluxo = df_filtrado.groupby("data")[["entrada", "saida"]].sum().reset_index()

fig3 = px.line(
    df_fluxo,
    x="data",
    y=["entrada", "saida"],
    title="Entradas vs Saídas ao Longo do Tempo"
)

st.plotly_chart(fig3, use_container_width=True)

