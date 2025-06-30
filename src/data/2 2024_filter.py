import os
from glob import glob
import pandas as pd
from tqdm import tqdm

data_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/"
interim_data_path = f"{data_path}/interim/2024/"
files = glob(data_path + 'raw/' + '*.xlsx')
current_files = glob(interim_data_path + "*.xlsx")

for file in (pbar := tqdm(files)):
    if file in current_files:
        continue
    file_name = file.split('\\')[-1]
    pbar.set_description(f'Lendo {file_name}')
    df = pd.read_excel(file)
    df = df[df['Date'] > '2024-01-01']
    
    df.to_excel(data_path + 'interim/2024/' + file_name, index=False)