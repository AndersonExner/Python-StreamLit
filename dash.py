
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard interativo - Teste")

# Gerar dados aleatórios
np.random.seed(42)

quantidade = 100

df = pd.DataFrame({
    "Data": pd.date_range(
        start="2026-01-01",
        periods=quantidade,
        freq="D"
    ),
    "Vendas": np.random.randint(100, 1000, quantidade),
    "Lucro": np.random.randint(20, 300, quantidade),
    "Categoria": np.random.choice(
        ["Eletrônicos", "Roupas", "Alimentos"],
        quantidade
    )
})

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("Filtros")

# Filtro por período
data_inicial, data_final = st.sidebar.date_input(
    "Período",
    value=(df["Data"].min().date(), df["Data"].max().date()),
    min_value=df["Data"].min().date(),
    max_value=df["Data"].max().date()
)

# Filtro por categoria
categorias = st.sidebar.multiselect(
    "Categorias",
    options=sorted(df["Categoria"].unique()),
    default=sorted(df["Categoria"].unique())
)

# Filtro por faixa de vendas
venda_min, venda_max = st.sidebar.slider(
    "Faixa de vendas",
    min_value=int(df["Vendas"].min()),
    max_value=int(df["Vendas"].max()),
    value=(
        int(df["Vendas"].min()),
        int(df["Vendas"].max())
    )
)

# Aplicar filtros
df_filtrado = df[
    (df["Data"].dt.date >= data_inicial)
    & (df["Data"].dt.date <= data_final)
    & (df["Categoria"].isin(categorias))
    & (df["Vendas"] >= venda_min)
    & (df["Vendas"] <= venda_max)
]

# -------------------------
# INDICADORES
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total de vendas",
    f"R$ {df_filtrado['Vendas'].sum():,.2f}"
)

col2.metric(
    "Lucro total",
    f"R$ {df_filtrado['Lucro'].sum():,.2f}"
)

col3.metric(
    "Média de vendas",
    f"R$ {df_filtrado['Vendas'].mean():,.2f}"
    if not df_filtrado.empty else "R$ 0,00"
)

st.caption(f"Registros encontrados: {len(df_filtrado)} de {len(df)}")

st.divider()

# -------------------------
# GRÁFICO DE VENDAS
# -------------------------
if df_filtrado.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
else:
    fig_vendas = px.line(
        df_filtrado,
        x="Data",
        y="Vendas",
        title="Vendas ao longo do tempo",
        markers=True
    )

    st.plotly_chart(fig_vendas, use_container_width=True)

    # -------------------------
    # GRÁFICOS POR CATEGORIA
    # -------------------------
    col4, col5 = st.columns(2)

    with col4:
        vendas_categoria = (
            df_filtrado.groupby("Categoria", as_index=False)["Vendas"]
            .sum()
        )

        fig_categoria = px.bar(
            vendas_categoria,
            x="Categoria",
            y="Vendas",
            title="Vendas por categoria",
            color="Categoria"
        )

        st.plotly_chart(fig_categoria, use_container_width=True)

    with col5:
        fig_lucro = px.scatter(
            df_filtrado,
            x="Vendas",
            y="Lucro",
            color="Categoria",
            title="Relação entre vendas e lucro",
            hover_data=["Data"]
        )

        st.plotly_chart(fig_lucro, use_container_width=True)

    # -------------------------
    # TABELA DE DADOS
    # -------------------------
    with st.expander("Visualizar dados"):
        st.dataframe(df_filtrado, use_container_width=True)
