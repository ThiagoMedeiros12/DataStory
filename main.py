import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
import json

def text_normalizer(text):
    if isinstance(text, str):
        text_no_accent = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return text_no_accent.lower()
    return text

sp_state = json.load(open("geojson/map.geojson", 'r', encoding="utf8"))

# Configuração da página
st.set_page_config(layout="wide", page_title="PCG Storytelling de Dados", page_icon=":bar_chart:")



st.title("PCG Storytelling de Dados")
st.markdown("Análise de Dados com Storytelling")



st.markdown("---")
st.title("Análise de Tempo de Entrega",)
st.markdown("Nessa análise é possível observar o tempo entre o pedido e a entrega do produto.")
st.markdown("---")

num = st.number_input(
    "Quantas linhas você quer carregar do dataset?", 
    min_value=1,
    max_value=10000,
    value=5000,
    step=500,
    help="Escolha o número de linhas a serem carregadas do dataset. O padrão é 1000."
)

try:
    pedidoxentrega = pd.read_csv(
        "datasets/olist_orders_dataset.csv",
        usecols=['order_id', 'order_purchase_timestamp', 'order_delivered_customer_date' ] , nrows = num # Pode ajustar conforme quiser
    )
except FileNotFoundError:
    st.error("Arquivo 'olist_orders_dataset.csv' não encontrado. Verifique o caminho e tente novamente.")
    st.stop()


pedidoxentrega['order_purchase_timestamp'] = pd.to_datetime(pedidoxentrega['order_purchase_timestamp'], errors='coerce')
pedidoxentrega['order_delivered_customer_date'] = pd.to_datetime(pedidoxentrega['order_delivered_customer_date'], errors='coerce')


pedidoxentrega = pedidoxentrega.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])


pedidoxentrega['tempo_entrega_dias'] = (
    pedidoxentrega['order_delivered_customer_date'] - pedidoxentrega['order_purchase_timestamp']
).dt.days


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

st.plotly_chart(fig, use_container_width=True)



st.markdown("---")
st.title("Tipos de Cliente por Geolocalização")
st.markdown("Essa análise mostra a quantidade de clientes por município na região de São Paulo.")
st.markdown("---")

city = pd.read_csv('coordcidades/municipios.csv')
city_sp = city[city['ddd'].between(11, 19)]
city_sp['city'] = city_sp['city'].apply(text_normalizer)

clients = pd.read_csv("datasets/olist_customers_dataset.csv", index_col=False, sep=",")
clients['ddd'] = clients['ddd'].replace('SP', 11)
clients['city'] = clients['city'].apply(text_normalizer)

client_city_merge = pd.merge(city_sp, clients, on='city', how='inner')

client_count = client_city_merge.groupby('city').size().reset_index(name='client_count')
df_final = pd.merge(client_city_merge, client_count, on='city', how='left')

fig_customer_city = px.choropleth_mapbox(df_final, 
                               locations="codigo_ibge",
                               geojson=sp_state,
                               featureidkey="properties.id",
                               color="client_count",
                               hover_name="city",
                               mapbox_style="open-street-map",
                               center={"lat": -23.5489, "lon": -46.6388},
                               zoom=7.2,
                               opacity=0.5,
                               color_continuous_scale="RdBu_r",
                               title="Quantidade de clientes por município")
st.plotly_chart(fig_customer_city, use_container_width=True)

st.markdown("---")
st.title("Categorias de Produtos com mais Vendas")
st.markdown("Essa análise mostra a quantidade de vendas por categoria de produto.")
st.markdown("---")


produtos = pd.read_csv("datasets/olist_products_dataset.csv",  usecols =['product_id','product_category_name'])
orders = pd.read_csv("datasets/olist_order_items_dataset.csv", usecols=['order_id','product_id'])


productosxorders = pd.merge(produtos, orders, on='product_id', how='inner')
orders_count = productosxorders.groupby('product_category_name').size().reset_index(name='orders_count')	
productosxorders = pd.merge(produtos, orders_count, on='product_category_name', how='left')

fig_pizza = px.pie(productosxorders,
                   names='product_category_name',
                   values='orders_count',
                   title='Quantidade de vendas por categoria de produto',
                   color_discrete_sequence=px.colors.sequential.Rainbow_r,
                   hole=0.3)
exploded = [0.1] * len(productosxorders['product_category_name'])
fig_pizza.update_traces(textposition='inside', textinfo='percent+label', pull=exploded)
fig_pizza.update_layout(
    title_x=0.3,
    title_y=0.95,
    title_font=dict(size=20),
    legend_title_text='Categorias de produtos',
    legend_title_font=dict(size=15),
    legend_font=dict(size=12)
)
fig_pizza.update_traces(textfont_size=12, textfont_color='black')
st.plotly_chart(fig_pizza, use_container_width=True, use_container_height=True)





st.markdown("---")
