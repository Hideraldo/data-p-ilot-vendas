# Data Pilot — Painel de Vendas com Chat Inteligente

Painel interativo de vendas em Streamlit + agente de IA que responde perguntas
em português consultando métricas calculadas em Python.

> **A regra que segura tudo:** o Python calcula, a IA só explica.
> O modelo nunca inventa número — ele escolhe qual função chamar e o Python
> devolve o valor real.

## 📸 Prints

| Painel | Chat |
|---|---|
| ![Painel](images/painel.png) | ![Chat](images/chat.png) |

## 📊 O que o Data Pilot faz

- **Painel**: receita total, pedidos, ticket médio, clientes únicos,
  taxa de cancelamento e receita média por cliente — filtrável por categoria.
  Gráfico de receita mensal em Plotly.
- **Chat**: você pergunta em português; o modelo escolhe a ferramenta certa,
  o Python calcula e a resposta volta com o número exato.

## 🗂️ De onde vêm os dados

`data/sales.csv` — planilha de vendas com colunas:
`pedido_id, data, produto, categoria, cliente_id, cidade, canal,
quantidade, preco_unitario, status`.

A limpeza (`data_prep.py`) converte datas, padroniza o status, remove
duplicados e cria a coluna `receita`, salvando `data/sales_clean.csv`
com `;` como separador e `,` como decimal.

## ⚙️ Como instalar e rodar

```bash
# 1. Clone o repositório
git clone https://github.com/Hideraldo/data-p-ilot-vendas.git
cd data-p-ilot-vendas

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a chave do OpenRouter
cp .env.example .env
# edite o .env e cole sua chave em OPENROUTER_API_KEY

# 4. Rode o app
python -m streamlit run app.py
