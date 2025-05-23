import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(layout="wide")

st.title("PCG Storytelling de Dados")
st.markdown("Análise de Dados com Storytelling")


# Verificar diretório atual para evitar erros de caminho
st.write("Diretório atual:", os.getcwd())

num = st.number_input(
    "Quantas linhas você quer carregar do dataset?", 
    min_value=1,
    max_value=10000,
    value=5000,
    step=1000,
    help="Escolha o número de linhas a serem carregadas do dataset. O padrão é 1000."
)

# Carregar dados com limitação de colunas e linhas
try:
    pedidoxentrega = pd.read_csv(
        "datasets/olist_orders_dataset.csv",
        usecols=['order_id', 'order_purchase_timestamp', 'order_delivered_customer_date' ] , nrows = num # Pode ajustar conforme quiser
    )
except FileNotFoundError:
    st.error("Arquivo 'olist_orders_dataset.csv' não encontrado. Verifique o caminho e tente novamente.")
    st.stop()

# Conversão de colunas para datetime
pedidoxentrega['order_purchase_timestamp'] = pd.to_datetime(pedidoxentrega['order_purchase_timestamp'], errors='coerce')
pedidoxentrega['order_delivered_customer_date'] = pd.to_datetime(pedidoxentrega['order_delivered_customer_date'], errors='coerce')

# Remover linhas com datas ausentes
pedidoxentrega = pedidoxentrega.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])

# Cálculo do tempo de entrega em dias
pedidoxentrega['tempo_entrega_dias'] = (
    pedidoxentrega['order_delivered_customer_date'] - pedidoxentrega['order_purchase_timestamp']
).dt.days

# Criar gráfico
fig = go.Figure()

fig.add_trace(go.Line(
    x=pedidoxentrega['order_purchase_timestamp'],
    y=pedidoxentrega['tempo_entrega_dias'],
    mode='markers',
    name='Tempo de Entrega (dias)'
))

fig.update_layout(
    title="Tempo entre pedido e entrega",
    xaxis_title="Data do pedido",
    yaxis_title="Tempo de entrega (dias)",
    title_x=0.5,
    title_y=0.95,
    title_font=dict(size=20),
    xaxis_tickformat="%Y-%m-%d"
)

# Mostrar gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)

# Placeholder para próximos gráficos:
st.markdown("---")
st.markdown("- Tipos de pagamento por geolocalização - HEATMAP")

st.title("Tipos de Cliente por Geolocalização")


city = pd.read_csv('coordcidades/municipios.csv')
city_sp = city[city['ddd'] == 11]

clients = pd.read_csv( "datasets/olist_customers_dataset.csv")



#pegar tudo que for sp -> 11
#coluna customer state -> ddd




st.markdown("- Tempo de localização entre pedido e entrega por geolocalização - Heatmap")
st.markdown("- Quantas vendas foram feitas em cada estado - Gráfico de barras")
st.markdown("- Qual categoria mais vendeu - Gráfico de pizza")
