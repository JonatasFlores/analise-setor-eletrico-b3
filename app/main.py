import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from utils import formatar_bilhoes_milhoes

st.set_page_config(page_title="Dashboard Setor Elétrico B3", layout="wide")

@st.cache_data
def carregar_dados():
    # Carregando o CSV final gerado pelo seu script de processamento
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

# --- MÉTRICAS PRINCIPAIS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("ROE Médio", f"{df_filtrado['roe'].mean()*100:.2f}%")
with col2:
    # CORREÇÃO: Multiplicando por 100 para o DY médio não aparecer como 0.07%
    st.metric("DY Médio", f"{df_filtrado['dy'].mean()*100:.2f}%")
with col3:
    st.metric("Margem Líquida Média", f"{df_filtrado['mrgliq'].mean()*100:.2f}%")
with col4:
    # Adicionando o Patrimônio Médio solicitado
    patr_medio = formatar_bilhoes_milhoes(df_filtrado['patrliq'].mean())
    st.metric("Patr. Líquido Médio", patr_medio)

st.divider()

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Eficiência: ROE por Empresa")
    # Multiplicamos por 100 no gráfico para o eixo Y ficar correto
    df_graf = df_filtrado.copy()
    df_graf['roe_pct'] = df_graf['roe'] * 100
    fig_roe = px.bar(df_graf.sort_values('roe_pct'), x='roe_pct', y='Ticker', 
                     orientation='h', color='Segmento',
                     labels={'roe_pct': 'ROE (%)', 'Ticker': 'Ticker'})
    st.plotly_chart(fig_roe, use_container_width=True)

with col_graf2:
    st.subheader("Dividendos: DY por Empresa")
    df_graf['dy_pct'] = df_graf['dy'] * 100
    fig_dy = px.bar(df_graf.sort_values('dy_pct'), x='dy_pct', y='Ticker', 
                    orientation='h', color='Regiao_Atuacao',
                    labels={'dy_pct': 'DY (%)', 'Ticker': 'Ticker'})
    st.plotly_chart(fig_dy, use_container_width=True)

# --- PREPARAÇÃO DA TABELA (df_view) ---
df_view = df_filtrado.copy()

# 1. Transformar decimais em porcentagem (0.20 -> 20.0)
colunas_pct = ['roe', 'dy', 'mrgliq', 'roic', 'mrgebit', 'c5y']
for col in colunas_pct:
    if col in df_view.columns:
        df_view[col] = df_view[col] * 100

# 2. Aplicar formatação de B/M no Patrimônio
df_view['patrliq'] = df_view['patrliq'].apply(formatar_bilhoes_milhoes)

# --- EXIBIÇÃO DA TABELA ---
# --- TABELA FUNDAMENTALISTA PROFISSIONAL ---
st.divider()
st.subheader("📑 Terminal de Indicadores: Visão Completa")

# Lista de colunas na ordem ideal de leitura
colunas_finais = [
    "Ticker", "Empresa", "pl", "pvp", "dy", "roe", "roic", 
    "mrgliq", "mrgebit", "divbpatr", "evebit", "evebitda", "psr", 
    "pa", "pcg", "pebit", "pacl", "liqc", "patrliq", "c5y",
    "Segmento", "Regiao_Atuacao"
]

st.dataframe(
    df_view,
    column_order=colunas_finais,
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Empresa": st.column_config.TextColumn("Empresa", width="medium"),
        
        # Indicadores de Preço (Alinhados e com 2 casas)
        "pl": st.column_config.NumberColumn("P/L", format="%.2f"),
        "pvp": st.column_config.NumberColumn("P/VP", format="%.2f"),
        "psr": st.column_config.NumberColumn("PSR", format="%.2f"),
        
        # Rentabilidade (Já multiplicados por 100 no processamento anterior)
        "dy": st.column_config.NumberColumn("DY (%)", format="%.2f%%"),
        "roe": st.column_config.NumberColumn("ROE (%)", format="%.2f%%"),
        "roic": st.column_config.NumberColumn("ROIC (%)", format="%.2f%%"),
        "mrgliq": st.column_config.NumberColumn("Marg. Líq (%)", format="%.2f%%"),
        "mrgebit": st.column_config.NumberColumn("Marg. EBIT (%)", format="%.2f%%"),
        
        # Dívida e Eficiência
        "divbpatr": st.column_config.NumberColumn("Dív. Bruta/PL", format="%.2f"),
        "evebit": st.column_config.NumberColumn("EV/EBIT", format="%.2f"),
        "evebitda": st.column_config.NumberColumn("EV/EBITDA", format="%.2f"),
        
        # Outros Múltiplos
        "pa": st.column_config.NumberColumn("P/Ativos", format="%.2f"),
        "pcg": st.column_config.NumberColumn("P/Cap. Giro", format="%.2f"),
        "pebit": st.column_config.NumberColumn("P/EBIT", format="%.2f"),
        "pacl": st.column_config.NumberColumn("P/Ativ. Circ", format="%.2f"),
        "liqc": st.column_config.NumberColumn("Liq. Corr.", format="%.2f"),
        
        # Patrimônio e Crescimento
        "patrliq": st.column_config.TextColumn("Patrimônio Líquido", width="medium"),
        "c5y": st.column_config.NumberColumn("Cresc. 5a (%)", format="%.2f%%"),
        
        "Segmento": "Segmento",
        "Regiao_Atuacao": "Região"
    },
    hide_index=True,
    use_container_width=True
)

# --- ANÁLISE TERRITORIAL ---
st.divider()
st.subheader("📊 Presença Territorial por Estado")

df_presenca = df_filtrado.assign(Estado=df_filtrado['Estados_Atuacao'].str.split(',')).explode('Estado')
df_presenca['Estado'] = df_presenca['Estado'].str.strip()

ranking_estados = df_presenca.groupby('Estado').size().reset_index(name='Qtd_Empresas').sort_values('Qtd_Empresas')

fig_presenca = px.bar(
    ranking_estados, 
    x='Qtd_Empresas', 
    y='Estado', 
    orientation='h',
    color='Qtd_Empresas', 
    color_continuous_scale="Viridis",
    labels={'Qtd_Empresas': 'Quantidade de Empresas', 'Estado': 'Estado (UF)'}
)

fig_presenca.update_layout(
    xaxis_title="Quantidade de Empresas",
    yaxis_title="Estado",
    showlegend=False
)

st.plotly_chart(fig_presenca, use_container_width=True)

# --- QUADRO DE RANKING: TOP 5 POR CATEGORIA ---
st.divider()
st.subheader("🏆 Ranking de Performance: Top 5")

# Criando a grade 2x2
col_esq, col_dir = st.columns(2)

# --- LINHA 1 ---
with col_esq:
    with st.container(border=True):
        st.markdown("##### 💰 Maiores Dividend Yield (DY)")
        top_dy = df_filtrado.nlargest(5, 'dy')[['Ticker', 'dy']]
        for _, row in top_dy.iterrows():
            st.write(f"**{row['Ticker']}**: {row['dy']*100:.2f}%")

with col_dir:
    with st.container(border=True):
        st.markdown("##### 📈 Maiores ROE")
        top_roe = df_filtrado.nlargest(5, 'roe')[['Ticker', 'roe']]
        for _, row in top_roe.iterrows():
            st.write(f"**{row['Ticker']}**: {row['roe']*100:.2f}%")

# --- LINHA 2 ---
with col_esq:
    with st.container(border=True):
        st.markdown("##### 🏢 Maiores Patrimônio Líquido")
        top_patr = df_filtrado.nlargest(5, 'patrliq')[['Ticker', 'patrliq']]
        for _, row in top_patr.iterrows():
            valor_formatado = formatar_bilhoes_milhoes(row['patrliq'])
            st.write(f"**{row['Ticker']}**: {valor_formatado}")

with col_dir:
    with st.container(border=True):
        st.markdown("##### 📉 Menores P/L")
        
        # Mantemos a sua lógica de pegar os 5 menores (o 0 da Light entrará aqui)
        top_pl = df_filtrado.nsmallest(5, 'pl')[['Ticker', 'pl']]
        
        for _, row in top_pl.iterrows():
            ticker = row['Ticker']
            valor_pl = row['pl']
            
            # ORIENTAÇÃO: Só aplicamos a cor se for negativo. 
            # Se não for, usamos st.write ou st.markdown simples sem a tag de cor.
            if valor_pl < 0:
                st.markdown(f"**{ticker}**: :red[{valor_pl:.2f}x]")
            else:
                # Aqui o valor 0.00 aparecerá limpo, sem o erro ":white"
                st.write(f"**{ticker}**: {valor_pl:.2f}x")

with col_esq: # Ou a coluna que você desejar posicionar
    with st.container(border=True):
        st.markdown("##### 💎 Menores P/VP")
        
        # Filtramos para garantir que o P/VP exista (não seja nulo)
        df_pvp_valido = df_filtrado[df_filtrado['pvp'].notna()]
        
        # Pegamos as 5 empresas com os menores P/VP (mais baratas patrimonialmente)
        top_pvp = df_pvp_valido.nsmallest(5, 'pvp')[['Ticker', 'pvp']]
        
        for _, row in top_pvp.iterrows():
            ticker = row['Ticker']
            valor_pvp = row['pvp']
            
            # Lógica visual: Se for menor que 1, a empresa está "com desconto"
            # Vamos usar o azul para destacar o que está abaixo do valor patrimonial
            if valor_pvp < 1:
                st.markdown(f"**{ticker}**: :blue[{valor_pvp:.2f}x]")
            else:
                # Se for 1 ou mais, aparece no padrão do sistema sem erro visual
                st.write(f"**{ticker}**: {valor_pvp:.2f}x")
with col_dir: # Ou ajuste para a coluna de sua preferência
    with st.container(border=True):
        st.markdown("##### 🛡️ Menor Endividamento Dív. Bruta/PL")
        
        # Filtramos para garantir que o indicador de dívida exista
        df_div_valida = df_filtrado[df_filtrado['divbpatr'].notna()]
        
        # Pegamos as 5 empresas com menor relação Dívida/Patrimônio
        top_div = df_div_valida.nsmallest(5, 'divbpatr')[['Ticker', 'divbpatr']]
        
        for _, row in top_div.iterrows():
            ticker = row['Ticker']
            valor_div = row['divbpatr']
            
            # Lógica visual: Se for muito baixo (ex: < 0.5), destacamos em verde como "Conservadora"
            if valor_div < 0.5:
                st.markdown(f"**{ticker}**: :green[{valor_div:.2f}]")
            else:
                st.write(f"**{ticker}**: {valor_div:.2f}")
        
# --- ANÁLISE INDIVIDUAL COM COTAÇÃO EM TEMPO REAL ---
st.divider()
st.subheader("🔍 Consulta Individual: Performance em Tempo Real")

# Seletor de Empresa
ticker_selecionado = st.selectbox("Selecione uma empresa:", df_filtrado['Ticker'].unique())

# O Yahoo Finance usa o sufixo .SA para ações brasileiras
ticker_b3 = f"{ticker_selecionado}.SA"

@st.cache_data(ttl=3600)
def buscar_dados_vivos(ticker):
    try:
        import yfinance as yf
        acao = yf.Ticker(ticker)
        hist = acao.history(period="1y")
        return hist
    except Exception:
        return None

historico = buscar_dados_vivos(ticker_b3)

# 1. Bloco de Métricas (Depende do Yahoo Finance)
if historico is not None and not historico.empty:
    preco_atual = historico['Close'].iloc[-1]
    preco_ontem = historico['Close'].iloc[-2]
    preco_mes = historico['Close'].iloc[-21] if len(historico) > 21 else preco_ontem
    preco_ano = historico['Close'].iloc[0]

    var_dia = ((preco_atual / preco_ontem) - 1) * 100
    var_mes = ((preco_atual / preco_mes) - 1) * 100
    var_ano = ((preco_atual / preco_ano) - 1) * 100

    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    
    with col_v1:
        st.metric("Cotação Atual", f"R$ {preco_atual:.2f}", f"{var_dia:.2f}%")
    with col_v2:
        st.metric("Variação Mês", f"{var_mes:.2f}%", delta=f"{var_mes:.2f}%")
    with col_v3:
        # Puxando o DY do seu CSV para comparação
        dy_csv = df_filtrado[df_filtrado['Ticker'] == ticker_selecionado]['dy'].iloc[0]
        st.metric("DY (Base CSV)", f"{dy_csv*100:.2f}%")
    with col_v4:
        st.metric("Variação Ano (YTD)", f"{var_ano:.2f}%", delta=f"{var_ano:.2f}%")
else:
    st.warning(f"Aguardando conexão ou dados indisponíveis para {ticker_selecionado}.")

# 2. Bloco de Detalhes (Gráfico + Fundamentos + Payout)
with st.expander(f"➕ Detalhes de {ticker_selecionado}"):
    dados_ticker = df_filtrado[df_filtrado['Ticker'] == ticker_selecionado].iloc[0]
    
    # Gráfico de Evolução (Mantendo o que já fizemos)
    if historico is not None and not historico.empty:
        st.markdown(f"**Evolução do Preço (12 meses): {ticker_selecionado}**")
        fig_evolucao = px.line(
            historico, x=historico.index, y='Close',
            labels={'Close': 'Preço (R$)', 'Date': 'Data'},
            template="plotly_dark"
        )
        fig_evolucao.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    st.divider()
    
    # Lógica de Cálculo do Payout
    dy_val = dados_ticker['dy']
    pl_val = dados_ticker['pl']
    payout = dy_val * pl_val * 100 # Transformando em porcentagem

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Segmento:** {dados_ticker['Segmento']}")
        st.write(f"**Região:** {dados_ticker['Regiao_Atuacao']}")
        
        # Exibição do Payout com Alerta
        if pl_val > 0:
            if payout > 100:
                st.write(f"**Payout:** {payout:.2f}% ⚠️")
                st.caption("ℹ️ *Atenção: Payout acima de 100% indica uso de reservas ou eventos não recorrentes.*")
            else:
                st.write(f"**Payout:** {payout:.2f}%")
        else:
            st.write(f"**Payout:** N/A (P/L Negativo) ⚠️")
            st.caption("ℹ️ *Empresa em prejuízo contábil; dividendos podem estar sendo pagos via caixa/reservas.*")

    with c2:
        st.write(f"**Patrimônio:** {formatar_bilhoes_milhoes(dados_ticker['patrliq'])}")
        st.write(f"**P/L:** {pl_val:.2f}x")
        st.write(f"**P/VP:** {dados_ticker['pvp']:.2f}x")