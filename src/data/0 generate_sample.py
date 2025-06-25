from random import choice
from glob import glob
import os
import pandas as pd

data_path = "C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data"
raw_data = os.path.join(data_path, "raw/")

files = glob(raw_data + "*.xlsx")

#file = choice(files)
file = files[26] # gov_df

df = pd.read_excel(file).sample(250).filter(['Message'])

df["Informações Financeiras"] = ""

df.to_excel(os.path.join(data_path, "interim/") + file.split('\\')[-1], index=True)