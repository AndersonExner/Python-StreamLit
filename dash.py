"""
Dashboard interativo de vendas — projeto de estudos com Streamlit.

Como rodar:
    streamlit run dash.py

Como o Streamlit funciona (resumo):
    O Streamlit executa este arquivo de cima para baixo TODA VEZ que o usuário
    interage com algum widget (filtro, botão, slider...). Não existe "callback"
    obrigatório: o valor atual de cada widget é simplesmente retornado pela
    função que o desenha. Por isso o código é escrito como um script linear.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------------------------
# st.set_page_config deve ser a PRIMEIRA chamada do Streamlit no script.
# Define título da aba do navegador, ícone e layout ("wide" usa a tela toda).
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# Constantes usadas em vários pontos do código
CATEGORIAS = ["Eletrônicos", "Roupas", "Alimentos"]

# Margem de lucro média de cada categoria (usada para gerar dados realistas)
MARGEM_POR_CATEGORIA = {"Eletrônicos": 0.15, "Roupas": 0.35, "Alimentos": 0.10}

# Cores fixas por categoria: assim a mesma categoria tem sempre a mesma cor
# em todos os gráficos, o que facilita a leitura.
CORES_CATEGORIA = {
    "Eletrônicos": "#4C78A8",
    "Roupas": "#F58518",
    "Alimentos": "#54A24B",
}

# Opções de agrupamento temporal -> "regra" de frequência do pandas
GRANULARIDADES = {"Diário": "D", "Semanal": "W", "Mensal": "MS"}


# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------
@st.cache_data
def gerar_dados(dias: int = 365, semente: int = 42) -> pd.DataFrame:
    """Gera um DataFrame de vendas fictícias, uma linha por dia e categoria.

    O decorator @st.cache_data guarda o resultado em memória: como o script
    roda de novo a cada interação, sem o cache os dados seriam recriados o
    tempo todo. Com o cache, a função só executa de novo se os argumentos
    (dias, semente) mudarem.
    """
    # Gerador de números aleatórios com semente fixa: os "aleatórios" saem
    # sempre iguais, então o dashboard é reproduzível.
    rng = np.random.default_rng(semente)

    datas = pd.date_range(start="2026-01-01", periods=dias, freq="D")

    linhas = []
    for categoria in CATEGORIAS:
        # Componentes da venda diária, para os dados não serem puro ruído:
        base = rng.integers(300, 600)                          # nível médio da categoria
        tendencia = np.linspace(0, 150, dias)                  # crescimento ao longo do ano
        fim_de_semana = np.where(datas.day_of_week >= 5, 1.3, 1.0)  # sábado/domingo vendem +30%
        ruido = rng.normal(0, 60, dias)                        # variação aleatória do dia a dia

        vendas = ((base + tendencia + ruido) * fim_de_semana).clip(min=50).round(2)

        # Lucro = vendas x margem da categoria, com uma pequena variação
        margem = MARGEM_POR_CATEGORIA[categoria] + rng.normal(0, 0.03, dias)
        lucro = (vendas * margem).round(2)

        linhas.append(pd.DataFrame({
            "Data": datas,
            "Categoria": categoria,
            "Vendas": vendas,
            "Lucro": lucro,
        }))

    # pd.concat empilha os DataFrames de cada categoria em um só
    return pd.concat(linhas, ignore_index=True)


def formatar_moeda(valor: float) -> str:
    """Formata um número no padrão brasileiro: 1234.5 -> 'R$ 1.234,50'.

    O Python formata no padrão americano (1,234.50), então trocamos os
    separadores usando um caractere temporário ("_").
    """
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def variacao_percentual(atual: float, anterior: float) -> str | None:
    """Calcula a variação % entre dois valores, já formatada para o st.metric.

    Retorna None quando não há base de comparação; nesse caso o st.metric
    simplesmente não mostra a seta de variação.
    """
    if not anterior:
        return None
    variacao = (atual - anterior) / anterior * 100
    return f"{variacao:+.1f}%".replace(".", ",")


def ler_periodo(selecao, padrao: tuple[date, date]) -> tuple[date, date]:
    """Normaliza o retorno do st.date_input em modo intervalo.

    CORREÇÃO DO BUG ORIGINAL: enquanto o usuário escolhe o intervalo, o
    date_input devolve uma tupla com só UMA data (a inicial). Fazer
    `inicio, fim = st.date_input(...)` nesse momento gerava:
        ValueError: not enough values to unpack (expected 2, got 1)
    Aqui tratamos os três casos possíveis: 0, 1 ou 2 datas.
    """
    if len(selecao) == 2:
        return selecao[0], selecao[1]
    if len(selecao) == 1:
        # Só a data inicial foi escolhida: usamos ela como início e fim
        return selecao[0], selecao[0]
    return padrao


def filtrar(df: pd.DataFrame, inicio: date, fim: date, categorias: list[str]) -> pd.DataFrame:
    """Retorna apenas as linhas dentro do período e das categorias escolhidas.

    Cada condição gera uma "máscara booleana" (uma Series de True/False);
    o operador & combina as máscaras e df[mascara] mantém só as linhas True.
    """
    mascara = (
        (df["Data"].dt.date >= inicio)
        & (df["Data"].dt.date <= fim)
        & (df["Categoria"].isin(categorias))
    )
    return df[mascara]


# ---------------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------------
df = gerar_dados()
data_min = df["Data"].min().date()
data_max = df["Data"].max().date()

# ---------------------------------------------------------------------------
# BARRA LATERAL (FILTROS)
# ---------------------------------------------------------------------------
# Tudo que é chamado via st.sidebar aparece no painel lateral esquerdo.
st.sidebar.header("🔎 Filtros")

# Por padrão mostramos os últimos 90 dias do conjunto de dados
periodo_padrao = (data_max - timedelta(days=89), data_max)

selecao_periodo = st.sidebar.date_input(
    "Período",
    value=periodo_padrao,       # passar uma tupla ativa o modo "intervalo"
    min_value=data_min,
    max_value=data_max,
    format="DD/MM/YYYY",
)
data_inicial, data_final = ler_periodo(selecao_periodo, periodo_padrao)

# st.multiselect devolve a lista de opções marcadas
categorias = st.sidebar.multiselect(
    "Categorias",
    options=CATEGORIAS,
    default=CATEGORIAS,
)

# st.segmented_control mostra botões lado a lado onde só um fica ativo
granularidade = st.sidebar.segmented_control(
    "Agrupar gráficos por",
    options=list(GRANULARIDADES),
    default="Semanal",
)
# Se o usuário clicar no botão ativo ele é desmarcado (retorna None)
granularidade = granularidade or "Semanal"

st.sidebar.caption(
    f"Dados disponíveis de {data_min:%d/%m/%Y} a {data_max:%d/%m/%Y}."
)

# ---------------------------------------------------------------------------
# APLICAÇÃO DOS FILTROS
# ---------------------------------------------------------------------------
df_filtrado = filtrar(df, data_inicial, data_final, categorias)

# Período anterior com a mesma duração, para comparar nos indicadores.
# Ex.: filtro de 01/04 a 30/04 (30 dias) -> período anterior: 02/03 a 31/03.
duracao = data_final - data_inicial
fim_anterior = data_inicial - timedelta(days=1)
inicio_anterior = fim_anterior - duracao
df_anterior = filtrar(df, inicio_anterior, fim_anterior, categorias)

# ---------------------------------------------------------------------------
# CABEÇALHO
# ---------------------------------------------------------------------------
st.title("📊 Dashboard de Vendas")
st.caption(
    f"Período: **{data_inicial:%d/%m/%Y}** a **{data_final:%d/%m/%Y}** · "
    f"{len(df_filtrado)} registros · dados fictícios gerados com NumPy"
)

# st.stop() interrompe o script aqui: nada abaixo é desenhado.
# Útil para evitar erros quando o filtro não retorna dados.
if df_filtrado.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

# ---------------------------------------------------------------------------
# INDICADORES (KPIs)
# ---------------------------------------------------------------------------
# Totais do período atual e do anterior
vendas_total = df_filtrado["Vendas"].sum()
lucro_total = df_filtrado["Lucro"].sum()
margem = lucro_total / vendas_total * 100
dias_no_periodo = df_filtrado["Data"].nunique()
media_diaria = vendas_total / dias_no_periodo

vendas_ant = df_anterior["Vendas"].sum()
lucro_ant = df_anterior["Lucro"].sum()
margem_ant = lucro_ant / vendas_ant * 100 if vendas_ant else 0
media_diaria_ant = vendas_ant / df_anterior["Data"].nunique() if vendas_ant else 0

# Série diária de vendas, usada nas mini-linhas (sparklines) dos cards
vendas_por_dia = df_filtrado.groupby("Data")["Vendas"].sum()
lucro_por_dia = df_filtrado.groupby("Data")["Lucro"].sum()

# st.columns divide a largura em colunas; cada uma recebe um card
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total de vendas",
    formatar_moeda(vendas_total),
    delta=variacao_percentual(vendas_total, vendas_ant),
    help="Variação em relação ao período anterior de mesma duração.",
    chart_data=vendas_por_dia.tolist(),   # mini gráfico dentro do card
    border=True,
)
col2.metric(
    "Lucro total",
    formatar_moeda(lucro_total),
    delta=variacao_percentual(lucro_total, lucro_ant),
    chart_data=lucro_por_dia.tolist(),
    border=True,
)
col3.metric(
    "Margem de lucro",
    f"{margem:.1f}%".replace(".", ","),
    # Para margem, a variação é em pontos percentuais (p.p.), não em %
    delta=f"{margem - margem_ant:+.1f}".replace(".", ",") + " p.p." if vendas_ant else None,
    border=True,
)
col4.metric(
    "Média de vendas por dia",
    formatar_moeda(media_diaria),
    delta=variacao_percentual(media_diaria, media_diaria_ant),
    border=True,
)

# ---------------------------------------------------------------------------
# ABAS
# ---------------------------------------------------------------------------
# st.tabs cria abas; o conteúdo de cada uma vai dentro de um bloco "with".
aba_geral, aba_categorias, aba_dados = st.tabs(
    ["📈 Visão geral", "🏷️ Categorias", "🗂️ Dados"]
)

# Agrupa por período (dia/semana/mês) e categoria.
# pd.Grouper(key=..., freq=...) agrupa datas em "baldes" de tempo.
freq = GRANULARIDADES[granularidade]
df_tempo = (
    df_filtrado
    .groupby([pd.Grouper(key="Data", freq=freq), "Categoria"], as_index=False)
    [["Vendas", "Lucro"]]
    .sum()
)

with aba_geral:
    # Gráfico de área empilhada: mostra o total e a contribuição de cada categoria
    fig_tempo = px.area(
        df_tempo,
        x="Data",
        y="Vendas",
        color="Categoria",
        color_discrete_map=CORES_CATEGORIA,
        title=f"Vendas ao longo do tempo ({granularidade.lower()})",
        labels={"Vendas": "Vendas (R$)", "Data": ""},
    )
    # hovermode="x unified" mostra todas as categorias num único balão
    fig_tempo.update_layout(hovermode="x unified", legend_title_text="")
    st.plotly_chart(fig_tempo)

    col_esq, col_dir = st.columns(2)

    with col_esq:
        # Vendas por dia da semana: ajuda a enxergar o efeito "fim de semana"
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        por_dia_semana = (
            df_filtrado
            .assign(DiaSemana=df_filtrado["Data"].dt.day_of_week)  # 0=segunda ... 6=domingo
            .groupby("DiaSemana", as_index=False)["Vendas"]
            .mean()
        )
        por_dia_semana["Dia"] = por_dia_semana["DiaSemana"].map(dict(enumerate(dias_semana)))

        fig_semana = px.bar(
            por_dia_semana,
            x="Dia",
            y="Vendas",
            title="Média de vendas por dia da semana",
            labels={"Vendas": "Vendas médias (R$)", "Dia": ""},
            text_auto=".0f",   # escreve o valor em cima de cada barra
        )
        st.plotly_chart(fig_semana)

    with col_dir:
        # Os 5 dias com maior faturamento (todas as categorias somadas)
        top_dias = (
            vendas_por_dia
            .nlargest(5)
            .reset_index()
            .rename(columns={"Data": "Dia"})
        )
        st.markdown("**🏆 Top 5 dias de vendas**")
        # column_config controla como cada coluna da tabela é exibida
        st.dataframe(
            top_dias,
            hide_index=True,
            column_config={
                "Dia": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Vendas": st.column_config.NumberColumn("Vendas (R$)", format="%.2f"),
            },
        )

with aba_categorias:
    resumo = (
        df_filtrado
        .groupby("Categoria", as_index=False)[["Vendas", "Lucro"]]
        .sum()
    )
    resumo["Margem (%)"] = resumo["Lucro"] / resumo["Vendas"] * 100

    col_esq, col_dir = st.columns(2)

    with col_esq:
        # Gráfico de rosca (pizza com furo): participação de cada categoria
        fig_pizza = px.pie(
            resumo,
            names="Categoria",
            values="Vendas",
            hole=0.5,
            color="Categoria",
            color_discrete_map=CORES_CATEGORIA,
            title="Participação nas vendas",
        )
        st.plotly_chart(fig_pizza)

    with col_dir:
        fig_margem = px.bar(
            resumo,
            x="Categoria",
            y="Margem (%)",
            color="Categoria",
            color_discrete_map=CORES_CATEGORIA,
            title="Margem de lucro por categoria",
            text_auto=".1f",
        )
        fig_margem.update_layout(showlegend=False)
        st.plotly_chart(fig_margem)

    # Dispersão: cada ponto é um dia de uma categoria.
    # trendline="ols" exigiria a biblioteca statsmodels; por isso fica de fora.
    fig_dispersao = px.scatter(
        df_filtrado,
        x="Vendas",
        y="Lucro",
        color="Categoria",
        color_discrete_map=CORES_CATEGORIA,
        title="Relação entre vendas e lucro (cada ponto = 1 dia)",
        hover_data={"Data": "|%d/%m/%Y"},
        opacity=0.7,
    )
    st.plotly_chart(fig_dispersao)

with aba_dados:
    # Tabela completa, ordenada da data mais recente para a mais antiga
    tabela = df_filtrado.sort_values(["Data", "Categoria"], ascending=[False, True])

    st.dataframe(
        tabela,
        hide_index=True,
        column_config={
            "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Vendas": st.column_config.NumberColumn("Vendas (R$)", format="%.2f"),
            "Lucro": st.column_config.NumberColumn("Lucro (R$)", format="%.2f"),
        },
    )

    # st.download_button permite baixar um arquivo gerado na hora.
    # sep=";" e decimal="," deixam o CSV pronto para abrir no Excel em português;
    # o encoding "utf-8-sig" faz o Excel reconhecer os acentos.
    csv = tabela.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar dados filtrados (CSV)",
        data=csv,
        file_name=f"vendas_{data_inicial:%Y%m%d}_{data_final:%Y%m%d}.csv",
        mime="text/csv",
    )
