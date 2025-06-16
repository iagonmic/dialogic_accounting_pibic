import pandas as pd
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv, find_dotenv
from time import sleep
import os
import glob
from tqdm.auto import tqdm # Importe tqdm

load_dotenv(find_dotenv())

chat_model_name = 'llama3.1:8b' # Certifique-se de que este é o nome correto do seu modelo no Ollama
chat = ChatOllama(model=chat_model_name)

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

file_path = 'files'
files = glob.glob(os.path.join(os.path.abspath(file_path), '*.xlsx'))

for i, file in enumerate(files):
    df = pd.read_excel(file)
    #df = df[(df['Date'] > '2024-01-01') & (df['Date'] < '2024-12-31')].reset_index(drop=True)

    batch_inputs = []
    for text in df['Message'].values:
        formatted_prompt = prompt.format_messages(text=text)
        batch_inputs.append(formatted_prompt)

    file_name = os.path.basename(file)
    print(f"\n--- Processando o arquivo: {file_name} ---")
    print(f"Total de mensagens no lote: {len(batch_inputs)}")

    response_list = []
    try:
        # Dividindo o lote em pedaços menores para exibir o progresso com tqdm
        # O tamanho do sub-lote (chunk_size) pode ser ajustado.
        # Um chunk_size muito pequeno pode adicionar overhead. Um chunk_size muito grande
        # pode não atualizar a barra com frequência suficiente.
        chunk_size = 50 # Exemplo: processe 50 mensagens por vez

        # Crie um iterador para os chunks
        chunks = [batch_inputs[j:j + chunk_size] for j in range(0, len(batch_inputs), chunk_size)]

        # Use tqdm para envolver o loop sobre os chunks
        # O `desc` adiciona um rótulo à barra de progresso
        for chunk_index, chunk in enumerate(tqdm(chunks, desc=f"Processando {file_name}", unit="chunks")):
            chunk_responses = chat.batch(chunk)
            for resposta_msg in chunk_responses:
                resposta_final = resposta_msg.content.strip().lower()
                if "sim" in resposta_final:
                    response_list.append("Sim")
                elif "não" in resposta_final or "nao" in resposta_final:
                    response_list.append("Não")
                else:
                    response_list.append("Inconclusivo")

    except Exception as e:
        print(f"\nOcorreu um erro durante a inferência em lote para {file_name}: {e}")
        response_list = ["Erro na Classificação"] * len(batch_inputs)

    if len(response_list) != len(df):
        print(f"\nAtenção: O número de respostas ({len(response_list)}) não corresponde ao número de prompts ({len(df)}) em {file_name}. Preenchendo com erros.")
        while len(response_list) < len(df):
            response_list.append("Erro na Classificação")

    df['Informação Financeira'] = response_list

    output_dir = 'classification/'
    os.makedirs(output_dir, exist_ok=True)

    output_file_name = os.path.basename(file)
    df.to_excel(os.path.join(output_dir, output_file_name), index=False)
    print(f"\nArquivo '{output_file_name}' classificado e salvo.")
    # Removido o sleep(randint(5, 10)) para não atrasar desnecessariamente

print("\nProcessamento concluído para todos os arquivos.")