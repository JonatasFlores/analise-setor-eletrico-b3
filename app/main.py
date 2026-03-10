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