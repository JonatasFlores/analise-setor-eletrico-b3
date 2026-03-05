import fundamentus
import pandas as pd
import sqlite3
from datetime import datetime

def coletar_base_total_b3():
    print("🌐 Coletando dados brutos de todas as empresas da B3...")
    
    # 1. Busca TUDO da B3
    df_bruto = fundamentus.get_resultado()
    df_bruto = df_bruto.reset_index()
    
    # 2. Adiciona a data da coleta (Snapshot)
    df_bruto['Data_Snapshot'] = datetime.now().strftime('%Y-%m-%d')
    
    # 3. Salva no seu Banco de Dados Histórico (Data Lake)
    conn = sqlite3.connect('data/banco_geral_b3.db')
    df_bruto.to_sql('cotacoes_historicas', conn, if_exists='append', index=False)
    conn.close()
    
    print(f"✅ {len(df_bruto)} ativos salvos com sucesso no histórico.")
    return df_bruto

if __name__ == "__main__":
    coletar_base_total_b3()