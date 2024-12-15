import pandas as pd
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from groq import RateLimitError
from dotenv import load_dotenv, find_dotenv
from time import sleep
from random import randint, choice
import os

print(os.getcwd())

df = pd.read_excel('classification/Aracaju.xlsx', engine='openpyxl')

load_dotenv(find_dotenv())

models = [
    'llama-3.1-70b-versatile',
    'llama-3.3-70b-versatile',
    'llama3-groq-70b-8192-tool-use-preview',
    'llama-3.2-11b-text-preview',
    'llama-3.2-90b-text-preview'
]

chat = ChatGroq(model='llama-3.1-70b-versatile')

prompt = ChatPromptTemplate.from_template('''
Você é um analista de dados, trabalhando em um projeto de dados.
Seu trabalho é analisar o texto que vou te enviar e você classificará esse texto
como sendo uma informação financeira ou não, baseado no conteúdo do texto.
                                      
Esses textos foram retirados de postagens feitas nas redes sociais de prefeituras localizadas
em diversos estados do Brasil.                                                                          
                                    
Se for uma informação financeira, você retornará "sim", se não for, você retornará "não"

Texto:
{text}
                                          
Responda apenas com 'sim' ou 'não' apenas.                                          
'''
)

response_list = []
for text in list(df['Message'].values):
    resposta = None
    while resposta is None:
        try:
            resposta = chat.invoke(prompt.format_messages(text=text))

        except RateLimitError:
            new_model = choice(models)
            print(f'Escolhendo novo modelo: {new_model}')
            chat = ChatGroq(model=new_model)
            sleep(5)
            resposta = chat.invoke(prompt.format_messages(text=text))

        except Exception as e:
            print(f'Deu erro, exceção do tipo: {e}. Dormindo 30s...')
            print(f'{type(e).__name__}')
            sleep(20)

    response_list.append(resposta.content[:3].lower())
    sleep(randint(2,4))
    print(len(response_list), resposta.content)

df['Retorno'] = response_list

df.to_excel('classification/Aracaju_finish.xlsx')

