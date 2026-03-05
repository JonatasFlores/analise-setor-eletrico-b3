import pandas as pd
import sqlite3

def processar_analise_eletrica():
    print("⚙️ Iniciando processamento do setor elétrico...")
    
    # 1. Conecta ao banco geral e pega a foto mais recente
    conn = sqlite3.connect('data/banco_geral_b3.db')
    query = "SELECT * FROM cotacoes_historicas WHERE Data_Snapshot = (SELECT MAX(Data_Snapshot) FROM cotacoes_historicas)"
    df_b3 = pd.read_sql(query, conn)
    conn.close()
    
    # 2. Lê seu mapeamento manual (ISAE, AXIA, etc)
    mapa = pd.read_csv('data/mapeamento_setor_eletrico.csv')
    
    # 3. Faz o JOIN (Cruza a base total com seu filtro)
    df_eletrico = pd.merge(df_b3, mapa, left_on='papel', right_on='Ticker')
    
    # 4. Salva o arquivo final pronto para o Dashboard e Relatório
    df_eletrico.to_csv('data/analise_eletrica_final.csv', index=False)
    
    print(f"📊 Análise pronta! {len(df_eletrico)} elétricas filtradas e segmentadas.")
    print(df_eletrico[['Ticker', 'Segmento', 'dy', 'roe']].head())

if __name__ == "__main__":
    processar_analise_eletrica()