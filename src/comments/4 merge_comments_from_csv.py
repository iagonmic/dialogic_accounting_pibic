import pandas as pd
from ast import literal_eval

df_comments = pd.read_csv('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/comentarios_apify.csv')
df1 = pd.read_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample.xlsx')
df2 = pd.read_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample_4468.xlsx')

df_list = [df1, df2]

def safe_get_username(row):
    # Verifica se o campo user não é NaN
    if pd.isna(row['user']):
        return {'comment': row['message'], 'user': None}
    try:
        user_dict = literal_eval(row['user'])
        username = user_dict.get('username', None)
    except Exception:
        username = None
    return {'comment': row['message'], 'user': username}

df_comments['Comentários'] = df_comments.apply(safe_get_username, axis=1)

for df in df_list:
    df['postid'] = df['Link'].str.extract(r'/([^/]+)/?$')
    df['Comentários'] = df_comments['Comentários']

df1.to_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample.xlsx', index=False)
df2.to_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample_4468.xlsx', index=False)
