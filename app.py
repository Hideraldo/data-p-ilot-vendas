import streamlit as st
import pandas as pd
import plotly.express as px

from metrics import (
    receita_total, total_pedidos, ticket_medio,
    clientes_unicos, taxa_cancelamento, receita_media_por_cliente
)
from agent import perguntar_ao_agente

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Data Pilot",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# CARREGAMENTO DOS DADOS (com cache)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    return pd.read_csv("data/sales_clean.csv", sep=';', decimal=',')

df = carregar_dados()

# ---------------------------------------------------------
# MENU LATERAL
# ---------------------------------------------------------
st.sidebar.title("📊 Data Pilot")
pagina = st.sidebar.radio("Navegação", ["Painel", "Chat com os Dados"])

# Filtro de categoria (aparece nas duas páginas)
categorias = sorted(df['categoria'].dropna().unique().tolist())
categoria_selecionada = st.sidebar.multiselect(
    "Filtrar por categoria",
    options=categorias,
    default=categorias
)

df_filtrado = df[df['categoria'].isin(categoria_selecionada)].copy()

# ---------------------------------------------------------
# PÁGINA 1: PAINEL
# ---------------------------------------------------------
if pagina == "Painel":
    st.title("📊 Painel de Vendas")
    st.caption(f"{len(df_filtrado)} pedidos no filtro atual")

    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Receita Total", f"R$ {receita_total(df_filtrado):,.2f}")
    with col2:
        st.metric("Pedidos", total_pedidos(df_filtrado))
    with col3:
        st.metric("Ticket Médio", f"R$ {ticket_medio(df_filtrado):,.2f}")
    with col4:
        st.metric("Clientes Únicos", clientes_unicos(df_filtrado))

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Taxa de Cancelamento", f"{taxa_cancelamento(df_filtrado):.1%}")
    with col6:
        st.metric(
            "Receita Média por Cliente",
            f"R$ {receita_media_por_cliente(df_filtrado):,.2f}"
        )

    st.divider()

    # Gráfico de receita mensal
    st.subheader("Receita por Mês")
    df_mensal = df_filtrado.copy()
    df_mensal['data'] = pd.to_datetime(df_mensal['data'])
    df_mensal['mes'] = df_mensal['data'].dt.to_period('M').astype(str)
    receita_mensal = (
        df_mensal.groupby('mes')['receita']
        .sum()
        .reset_index()
        .sort_values('mes')
    )

    if not receita_mensal.empty:
        fig = px.line(
            receita_mensal,
            x='mes',
            y='receita',
            markers=True,
            labels={'mes': 'Mês', 'receita': 'Receita (R$)'},
            title="Evolução da Receita Mensal"
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado para o filtro selecionado.")

# ---------------------------------------------------------
# PÁGINA 2: CHAT
# ---------------------------------------------------------
elif pagina == "Chat com os Dados":
    st.title("💬 Converse com os Dados")
    st.caption(
        "Pergunte em português. O modelo escolhe a ferramenta certa — "
        "e o Python calcula. A IA só explica."
    )

    # Histórico de mensagens na sessão
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    # Renderiza histórico
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do usuário
    if pergunta := st.chat_input("Ex.: Qual foi a receita total?"):
        # Mostra a pergunta
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        # Chama o agente
        with st.chat_message("assistant"):
            with st.spinner("Consultando os dados..."):
                resposta = perguntar_ao_agente(pergunta, df_filtrado)
            st.markdown(resposta)

        st.session_state.mensagens.append({"role": "assistant", "content": resposta})

    # Botão para limpar histórico
    if st.session_state.mensagens:
        if st.button("🗑️ Limpar conversa"):
            st.session_state.mensagens = []
            st.rerun()