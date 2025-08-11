import pandas as pd
import numpy as np
data_path = 'C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data'

# df1 tem os 78000 comentários, um pouco viesado
# df2 tem os 55800 comentários menos viesado
df1 = pd.read_excel(data_path + '/processed/final_sample_4468.xlsx')
df2 = pd.read_excel(data_path + '/processed/final_sample.xlsx')

def calcular_iengajamento(df1):
    # remover linhas com na
    df1 = df1[df1.notna().all(axis=1)]

    # calcular medida de engajamento para cada linha ((likes + comentários)/2)
    df1['TotInt'] = (df1['Likes per post'] + df1['Comments per post']) / 2

    # divisão por zero deixamos como NaN
    df1['PesoCurt'] = np.where(
        (df1['TotInt'] != 0) & (df1['Likes per post'] != 0),
        1 / ((df1['Likes per post'] / df1['TotInt']) * 2),
        np.nan
    )

    df1['PesoCom'] = np.where(
        (df1['TotInt'] != 0) & (df1['Comments per post'] != 0),
        1 / ((df1['Comments per post'] / df1['TotInt']) * 2),
        np.nan
    )

    df1['IEngajamento'] = (df1['Likes per post'] * df1['PesoCurt']) + (df1['Comments per post'] * df1['PesoCom'])
    
    return df1

def show_best_engagement(df1):
    return df1.sort_values(by='IEngajamento', ascending=False)

if __name__ == "__main__":
    df1 = calcular_iengajamento(df1)
    df2 = calcular_iengajamento(df2)
    df1 = show_best_engagement(df1) # -> temos 3992/4468 linhas após filtrar apenas os que tem engajamento > 0
    df2 = show_best_engagement(df2) # -> temos 3710/4024 linhas após filtrar apenas os que tem engajamento > 0

    df1.to_excel(data_path + '/results/01_final_sample_4468_engajamento.xlsx', index=False)
    df2.to_excel(data_path + '/results/01_final_sample_4024_engajamento.xlsx', index=False)
