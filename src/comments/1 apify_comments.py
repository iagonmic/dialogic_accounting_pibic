from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import pandas as pd
from tqdm import tqdm

load_dotenv()

TOKEN = os.getenv('APIFY_TOKEN')

# You can find your API token at https://console.apify.com/settings/integrations.
apify_client = ApifyClient(TOKEN)

# Start an Actor and wait for it to finish.
actor_client = apify_client.actor('apidojo/instagram-comments-scraper')

def get_comments(link):
    call_result = actor_client.call(run_input=({
    "customMapFunction": "(object) => { return {...object} }",
    "maxItems": 101,
    "startUrls": [
        f"{link}"
    ]}))
    
    if call_result is None:
        print('Actor run failed.')
        return None
    
    dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
    list_items_result = dataset_client.list_items()

    comments = [comment['message'] for comment in list_items_result.items]

    return comments

def main():
    file_path = "/home/iagonmic/data_science/dialogic_accounting_pibic/data/processed/final_sample.xlsx"
    df = pd.read_excel(file_path)

    if 'Comentários' not in df.columns:
        df['Comentários'] = None

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        link = row['Link']

        if pd.notna(df.at[idx, 'Comentários']):
            continue

        comments = get_comments(link)

        df.at[idx, 'Comentários'] = comments
        df.to_excel('/home/iagonmic/data_science/dialogic_accounting_pibic/data/processed/final_sample.xlsx', index=False)