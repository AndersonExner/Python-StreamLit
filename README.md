# Python + Streamlit — Projeto de Estudos

Projeto pessoal de estudos para aprender a construir **dashboards interativos em Python** usando Streamlit, pandas e Plotly.

O app (`dash.py`) gera um conjunto de dados de vendas fictício e o apresenta em um dashboard com filtros, indicadores e gráficos.

## O que o dashboard faz

- **Dados de exemplo**: 100 dias de vendas aleatórias (a partir de 01/01/2026), com as colunas `Data`, `Vendas`, `Lucro` e `Categoria` (Eletrônicos, Roupas, Alimentos). A semente fixa (`np.random.seed(42)`) garante que os dados sejam sempre os mesmos.
- **Filtros na barra lateral**: período, categorias e faixa de valores de vendas.
- **Indicadores (KPIs)**: total de vendas, lucro total e média de vendas do recorte filtrado.
- **Gráficos**:
  - Linha — vendas ao longo do tempo
  - Barras — vendas por categoria
  - Dispersão — relação entre vendas e lucro
- **Tabela**: os dados filtrados, dentro de um painel expansível.

## Tecnologias utilizadas

| Biblioteca | Para que serve no projeto |
|---|---|
| [Python 3.13](https://www.python.org/) | Linguagem base |
| [Streamlit](https://streamlit.io/) | Cria a interface web (layout, filtros, métricas, tabela) direto do script Python, sem HTML/JS |
| [pandas](https://pandas.pydata.org/) | Monta o `DataFrame`, aplica os filtros e faz agregações (`groupby`) |
| [NumPy](https://numpy.org/) | Gera os dados aleatórios de exemplo |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Gera os gráficos interativos (zoom, hover, legenda clicável) |

### Conceitos praticados

- `st.set_page_config`, `st.title`, `st.sidebar`, `st.columns`, `st.metric`, `st.expander`, `st.plotly_chart`, `st.dataframe`
- Widgets de entrada: `st.date_input`, `st.multiselect`, `st.slider`
- Modelo de execução do Streamlit: o script inteiro roda de novo a cada interação do usuário
- Filtragem com máscaras booleanas no pandas e agregação com `groupby`
- Gráficos de linha, barra e dispersão com Plotly Express

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
