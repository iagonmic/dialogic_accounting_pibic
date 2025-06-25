from glob import glob
import pandas as pd
from tqdm import tqdm

data_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/"
files = glob(data_path + 'raw/' + '*.xlsx')

for file in (pbar := tqdm(files)):
    file_name = file.split('\\')[-1]
    pbar.set_description(f'Lendo {file_name}')
    df = pd.read_excel(file)
    df = df[df['Date'] > '2024-01-01']
    
    df.to_excel(data_path + 'interim/2024/' + file_name, index=False)