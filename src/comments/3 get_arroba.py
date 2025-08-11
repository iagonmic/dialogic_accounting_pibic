from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import pandas as pd
from tqdm import tqdm

load_dotenv()

TOKEN = os.getenv('APIFY_TOKEN')

def get_all_runs(client, actor_id):
    runs = []
    offset = 0
    limit = 100
    while True:
        response = client.actor(actor_id).runs().list(limit=limit, offset=offset)
        runs.extend(response.items)
        if len(response.items) < limit:
            break
        offset += limit
    return runs

def get_run_output(client, run_id):
    # Busca todos os itens do dataset de saída do run
    dataset_items = client.run(run_id).dataset().list_items().items
    return dataset_items

def main():
    actor_id = 'apidojo/instagram-comments-scraper'
    client = ApifyClient(TOKEN)
    runs = get_all_runs(client, actor_id)
    print(f'Total de runs encontradas: {len(runs)}')
    todas_respostas = []
    for run in tqdm(runs):
        run_id = run['id']
        try:
            respostas = get_run_output(client, run_id)
            todas_respostas.extend(respostas)
        except Exception as e:
            print(f'Erro ao buscar respostas do run {run_id}: {e}')
    # Salvar todas as respostas em um arquivo CSV usando pandas
    df = pd.DataFrame(todas_respostas)
    df.to_csv('C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data/comentarios.csv', index=False, encoding='utf-8')
    print('Respostas salvas em data/comentarios_apify.csv')

if __name__ == '__main__':
    main()