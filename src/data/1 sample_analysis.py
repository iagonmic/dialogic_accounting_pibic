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

models = [
    'meta-llama/llama-4-maverick-17b-128e-instruct',
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'deepseek-r1-distill-llama-70b',
    'meta-llama/llama-4-scout-17b-16e-instruct',
    'qwen-qwq-32b'
]

models_refined = [
    'meta-llama/llama-4-scout-17b-16e-instruct',
]

data_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data"
interim_data = os.path.join(data_path, "interim/")


if os.path.exists(interim_data + 'sample/df_gov_final_sample.xlsx'):
    df = pd.read_excel(interim_data + 'sample/df_gov_final_sample.xlsx')

else:
    file_human = glob(interim_data + "*human.xlsx")[0]
    file_llm = glob(interim_data + "*llm.xlsx")[0]

    df_human = pd.read_excel(file_human).rename(columns={"Unnamed: 0": "Original_index"})
    df_llm = pd.read_excel(file_llm).rename(columns={"Unnamed: 0": "Original_index"})
    
    df = pd.merge(df_human, df_llm, on='Original_index').filter(
        ['Original_index', 'Message_x', 'Informações Financeiras_x']).rename(columns={
            'Original_index': "Original Index",
            'Message_x': "Message",
            'Informações Financeiras_x': "Informação Financeira Humano"   
        })

'''
prompt = ChatPromptTemplate.from_template(
Sua tarefa é classificar o texto fornecido como contendo informação financeira, respondendo "sim", ou não contendo informação financeira, respondendo "não". O critério fundamental para essa classificação é o vínculo direto das ações descritas no texto com recursos financeiros, investimentos, despesas públicas, receitas ou quaisquer ações relacionadas à execução orçamentária.

Uma mensagem deve ser classificada como "sim" se apresentar menções explícitas ou implicitas a valores, investimentos, despesas, ou receitas. Por exemplo, o texto "A semana começou com um café da manhã na Guarda Municipal, onde o prefeito assinou o início do processo licitatório de reforma do prédio. Ainda hoje garantimos equipamentos de controle de distúrbio civil e novos notebooks" é classificado como "sim", pois menciona gastos com reforma e aquisição de materiais, mesmo de maneira implicita. Além disso, a presença de palavras-chave como orçamento, despesa, gasto, impostos, receita ou investimentos automaticamente qualifica a mensagem como "sim".

Por outro lado, mensagens serão classificadas como "não" se descreverem atividades administrativas, eventos, ou ações sem relação com recursos financeiros.
Um exemplo é: "Equipes da Secretaria de Segurança Comunitária e Convívio Social realizaram fiscalização na orla marítima para orientar os trabalhadores sobre a redução de 30% do comércio na região", que é "não" por relatar uma fiscalização.

Existem exclusões importantes que levam à classificação "não".
Mensagens sobre eventos, promoções, feiras, shows e festas devem ser classificadas como "não", mesmo que impliquem gastos públicos, se o foco for a divulgação e não o detalhamento financeiro. 
Palavras como evento, festas, festival, show, programação cultural, carnaval, natal, ano novo, campanha, desconto, promoção, inscrição, divulgação, comunicado, dia, e horário em uma mensagem conduzem à classificação "não". Por exemplo, a postagem "Nosso primeiro Réveillon Ananin tá ON! Confira a programação completa que conta com um grande espetáculo de shows e fogos para toda a família. Quer saber mais? O nosso site oficial, ananews.com.br, tem todas as informações" é "não", pois foca na programação do evento e não em seus custos. Adicionalmente, em contextos específicos como análises de dados de 2021 (auge da pandemia de COVID-19), mensagens relacionadas a vacinação (contendo palavras como vacina, vacinação, vacinado e derivados) devem ser classificadas como "não" para evitar distorções devido ao alto volume, mesmo que envolvam execução orçamentária.
                                          
Lembre-se, se tiver uma menção mesmo que implícita a parte orçamentária, classifique como "sim". Muito importante: para diferenciar, o foco da mensagem é o mais importante, se tiver detalhamento financeiro na mensagem ou planejamento orçamentário concluído, falando de investimentos, despesas, receitas ou algum desses, classifique como "sim", do contrário, classifique como "não".

Analise o texto que será fornecido a seguir e responda apenas com "sim" ou "não".    

Texto: {text}                               

)

'''


prompt_dict = {
    "prompt1":
    ChatPromptTemplate.from_template("""
    Sua tarefa é identificar se o texto a seguir contém informações financeiras ou não financeiras. Responda apenas com "sim" se houver qualquer menção, ainda que implícita, a gastos públicos, investimentos, despesas, receitas, execução orçamentária ou planejamento financeiro. Caso contrário, responda "não".

    Considere como "sim" qualquer menção direta ou indireta a:

    Valores monetários

    Ações governamentais que envolvam recursos (ex: reformas, aquisições, licitações)

    Termos como: orçamento, gasto, despesa, receita, investimento, imposto

    Considere como "não":

    Textos com foco em eventos (ex: feiras, shows, festas, promoções), mesmo que envolvam custo

    Ações informativas sem ligação com uso de recursos financeiros

    Campanhas, comunicados, divulgações e eventos culturais

    Postagens sobre vacinação e saúde pública durante a pandemia de 2021, independentemente de envolverem execução orçamentária

    Exemplos:

    “Foi iniciada a construção da nova escola com recursos do PAC.” → sim

    “A cidade recebe neste sábado a tradicional feira do produtor local.” → não

    Analise o texto e classifique com "sim" ou "não".
    Texto: {text}
    """),
    "prompt2":ChatPromptTemplate.from_template("""
    Classifique o texto fornecido com base na presença de informação financeira, respondendo com "sim" ou "não".

    Responda "sim" apenas quando o foco do conteúdo estiver relacionado ao uso de recursos públicos, como:

    Despesas e receitas públicas

    Investimentos realizados ou planejados

    Compras, licitações ou contratações

    Termos relacionados à execução orçamentária

    Responda "não" quando o texto tratar de:

    Divulgação de eventos, campanhas, festas ou promoções

    Informações administrativas sem conexão orçamentária

    Conteúdos sobre vacinação ou saúde pública durante a pandemia (especialmente em 2021)

    Postagens com foco meramente informativo

    Importante: O foco da mensagem é determinante. Se o texto enfatiza ações financeiras, mesmo que sem valores explícitos, classifique como "sim". Se o foco é descritivo, informativo ou promocional, classifique como "não".

    Texto para análise: {text}

    """),
    "prompt3": ChatPromptTemplate.from_template("""
    Sua tarefa é determinar se o texto a seguir contém informação financeira, com base em seu conteúdo. Responda apenas com "sim" ou "não".

    Considere "sim" se:

    O texto descreve gastos, investimentos, receitas ou execução orçamentária

    Menciona processos como reforma, aquisição de bens, contratos, licitação

    Aparece alguma das seguintes palavras: orçamento, gasto, despesa, receita, investimento, imposto

    Considere "não" se:

    Trata-se de divulgação de eventos, festividades, promoções ou campanhas

    O texto apenas informa datas, locais, horários ou detalhes de atividades públicas

    É uma publicação relacionada à vacinação ou saúde pública em 2021, sem foco financeiro

    Exemplo 1 - "sim": “A prefeitura investiu na construção de duas novas creches com recursos do Fundeb.”
    Exemplo 2 - "não": “Neste sábado acontece o Festival de Verão com shows gratuitos para toda a comunidade.”

    Texto a ser classificado: {text}

    """),
    "prompt_original": ChatPromptTemplate.from_template(
    '''
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
    
    '''),
    "final_prompt": ChatPromptTemplate.from_template("""

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
    """)
}

output_path = os.path.join(data_path, "interim/", "df_gov_final_sample.xlsx")

# inputar colunas
def llm_response(model):
    chat = ChatGroq(model=model)

    for prompt_key, prompt_value in prompt_dict.items():
        column_name = f"{model} - {prompt_key}"
        if column_name not in df.columns:
            df[column_name] = None

        for idx, text in enumerate(tqdm(list(df['Message'].values), desc=f"{model} - {prompt_key}", total=len(df))):
            if pd.notna(df.at[idx, column_name]):
                continue

            resposta = None
            while resposta is None:
                try:
                    resposta = chat.invoke(prompt_value.format_messages(text=text))

                except RateLimitError or InternalServerError:
                    print(f'Rate limit atingido, retornando função')
                    return df

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

            df.at[idx, column_name] = resposta_final

            sleep(randint(2,4))
            df.to_excel(output_path, index=False)
    
    return df

for model in models_refined:
    df = llm_response(model)


# calcular taxa de acerto
accuracy_dict = {'Original Index': 'Model Accuracy', 'Message': None, 'Informação Financeira Humano': None}
for col in df.columns:
    if any(model in col for model in models):
        correct = df[col].str.lower() == df['Informação Financeira Humano'].str.lower()
        accuracy_dict[col] = f"{correct.mean():.2f}%"

pd.DataFrame.from_dict(accuracy_dict, orient='index', columns=['accuracy']).iloc[3:].to_excel(interim_data + 'sample/model_accuracy.xlsx')

