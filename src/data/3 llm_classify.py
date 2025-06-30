import os
import pandas as pd
from glob import glob
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from groq import RateLimitError, InternalServerError
from langchain_core.prompts import ChatPromptTemplate
from random import randint
from time import sleep
import re
from tqdm import tqdm

load_dotenv(find_dotenv())

model = 'meta-llama/llama-4-scout-17b-16e-instruct'
data_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/"
output_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/interim/2024_classified/"

files = glob(data_path + 'interim/2024/' + '*.xlsx')

final_prompt = ChatPromptTemplate.from_template(
'''
Sua tarefa é determinar se o texto a seguir contém informação financeira, com base em seu conteúdo. Responda apenas com "sim" ou "não".

Considere "sim" se:

O texto descreve gastos, investimentos, receitas ou execução orçamentária

Menciona processos como reforma, aquisição de bens, contratos, licitação, entrega de etapa de reforma ou reparo, obra, fase de obra, iniciativa, novas unidades

Aparece alguma das seguintes palavras: orçamento, gasto, despesa, receita, investimento, imposto, recursos, contemplação

Considere "não" se:

Trata-se de divulgação de eventos, festividades, promoções, campanhas, sorteios, jogo beneficente, negociação de dívidas

O texto apenas informa datas, locais, horários ou detalhes de atividades públicas

É uma publicação relacionada à vacinação ou saúde pública em 2021, sem foco financeiro

Exemplo 1 - "sim": “A prefeitura investiu na construção de duas novas creches com recursos do Fundeb.”
Exemplo 2 - "não": “Neste sábado acontece o Festival de Verão com shows gratuitos para toda a comunidade.”

Se houver palavras que classifiquem mais como "sim" do que "não", classifique como "sim"

Texto a ser classificado: {text}
''')

def llm_response(df:pd.DataFrame, model, file_name):
    chat = ChatGroq(model=model)

    if 'Informação Financeira' not in df.columns:
        df['Informação Financeira'] = None

    sample = df.sample(int(len(df)*0.05) + 1, random_state=1)

    for idx, row in tqdm(sample.iterrows(), desc=f"{file_name}", total=len(sample)):
        text = row['Message']
        
        if pd.notna(sample.at[idx, 'Informação Financeira']):
            continue

        resposta = None
        while resposta is None:
            try:
                resposta = chat.invoke(final_prompt.format_messages(text=text))

            except RateLimitError or InternalServerError:
                print(f'Rate limit atingido, retornando função')
                #return df

            except Exception as e:
                print(f'Deu erro, exceção do tipo: {e}. Dormindo 20s...')
                print(f'{type(e).__name__}')
                sleep(20)

        if re.search(pattern=r'\bsim\b', string=resposta.content, flags=re.IGNORECASE):
            resposta_final = 'Sim'
        elif re.search(pattern=r'\bnão\b', string=resposta.content, flags=re.IGNORECASE):
            resposta_final = 'Não'
        else:
            resposta_final = None

        sample.at[idx, 'Informação Financeira'] = resposta_final

        df.update(sample)
        df.to_excel(output_path + file_name, index=False)

        sleep(randint(1, 2))
    
    return df

for file in files:
    file_name = file.split('\\')[-1]
    df = pd.read_excel(file)
    llm_response(df, model, file_name)