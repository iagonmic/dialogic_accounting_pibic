import pandas as pd
from ast import literal_eval

df_comments = pd.read_csv('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/comentarios_apify.csv')
df1 = pd.read_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample.xlsx')
df2 = pd.read_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample_4468.xlsx')

df_list = [df1, df2]

df_comments_subset = df_comments[['postId', 'message', 'user']]

# Agrupa por postId e cria uma lista de dicionários para cada postId
grouped_comments = df_comments_subset.groupby('postId').apply(
    lambda x: x[['message', 'user']].to_dict('records')
).reset_index(name='Comentários')

def extract_comment_and_username(comment_list):
    # Se não for lista (por exemplo, NaN), retorna vazio
    if not isinstance(comment_list, list):
        return []
    result = []
    for item in comment_list:
        message = item.get('message')
        user = item.get('user')
        if isinstance(user, str):
            try:
                user = literal_eval(user)
            except Exception:
                user = {}
        username = user.get('username') if isinstance(user, dict) else None
        result.append({'message': message, 'user': username})
    return result

df1['postId'] = df1['Link'].str.extract(r'/([^/]+)/?$')
df1 = df1.merge(grouped_comments, on='postId', how='outer')
df1 = df1.drop(columns=['Comentários_x', 'Comentários', 'postid', 'level_0', 'index'], errors='ignore').rename(columns={'Comentários_y': 'Comentários'})
df1['Comentários'] = df1['Comentários'].apply(extract_comment_and_username)

df2['postId'] = df2['Link'].str.extract(r'/([^/]+)/?$')
df2 = df2.merge(grouped_comments, on='postId', how='outer')
df2 = df2.drop(columns=['Comentários_x', 'Comentários', 'postid', 'level_0', 'index'], errors='ignore').rename(columns={'Comentários_y': 'Comentários'})
df2['Comentários'] = df2['Comentários'].apply(extract_comment_and_username)

df1.to_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample.xlsx', index=False)
df2.to_excel('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/processed/final_sample_4468.xlsx', index=False)