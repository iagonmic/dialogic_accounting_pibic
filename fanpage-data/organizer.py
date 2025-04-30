import pandas as pd
import glob
import os

# caminhos dos arquivos
path1 = 'fanpage-data/rcs/'
path2 = 'fanpage-data/likes/'
path3 = 'fanpage-data/processed/'

# ler arquivos
files_rcs = glob.glob(os.path.join(os.path.abspath(path1), '*.xlsx'))

for i, file in enumerate(files_rcs):
    
    df_rcs = pd.read_excel(file, header=4, usecols="B:I").sort_values(by="Date").reset_index(drop=True)

    file_name = file.split('\\')[-1].split('.')[:-1]
    file_name = '.'.join(file_name)
    
    file_like = glob.glob(os.path.join(os.path.abspath(path2), file_name + '*.xlsx'))
    df_like = pd.read_excel(file_like[0], header=4, usecols="B:I").sort_values(by="Date").reset_index(drop=True)

    df_like['Likes per post'] = pd.to_numeric(df_like['Likes per post'], errors='coerce')
    df_like['Likes per post'] = df_like['Likes per post'].fillna(0).astype(int)

    df_rcs.insert(5, 'Likes per post', value=(df_like['Likes per post'].values))
    df_rcs.insert(6, 'Comments per post', value=(
        df_rcs['Reactions, Comments & Shares'].values - df_like['Likes per post'].values
    ))

    df_rcs.to_excel(os.path.join(os.path.abspath(path3), file_name + '.xlsx'), index=False)
    print(f'Arquivo {i+1} de {len(files_rcs)} processados: {file_name}.xlsx')

    
    
    