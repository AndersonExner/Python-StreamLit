# Python + Streamlit — Projeto de Estudos

Projeto pessoal de estudos para aprender a construir **dashboards interativos em Python** usando Streamlit, pandas e Plotly.

O app (`dash.py`) gera um conjunto de dados de vendas fictício e o apresenta em um dashboard com filtros, indicadores e gráficos.

## O que o dashboard faz

- **Dados de exemplo**: 1 ano de vendas diárias fictícias (a partir de 01/01/2026) para 3 categorias (Eletrônicos, Roupas, Alimentos). Os dados têm tendência de crescimento, pico nos fins de semana e margem de lucro diferente por categoria, e usam semente fixa para serem sempre os mesmos.
- **Filtros na barra lateral**: período (padrão: últimos 90 dias), categorias e agrupamento dos gráficos (diário, semanal ou mensal).
- **Indicadores (KPIs)**: total de vendas, lucro total, margem de lucro e média diária, com variação em relação ao período anterior de mesma duração e mini-gráficos (sparklines).
- **Abas**:
  - **Visão geral**: vendas ao longo do tempo (área empilhada), média por dia da semana e top 5 dias.
  - **Categorias**: participação nas vendas (rosca), margem por categoria e dispersão vendas × lucro.
  - **Dados**: tabela formatada e botão para baixar o CSV (pronto para o Excel em português).

## Tecnologias utilizadas

| Biblioteca | Para que serve no projeto |
|---|---|
| [Python 3.13](https://www.python.org/) | Linguagem base |
| [Streamlit](https://streamlit.io/) | Cria a interface web (layout, filtros, métricas, tabela) direto do script Python, sem HTML/JS |
| [pandas](https://pandas.pydata.org/) | Monta o `DataFrame`, aplica os filtros e faz agregações (`groupby`) |
| [NumPy](https://numpy.org/) | Gera os dados aleatórios de exemplo |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Gera os gráficos interativos (zoom, hover, legenda clicável) |

### Conceitos praticados

- Layout: `st.set_page_config`, `st.sidebar`, `st.columns`, `st.tabs`
- Widgets de entrada: `st.date_input` (modo intervalo), `st.multiselect`, `st.segmented_control`
- Exibição: `st.metric` (com `delta` e sparkline), `st.plotly_chart`, `st.dataframe` com `column_config`, `st.download_button`
- Modelo de execução do Streamlit: o script inteiro roda de novo a cada interação, por isso o `@st.cache_data` evita recalcular os dados; `st.stop()` interrompe a renderização
- pandas: máscaras booleanas, `groupby`, `pd.Grouper` para agrupar datas por dia/semana/mês, `nlargest`, exportação para CSV
- Plotly Express: área, barras, rosca e dispersão, com cores fixas por categoria
- Formatação de valores no padrão brasileiro (`R$ 1.234,56`)

## Como executar

Pré-requisito: Python 3.13 (ou compatível) instalado.

```bash
# 1. Clonar o repositório
git clone https://github.com/AndersonExner/Python-StreamLit.git
cd Python-StreamLit

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Rodar o dashboard
streamlit run dash.py
```

O navegador abre automaticamente em `http://localhost:8501`.

> **Dica:** se o comando `streamlit` der erro de "Fatal error in launcher" (acontece quando a pasta do venv é renomeada ou movida), use `python -m streamlit run dash.py`.

## Estrutura

```
Python-StreamLit/
├── dash.py            # aplicação Streamlit
├── requirements.txt   # dependências
└── README.md
```
