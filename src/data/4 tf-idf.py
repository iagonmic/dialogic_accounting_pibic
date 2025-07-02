import pandas as pd
import os
from tkinter import Tk, filedialog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from glob import glob

# Baixar as stop words do nltk (se ainda não tiver)
from nltk.corpus import stopwords

# Função para selecionar o arquivo Excel manualmente
def escolher_arquivo():
    root = Tk()
    root.withdraw()
    caminho_inicial = r"C:"
    arquivo = filedialog.askopenfilename(initialdir=caminho_inicial,
                                         title="Selecione o arquivo Excel",
                                         filetypes=[("Arquivos Excel", "*.xlsx")])
    return arquivo

# Função para classificar a similaridade utilizando TF-IDF com similaridade de cosseno
def classificar_similaridade(texto, referencias, classificacoes, limite_similaridade=0.90):
    if pd.isna(texto):
        return 'Não'

    # Obter as stopwords em português do NLTK
    stop_words = stopwords.words('portuguese')

    # Inicializar o vetor TF-IDF com stop_words em português
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    textos_comparar = [texto] + referencias
    tfidf_matrix = vectorizer.fit_transform(textos_comparar)

    # Calcular a similaridade de cosseno
    cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    # Verificar se a similaridade excede o limite e a classificação da referência é 'Sim'
    for i, sim in enumerate(cos_sim[0]):
        if sim >= limite_similaridade and classificacoes[i] == 'Sim':
            return 'Sim'

    return 'Não'

# Função para verificar se a mensagem é relacionada a finanças
def verificar_informacao_financeira(texto):
    if not isinstance(texto, str):  # Verifica se o texto é uma string
        return 'Não'

    palavras_chave = [
        '%', 'R$', 'acessada', 'acessadas', 'acessado', 'acessados', 'acessam', 'acessar', 'acessibilidade', 'acessibilidades',
        'ajustada', 'ajustadas', 'ajustado', 'ajustados', 'ajustam', 'ajustar', 'ajuste', 'ajustes', 'ajustamos', 'ajustando',
        'alterada', 'alteradas', 'alterado', 'alterados', 'alteram', 'alterar', 'alteração', 'alterações', 'alteramos', 'alterando',
        'arrecadada', 'arrecadadas', 'arrecadado', 'arrecadados', 'arrecadação', 'arrecadamos', 'arrecadando',
        'asfaltam', 'asfaltamento', 'asfaltamentos', 'asfaltar', 'asfalto', 'asfaltamos',  'asfatando',
        'capital', 'capitalização', 'capitalizações',
        'contratada', 'contratadas', 'contratado', 'contratados', 'contratam', 'contratante', 'contratantes',
        'contratar', 'contrato', 'contratos', 'contratual', 'contratamos',
        'conveniada', 'conveniadas', 'conveniado', 'conveniados', 'conveniam', 'conveniar', 'convenios', 'convênio',
        'desembolsada', 'desembolsadas', 'desembolsado', 'desembolsados', 'desembolsam', 'desembolsar', 'desembolso', 'desembolsos',
        'desenbolsamos', 'desembolsando',
        'despendida', 'despendidas', 'despendido', 'despendidos', 'despendemos', 'despêndio',
        'despesa', 'despesa pública', 'despesas', 'despesas públicas',
        'entrega', 'entregam', 'entregar', 'entregas', 'entregou', 'entregue', 'entregues', 'entregamos', 'entregando',
        'espaço público',
        'estrutura', 'estruturam', 'estruturar', 'estruturamos', 'estruturando',
        'financiada', 'financiado', 'financiadores', 'financiam', 'financiamento', 'financiamentos', 'financiar', 'financiamos', 'financiando',
        'gastada', 'gastadas', 'gastado', 'gastam', 'gastar', 'gasto', 'gastos', 'gastamos', 'gastando',
        'iluminada', 'iluminadas', 'iluminado', 'iluminados', 'iluminam', 'iluminar', 'iluminação', 'iluminação pública',
        'iluminações', 'iluminamos', 'iluminando',
        'imposto', 'impostos',
        'infraestrutura', 'infraestrutura urbana', 'infraestruturas',
        'inovada', 'inovadas', 'inovado', 'inovados', 'inovam', 'inovar', 'inovação', 'inovações', 'inovamos', 'inovando',
        'investem', 'investida', 'investido', 'investidores', 'investimento', 'investimentos', 'investir', 'investimos', 'investindo',
        'iptu', 'iss', 'itbi',
        'licitadas', 'licitado', 'licitados', 'licitam', 'licitar', 'licitatório', 'licitatórios', 'licitação', 'licitamos',
        'mantem', 'manter', 'mantida', 'mantidas', 'mantido', 'mantidos', 'mantemos',
        'manutenção', 'manutenções',
        'melhorada', 'melhoradas', 'melhorado', 'melhorados', 'melhoram', 'melhorar', 'melhoria', 'melhoria de infraestrutura',
        'melhorias', 'melhoramos', 'melhorando',
        'mil', 'milhão', 'milhões',
        'mobilidade', 'mobilidades',
        'modernização', 'modernizar', 'modernizado', 'modernizada', 'modernizados', 'modernizadas', 'modernizamos', 'modernizando',
        'monetário', 'monetários',
        'mudança', 'mudar', 'mudado', 'mudada', 'mudados', 'mudadas', 'mudamos',
        'obra', 'obras',
        'orçamento', 'orçamentário', 'orçamentação', 'orçamentária',
        'pavimentação', 'pavimentar', 'pavimentado', 'pavimentada', 'pavimentados', 'pavimentadas', 'pavimentamos', 'pavimentando',
        'projeto', 'projetar', 'projetado', 'projetada', 'projetados', 'projetadas', 'projetamos', 'projetando',
        'readequada', 'readequadas', 'readequado', 'readequados', 'readequam', 'readequar', 'readequação', 'readequações',
        'readequamos', 'readequando',
        'recapeada', 'recapeadas', 'recapeados', 'recapeamento', 'recapeamento asfáltico', 'recapeamentos', 'recapeamos','recapeando',
        'receita', 'receitas',
        'recondicionada', 'recondicionadas', 'recondicionado', 'recondicionados', 'recondicionam', 'recondicionar',
        'recondicionamos', 'recondicionando',
        'reconstruem', 'reconstruir', 'reconstrução', 'reconstruções', 'reconstruída', 'reconstruídas',
        'reconstruído', 'reconstruídos', 'recostruímos', 'reconstruindo',
        'recuperada', 'recuperadas', 'recuperado', 'recuperados', 'recuperam', 'recuperar',
        'recuperação', 'recuperações', 'recuperamos', 'recuperando',
        'reestruturada', 'reestruturadas', 'reestruturado', 'reestruturados', 'reestruturam',
        'reestruturar', 'reestruturação', 'reestruturações', 'reestruturamos', 'reestruturando',
        'reforma', 'reformada', 'reformadas', 'reformado', 'reformadores', 'reformados', 'reformam', 'reformar', 'reformas',
        'reformamos', 'reformando',
        'reformulada', 'reformuladas', 'reformulado', 'reformulados', 'reformulam',
        'reformular', 'reformulação', 'reformulamos', 'reformulando',
        'renovada', 'renovadas', 'renovado', 'renovados', 'renovam', 'renovar', 'renovação', 'renovações', 'renovamos', 'renovando',
        'reorganizada', 'reorganizadas', 'reorganizado', 'reorganizados', 'reorganizam', 'reorganizar', 'reorganização',
        'reorganizações', 'reorganizamos', 'reorganizando',
        'requalificada', 'requalificadas', 'requalificado', 'requalificados', 'requalificam', 'requalificar',
        'requalificação', 'requalificações', 'requalificamos', 'requalificando',
        'restaurada', 'restauradas', 'restaurado', 'restaurados', 'restauram', 'restaurar',
        'restauração', 'restauramos', 'restaurando',
        'revitalizada', 'revitalizadas', 'revitalizado', 'revitalizados', 'revitalizam', 'revitalizar', 'revitalização',
        'revitalizações', 'revitalizamos', 'revitalizando',
        'serviço', 'serviços',
        'sinalizada', 'sinalizadas', 'sinalizado', 'sinalizados', 'sinalizam', 'sinalizar',
        'sinalização', 'sinalizações', 'sinalizamos', 'sinalizando',
        'subsidiada', 'subsidiadas', 'subsidiado', 'subsidiados', 'subsidiam', 'subsidiar', 'subsídio',
        'subsídios', 'subsidiamos', 'subsidiando',
        'transformada', 'transformadas', 'transformado', 'transformados', 'transformam', 'transformar', 'transformação',
        'transformações', 'transformamos', 'transformando',
        'urbanizada', 'urbanizadas', 'urbanizado', 'urbanizados', 'urbanizam', 'urbanizar', 'urbanização',
        'urbanizações', 'urbanizamos', 'urbanizando',
        'valor', 'valoração', 'valores', 'valorizada', 'valorizadas', 'valorizado', 'valorizadores', 'valorizados',
        'valorizam', 'valorizar', 'valorização', 'valorizamos', 'valorizando'
    ]


    # Palavras para excluir (informativos sobre eventos ou ações que não envolvem investimentos financeiros)
    palavras_excluir = [
         'aedes aegypti', 'acesso gratuito', 'acidente', 'acidentes', 'agasalho', 'agenda', 'aglomeração', 'aglomerações',
         'atração', 'atrações', 'amanhecer', 'amar', 'amor', 'aniversário', 'ano novo', 'aplicativo', 'arraial', 'arte',
         'artesã', 'artesanato', 'atenção', 'atendimento',
         'brega funk', 'cadastro', 'cadastrado', 'cadastrada', 'cadastradas', 'cadastrados', 'cadastramos', 'cadastral',
         'CadÚnico', 'campanha', 'cantor',
         'carnaval', 'ceia', 'censo', 'céu', 'chikungunya', 'ciclista', 'ciclistas',  'circular', 'corpus christi',
         'cota única', 'comitiva' 'comunicado', 'comunicados',
         'comunicamos', 'convite', 'convocação', 'corrida', 'corridas', 'coronavírus', 'COVID',
         'covid-19', 'crime', 'dia', 'dengue', 'denúncia', 'denúnicias', 'denunciem', 'desconto', ' desfile', 'desemprego', 'desempregados',
         'distanciamento social', 'divulgação', 'divulgações', 'divulgamos', 'doação', 'dose', 'edição','edições', 'edital',
         'emancipar', 'emancipação', 'empatia', 'emprego', 'empreendedora', 'empreendedor', 'empreender', 'empregados', 'escultura', 'espetáculo', 'espetáculos', 'evento',
         'eventos', 'evitar', 'feira', 'festas', 'festival', 'festivais', 'férias', 'fiéis', 'forró', 'forrozinho', 'frio', 'friozinho',
         'funk', 'grátis', 'gratuita', 'gratuitas', 'gratuito',
         'gratuitos', 'horário', 'homenagem', 'imunizada', 'imunizadas', 'imunizado', 'imunizados', 'informativo', 'informamos',
         'inscrição', 'inscrições', 'interditada', 'interditadas', 'irregular', 'irregulares', 'isolamento', 'junino',
         'junina', 'ligar', 'ligação', 'legado', 'local', 'manifestação',
         'manifestações', 'maratona', 'maratonas',  'máscara', 'máscaras', 'medalha', 'medalhas', 'milho', 'mosquito',
         'mosquitos', 'motorista', 'museu', 'música', 'natal',
        'nota', 'notas', 'olimpíada', 'olimpíadas', 'ONU', 'orgânico', 'orgânicos',
         'ouro', 'ouvidoria', 'palestra', 'palestras', 'pandemia', 'passo a passo',
         'participação', 'paz', 'pedal',  'pedalada', 'pedestre', 'pedestres', 'plenária', 'plenárias', 'posse', 'por do sol',
         'porto', 'preconceito', 'prêmio', 'prevenir', 'prevenção', 'procissão', 'procissões',
         'projeto verão', 'programação', 'programação cultural', 'promoção', 'promoções', 'protetor solar', 'ranking', 'resíduo', 'resíduos',
          'resgatada', 'resgatadas', 'respeito', 'respeitar', 'respeitamos', 'reunião', 'reuniões', 'roteiro', 'saudável', 'secretário', 'secretários',
         'seleção', 'seletiva', 'selo', 'show', 'shows','skate', 'skatista', 'sinistro', 'site', 'solidário', 'solidariedade', 'triatlo', 'triathlon' 'tutorial', 'turista',
         'turma', 'vacina', 'vacinar', 'vacinada',
         'vacinadas', 'vacinados', 'vacinação', 'vacinamos', 'varejão', 'verão',
         'vídeo', 'violência', 'virtual', 'vistoria', 'vistorias', 'vulnerável', 'vulnerabilidade', 'são joão', 'youtube', 'zika'
    ]

    texto_lower = texto.lower()

    # Verificar se o texto contém alguma palavra da lista de exclusão
    for palavra in palavras_excluir:
        if palavra in texto_lower:
            return 'Não'

    # Verifica se o texto contém alguma das palavras-chave financeiras
    for palavra in palavras_chave:
        if palavra in texto_lower:
            return 'Sim'

    # Verifica se o texto menciona termos relacionados a valores
    if 'r$' in texto_lower or 'valor' in texto_lower or 'investimento' in texto_lower or 'gasto' in texto_lower:
        return 'Sim'

    # Se não encontrar nenhuma palavra-chave financeira, retorna 'Não'
    return 'Não'


# Função principal
def main():
    # Selecionar o arquivo Excel
    files = glob('C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/interim/2024_classified/' + '*.xlsx')
    for file in files:
        arquivo_excel = file
        if not arquivo_excel:
            print("Nenhum arquivo foi selecionado.")
            return

        # Tentar carregar o arquivo Excel com exceções para problemas
        try:
            print("Carregando o arquivo...")

            # Limitar a 12.000 linhas para garantir performance
            dados = pd.read_excel(arquivo_excel, engine='openpyxl', sheet_name=0, nrows=12000)
            print("Arquivo carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return

        # Verificar colunas por índice
        coluna_texto = 'Message'  # Coluna de texto com as mensagens
        coluna_classificacao = 'Informação Financeira'  # Coluna para classificação

        print(f"Coluna de texto: {coluna_texto}")
        print(f"Coluna de classificação: {coluna_classificacao}")

        # Preencher valores nulos na coluna de texto com uma string vazia
        dados[coluna_texto] = dados[coluna_texto].fillna('')

        # Dividir os dados em base de treino e base de previsão
        base_treino = dados.dropna(subset=[coluna_classificacao])
        base_previsao = dados[dados[coluna_classificacao].isna()]

        if base_treino.empty:
            print("Não há dados classificados para usar como base.")
            return

        # Preencher as linhas vazias com a classificação
        print("Preenchendo as linhas vazias na coluna de classificação...")
        referencias = base_treino[coluna_texto].tolist()
        classificacoes = base_treino[coluna_classificacao].tolist()

        # Verificação das mensagens e classificação conforme o conteúdo financeiro
        dados[coluna_classificacao] = dados[coluna_classificacao].fillna(
            dados[coluna_texto].apply(
                lambda x: classificar_similaridade(x, referencias, classificacoes) if verificar_informacao_financeira(x) == 'Não' else 'Sim')
        )

        # Salvar o arquivo com o sufixo "classificado"
        diretorio_saida = 'C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/interim/2024_classified_tf_idf/'
        nome_arquivo = os.path.basename(arquivo_excel).replace('.xlsx', '_classificado.xlsx')
        caminho_saida = os.path.join(diretorio_saida, nome_arquivo)

        try:
            dados.to_excel(caminho_saida, index=False)
            print(f"Arquivo salvo com sucesso em: {caminho_saida}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

if __name__ == "__main__":
    main()