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
    
def post_frequency():
    pass
        
        
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

        # variável 3 - 