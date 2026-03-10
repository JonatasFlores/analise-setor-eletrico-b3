import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Setor Elétrico B3", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_csv('data/analise_eletrica_final.csv')
    return df

df = carregar_dados()

# --- SIDEBAR (Filtros) ---
st.sidebar.header("Filtros de Análise")
segmento = st.sidebar.multiselect(
    "Selecione o Segmento:",
    options=df['Segmento'].unique(),
    default=df['Segmento'].unique()
)

regiao = st.sidebar.multiselect(
    "Selecione a Região:",
    options=df['Regiao_Atuacao'].unique(),
    default=df['Regiao_Atuacao'].unique()
)

# Aplicando os filtros
df_filtrado = df[(df['Segmento'].isin(segmento)) & (df['Regiao_Atuacao'].isin(regiao))]

# --- TÍTULO ---
st.title("⚡ Inteligência de Mercado: Setor Elétrico")
st.markdown(f"Análise de **{len(df_filtrado)} empresas** filtradas para o seu portfólio econômico.")

# --- MÉTRICAS PRINCIPAIS (KPIs) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ROE Médio", f"{df_filtrado['roe'].mean()*100:.2f}%")
with col2:
    st.metric("DY Médio", f"{df_filtrado['dy'].mean():.2f}%")
with col3:
    st.metric("Margem Líquida Média", f"{df_filtrado['mrgliq'].mean()*100:.2f}%")

st.divider()

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Eficiência: ROE por Empresa")
    fig_roe = px.bar(df_filtrado.sort_values('roe'), x='roe', y='Ticker', 
                     orientation='h', color='Segmento',
                     title="Retorno sobre Patrimônio Líquido (ROE)")
    st.plotly_chart(fig_roe, use_container_width=True)

with col_graf2:
    st.subheader("Dividendos: DY por Empresa")
    fig_dy = px.bar(df_filtrado.sort_values('dy'), x='dy', y='Ticker', 
                    orientation='h', color='Regiao_Atuacao',
                    title="Dividend Yield (%)")
    st.plotly_chart(fig_dy, use_container_width=True)

# --- TABELA DETALHADA ---
st.subheader("Dados Consolidados e Estados de Atuação")
st.dataframe(df_filtrado[['Ticker', 'Empresa', 'Segmento', 'Regiao_Atuacao', 'Estados_Atuacao', 'roe', 'dy', 'mrgliq']])

# --- ANÁLISE DE PRESENÇA NACIONAL ---
st.divider()
st.subheader("📊 Presença Territorial por Estado")

# 1. Tratamento: Explodir a string de estados (ex: SP, RJ -> SP e RJ)
df_presenca = df_filtrado.assign(Estado=df_filtrado['Estados_Atuacao'].str.split(',')).explode('Estado')
df_presenca['Estado'] = df_presenca['Estado'].str.strip()

# 2. Agrupar para saber quantas empresas do seu filtro estão em cada estado
ranking_estados = df_presenca.groupby('Estado').size().reset_index(name='Qtd_Empresas')
ranking_estados = ranking_estados.sort_values('Qtd_Empresas', ascending=True) # Ordem para o gráfico horizontal

# 3. Gráfico de Barras Horizontal (Muito mais legível que o mapa vazio)
fig_presenca = px.bar(
    ranking_estados, 
    x='Qtd_Empresas', 
    y='Estado', 
    orientation='h',
    title="Estados com Maior Concentração de Empresas do Portfólio",
    color='Qtd_Empresas',
    color_continuous_scale="Viridis",
    labels={'Qtd_Empresas': 'Número de Empresas', 'Estado': 'UF'}
)

fig_presenca.update_layout(showlegend=False, height=600)

st.plotly_chart(fig_presenca, use_container_width=True)

# 4. Insights Automáticos para o seu Portfólio
estado_lider = ranking_estados.iloc[-1]['Estado']
qtd_lider = ranking_estados.iloc[-1]['Qtd_Empresas']

st.info(f"💡 **Insight Econômico:** O estado de **{estado_lider}** possui a maior concentração do seu portfólio, com **{qtd_lider} empresas** atuantes. Isso indica uma exposição maior aos riscos regulatórios e tarifários desta região.")