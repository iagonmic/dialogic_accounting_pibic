import pandas as pd
import re

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
    posts_per_year = df1.groupby(['Profile']).size().reset_index(name='posts_per_year')
    posts_per_year['posts_per_year'] = posts_per_year['posts_per_year'] / 365
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

if __name__ == "__main__":
    # leitura dos dataframes
    data_path = 'C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data'
    df1 = pd.read_excel(data_path + '/results/01_final_sample_4468_engajamento.xlsx')
    df2 = pd.read_excel(data_path + '/results/01_final_sample_4024_engajamento.xlsx')

    df_list = [df1, df2]

    for df in df_list:
        # variável 1 - detalhamento do conteúdo
        df['classify_3'] = df['Message'].apply(classify_3)
        df['classify_5_inverted'] = df['Message'].apply(classify_5_inverted)

        # variável 2 - tipo de conteúdo
        df['content_type'] = df['Link'].apply(content_type_classification)

        # variável 3 - frequência de posts
        df = post_frequency(df)

        # variável 4 - período do dia
        df['period_of_day'] = df['Date'].apply(period_of_day)

        # variável 5 - quantidade de hashtags
        df['num_hashtags'] = df['Message'].apply(count_hashtags)

        # variável 6 - índice de Flesch
        df['flesch_index'] = df['Message'].apply(flesch_index)

        # variável 7 - chamada para ação
        df['call_to_action'] = df['Message'].apply(has_call_to_action)

        # variável 8 - 