import pandas as pd
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from groq import RateLimitError, InternalServerError
from dotenv import load_dotenv, find_dotenv
from time import sleep
from random import randint, choice
import os
import glob

load_dotenv(find_dotenv())

model = 'llama-3.3-70b-versatile',

chat = ChatGroq(model='deepseek-r1-distill-llama-70b')

prompt = ChatPromptTemplate.from_template('''
Sua tarefa é classificar o texto fornecido como contendo informação financeira, respondendo "sim", ou não contendo informação financeira, respondendo "não". O critério fundamental para essa classificação é o vínculo direto das ações descritas no texto com recursos financeiros, investimentos, despesas públicas, receitas ou quaisquer ações relacionadas à execução orçamentária.

Uma mensagem deve ser classificada como "sim" se apresentar menções explícitas ou implicitas a valores, investimentos, despesas, ou receitas. Por exemplo, o texto "A semana começou com um café da manhã na Guarda Municipal, onde o prefeito assinou o início do processo licitatório de reforma do prédio. Ainda hoje garantimos equipamentos de controle de distúrbio civil e novos notebooks" é classificado como "sim", pois menciona gastos com reforma e aquisição de materiais, mesmo de maneira implicita. Além disso, a presença de palavras-chave como orçamento, despesa, gasto, impostos, receita ou investimentos automaticamente qualifica a mensagem como "sim".

Por outro lado, mensagens serão classificadas como "não" se descreverem atividades administrativas, eventos, ou ações sem relação com recursos financeiros.
Um exemplo é: "Equipes da Secretaria de Segurança Comunitária e Convívio Social realizaram fiscalização na orla marítima para orientar os trabalhadores sobre a redução de 30% do comércio na região", que é "não" por relatar uma fiscalização.

Existem exclusões importantes que levam à classificação "não".
Mensagens sobre eventos, promoções, feiras, shows e festas devem ser classificadas como "não", mesmo que impliquem gastos públicos, se o foco for a divulgação e não o detalhamento financeiro. 
Palavras como evento, festas, festival, show, programação cultural, carnaval, natal, ano novo, campanha, desconto, promoção, inscrição, divulgação, comunicado, dia, e horário em uma mensagem conduzem à classificação "não". Por exemplo, a postagem "Nosso primeiro Réveillon Ananin tá ON! Confira a programação completa que conta com um grande espetáculo de shows e fogos para toda a família. Quer saber mais? O nosso site oficial, ananews.com.br, tem todas as informações" é "não", pois foca na programação do evento e não em seus custos. Adicionalmente, em contextos específicos como análises de dados de 2021 (auge da pandemia de COVID-19), mensagens relacionadas a vacinação (contendo palavras como vacina, vacinação, vacinado e derivados) devem ser classificadas como "não" para evitar distorções devido ao alto volume, mesmo que envolvam execução orçamentária.
                                          
Lembre-se, se tiver uma menção mesmo que implícita a parte orçamentária, classifique como "sim".

Analise o texto que será fornecido a seguir e responda apenas com "sim" ou "não".    

Texto: {text}                               
'''
)

file_path = 'fanpage-data/processed/'
files = glob.glob(os.path.join(os.path.abspath(file_path), '*.xlsx'))

for i, file in enumerate(files):
    df = pd.read_excel(file).sample(n=200)

    response_list = []
    for text in list(df['Message'].values):
        resposta = None
        while resposta is None:
            try:
                resposta = chat.invoke(prompt.format_messages(text=text))

            except RateLimitError or InternalServerError:
                new_model = choice(models)
                print(f'Escolhendo novo modelo: {new_model}')
                chat = ChatGroq(model=new_model)
                sleep(5)
                resposta = chat.invoke(prompt.format_messages(text=text))

            except Exception as e:
                print(f'Deu erro, exceção do tipo: {e}. Dormindo 20s...')
                print(f'{type(e).__name__}')
                sleep(20)

        resposta_final = resposta.content[-3:].capitalize()

        response_list.append(resposta_final)
        sleep(randint(2,4))
        print(len(response_list), resposta_final)

    df['Informação Financeira'] = response_list

    df.to_excel('classification/classificated/' + file.split('\\')[-1], index=False)


