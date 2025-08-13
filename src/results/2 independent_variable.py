import pandas as pd
import re
from ast import literal_eval
from LeIA import SentimentIntensityAnalyzer
profile_to_estado = {
    'Estado do Paraná': 'Paraná',
    'Governo SP': 'São Paulo',
}

analyzer = SentimentIntensityAnalyzer()

def classify_3(text: str) -> str:
    text_lower = str(text).lower()
    money_flag = ("r$" in text_lower) or ("milhão" in text_lower) or ("milhões" in text_lower)
    numeric_flag = bool(re.search(r'\d+', text_lower))

    if money_flag:
        return "Alto detalhe"
    elif numeric_flag:
        return "Médio detalhe"
    else:
        return "Baixo detalhe"

def classify_5_inverted(text: str) -> str:
    text_lower = str(text).lower()
    money_flag = ("r$" in text_lower) or ("milhão" in text_lower) or ("milhões" in text_lower)
    tech_pattern = r'(m2|m²|\bkm\b|metros|canaleta|ciclovia|ciclofaixa|pavimenta|muro de arrimo)'
    tech_flag = bool(re.search(tech_pattern, text_lower))
    time_flag = bool(re.search(r'\b20[0-9]{2}\b', text_lower)) or ("desde" in text_lower)
    numeric_flag = bool(re.search(r'\d+', text_lower))

    if money_flag:
        if tech_flag and time_flag:
            return "Nível 5 (Extremo Detalhe)"
        elif tech_flag or time_flag:
            return "Nível 4 (Alto Detalhe)"
        else:
            return "Nível 3 (Detalhe Moderado/Médio)"
    else:
        if tech_flag and time_flag:
            return "Nível 3 (Detalhe Moderado/Médio)"
        elif numeric_flag:
            return "Nível 2 (Baixo Detalhe Intermediário)"
        else:
            return "Nível 1 (Mínimo ou Genérico)"
        
def content_type_classification(url: str) -> str:
    if re.search(r'/p/', url):
        return "Imagem"
    elif re.search(r'/reel/', url):
        return "Vídeo"
    else:
        return "Outro"
    
def post_frequency(df):
    # Conta posts por dia por perfil
    posts_per_year = df1.groupby(['Profile']).size().reset_index(name='posts_per_day')
    posts_per_year['posts_per_day'] = posts_per_year['posts_per_day'] / 365
    df = df.merge(posts_per_year, on='Profile', how='left')
    return df
        
def period_of_day(dt):
    # Aceita string ou datetime
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    hour = dt.hour
    if 6 <= hour < 12:
        return 'Manhã'
    elif 12 <= hour < 18:
        return 'Tarde'
    elif 18 <= hour < 24:
        return 'Noite'
    else:
        return 'Madrugada'
    
def count_hashtags(text):
    # Conta o número de hashtags em uma string
    return len(re.findall(r'#\w+', str(text)))

def count_syllables(word):
    # Conta sílabas de forma simples: cada grupo de vogais conta como uma sílaba
    return len(re.findall(r'[aeiouáéíóúãõâêôàü]+', word.lower()))

def flesch_index(text):
    # Divide o texto em sentenças usando . ! ou ? como separadores
    sentences = re.split(r'[.!?]+', str(text))
    # Remove sentenças vazias após a divisão
    sentences = [s for s in sentences if s.strip()]
    # Encontra todas as palavras no texto (sequências alfanuméricas)
    words = re.findall(r'\w+', str(text))
    # Conta o número total de palavras
    num_words = len(words)
    # Conta o número de sentenças, se não houver considera 1 para evitar divisão por zero
    num_sentences = len(sentences) if len(sentences) > 0 else 1
    # Conta o número total de sílabas em todas as palavras usando count_syllables
    num_syllables = sum(count_syllables(word) for word in words) if num_words > 0 else 1

    # Calcula a média de sílabas por palavra (SIP)
    sip = num_syllables / num_words if num_words > 0 else 0
    # Calcula a média de palavras por sentença (PSE)
    pse = num_words / num_sentences if num_sentences > 0 else 0

    # Aplica a fórmula do Índice de Flesch adaptado para português
    IF = 206.835 - 84.6 * sip - 1.015 * pse + 42
    # Retorna o valor do índice de legibilidade calculado
    return IF

def has_call_to_action(text):
    # Lista de palavras-chave que incentivam interação
    keywords = [
        'comente',
        'compartilhe',
        'opinião',
        'comentário',
        'participe',
        'conte',
        'escreva'
    ]
    # Verifica se alguma palavra-chave aparece no texto (case insensitive)
    text_lower = str(text).lower()
    for kw in keywords:
        if kw in text_lower:
            return 1
    return 0

def check_gov_comment(comments, arroba_governo):
    """
    Retorna 1 se algum dicionário da lista comments tem 'user' igual ao arroba_governo, senão 0.
    """
    if not isinstance(comments, list) or pd.isna(arroba_governo):
        return 0
    for comment in comments:
        if isinstance(comment, dict) and comment.get('user') == arroba_governo:
            return 1
    return 0

def sentimento_media_sem_neutros(lista_comentarios):
    # Se não for lista, retorna 0
    if not isinstance(lista_comentarios, list) or len(lista_comentarios) == 0:
        return 0
    compounds = []
    for comentario in lista_comentarios:
        # Pega o texto do comentário (pode ser 'comment' ou 'message')
        texto = comentario.get('message')
        if texto:
            score = analyzer.polarity_scores(str(texto))['compound']
            if abs(score) > 0.05:  # exclui neutros
                compounds.append(score)
    if not compounds:  # se não sobrou nada, retorna neutro (0)
        return 0
    media = sum(compounds) / len(compounds)
    return 1 if media > 0 else 0

def safe_literal_eval(x):
    if isinstance(x, str) and x.strip().startswith('['):
        try:
            return literal_eval(x)
        except Exception:
            return []
    elif isinstance(x, float) and pd.isna(x):
        return []
    return x

if __name__ == "__main__":
    # leitura dos dataframes
    data_path = 'C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data'
    df1 = pd.read_excel(data_path + '/results/01_final_sample_4468_engajamento.xlsx')
    df2 = pd.read_excel(data_path + '/results/01_final_sample_4024_engajamento.xlsx')
    df_link = pd.read_excel(data_path + '/links.xlsx')

    df1['Comentários'] = df1['Comentários'].apply(safe_literal_eval)
    df2['Comentários'] = df2['Comentários'].apply(safe_literal_eval)

    df1['Profile'] = df1['Profile'].str.replace(r'^Governo (do|de|da) ', '', regex=True)
    df2['Profile'] = df2['Profile'].str.replace(r'^Governo (do|de|da) ', '', regex=True)

    df_link['Arroba-Governo'] = df_link['INSTAGRAM'].str.extract(r'/([^/]+)/?$')

    df1['Profile'] = df1['Profile'].replace(profile_to_estado)
    df2['Profile'] = df2['Profile'].replace(profile_to_estado)

    # Faz o merge usando o nome do estado extraído de Profile e o nome do estado do df_link
    df1 = df1.merge(df_link.filter(['NOME DO ESTADO', 'Arroba-Governo']), left_on='Profile', right_on='NOME DO ESTADO', how='left').drop(columns=['NOME DO ESTADO'], errors='ignore')
    df2 = df2.merge(df_link.filter(['NOME DO ESTADO', 'Arroba-Governo']), left_on='Profile', right_on='NOME DO ESTADO', how='left').drop(columns=['NOME DO ESTADO'], errors='ignore')

    #### Atenção, aqui houve uma diminuição dos estados, não houve coleta de dados o suficiente para todos

    # variável 1 - detalhamento do conteúdo
    df1['classify_3'] = df1['Message'].apply(classify_3)
    df1['classify_5_inverted'] = df1['Message'].apply(classify_5_inverted)
    df2['classify_3'] = df2['Message'].apply(classify_3)
    df2['classify_5_inverted'] = df2['Message'].apply(classify_5_inverted)

    # variável 2 - tipo de conteúdo
    df1['content_type'] = df1['Link'].apply(content_type_classification)
    df2['content_type'] = df2['Link'].apply(content_type_classification)

    # variável 3 - frequência de posts
    df1 = post_frequency(df1)
    df2 = post_frequency(df2)

    # variável 4 - período do dia
    df1['period_of_day'] = df1['Date'].apply(period_of_day)
    df2['period_of_day'] = df2['Date'].apply(period_of_day)

    # variável 5 - quantidade de hashtags
    df1['num_hashtags'] = df1['Message'].apply(count_hashtags)
    df2['num_hashtags'] = df2['Message'].apply(count_hashtags)

    # variável 6 - índice de Flesch
    df1['flesch_index'] = df1['Message'].apply(flesch_index)
    df2['flesch_index'] = df2['Message'].apply(flesch_index)

    # variável 7 - chamada para ação
    df1['call_to_action'] = df1['Message'].apply(has_call_to_action)
    df2['call_to_action'] = df2['Message'].apply(has_call_to_action)

    # variável 8 - interação dialógica
    df1['gov_commented'] = df1.apply(lambda row: check_gov_comment(row['Comentários'], row['Arroba-Governo']), axis=1)
    df2['gov_commented'] = df2.apply(lambda row: check_gov_comment(row['Comentários'], row['Arroba-Governo']), axis=1)

    # variável 9 - análise de sentimento
    df1['mean_comment_sentiment'] = df1['Comentários'].apply(sentimento_media_sem_neutros)
    df2['mean_comment_sentiment'] = df2['Comentários'].apply(sentimento_media_sem_neutros)

df1.to_excel(data_path + '/results/2_independent_variable_4468.xlsx', index=False)
df2.to_excel(data_path + '/results/2_independent_variable_4024.xlsx', index=False)