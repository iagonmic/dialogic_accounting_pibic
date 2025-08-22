import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy.stats import shapiro
from statsmodels.graphics.tsaplots import plot_acf

data_path = 'C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data'

variaveis_independentes = [
    'classify_5_inverted',
    'content_type',
    'posts_per_day',
    'period_of_day',
    'num_hashtags',
    'flesch_index',
    'call_to_action',
    'gov_commented',
    'mean_comment_sentiment',
    'regiao',
    'PIB_regiao'
]

# Carrega o dataframe
df = pd.read_excel(data_path + '/results/2_independent_variable_4024.xlsx')
df = df.dropna(subset=['IEngajamento'])

# ==========================
# Mapeamento Profile -> Região
# ==========================
mapa_regiao = {
    "Acre": "Norte",
    "Amazonas": "Norte",
    "Amapá": "Norte",
    "Pará": "Norte",
    "Rondônia": "Norte",
    "Roraima": "Norte",
    "Tocantins": "Norte",
    "Alagoas": "Nordeste",
    "Bahia": "Nordeste",
    "Ceará": "Nordeste",
    "Maranhão": "Nordeste",
    "Paraíba": "Nordeste",
    "Pernambuco": "Nordeste",
    "Piauí": "Nordeste",
    "Rio Grande do Norte": "Nordeste",
    "Sergipe": "Nordeste",
    "Distrito Federal": "Centro-Oeste",
    "Goiás": "Centro-Oeste",
    "Mato Grosso": "Centro-Oeste",
    "Mato Grosso do Sul": "Centro-Oeste",
    "Espírito Santo": "Sudeste",
    "Minas Gerais": "Sudeste",
    "Rio de Janeiro": "Sudeste",
    "São Paulo": "Sudeste",
    "Paraná": "Sul",
    "Rio Grande do Sul": "Sul",
    "Santa Catarina": "Sul"
}

# ==========================
# PIB por região
# ==========================
df_pib_norte = pd.read_excel(data_path + '/IBGE_PIB/Tabela1.xls', sheet_name='Tabela1.1')
valor_norte = df_pib_norte.loc[55, 'Unnamed: 3']

df_pib_nordeste = pd.read_excel(data_path + '/IBGE_PIB/Tabela9.xls', sheet_name='Tabela9.1')
valor_nordeste = df_pib_nordeste.loc[55, 'Unnamed: 3']

df_pib_sudeste = pd.read_excel(data_path + '/IBGE_PIB/Tabela19.xls', sheet_name='Tabela19.1')
valor_sudeste = df_pib_sudeste.loc[55, 'Unnamed: 3']

df_pib_sul = pd.read_excel(data_path + '/IBGE_PIB/Tabela24.xls', sheet_name='Tabela24.1')
valor_sul = df_pib_sul.loc[55, 'Unnamed: 3']

df_pib_centrooeste = pd.read_excel(data_path + '/IBGE_PIB/Tabela28.xls', sheet_name='Tabela28.1')
valor_centrooeste = df_pib_centrooeste.loc[55, 'Unnamed: 3']

pib_regiao = {
    'Norte': valor_norte,
    'Nordeste': valor_nordeste,
    'Sudeste': valor_sudeste,
    'Sul': valor_sul,
    'Centro-Oeste': valor_centrooeste
}

# ==========================
# Adiciona colunas de região e PIB ao DataFrame
# ==========================
df["regiao"] = df["Profile"].map(mapa_regiao)
df["PIB_regiao"] = df["regiao"].map(pib_regiao)

# ==========================
# Modelo com controle de região e PIB
# ==========================
# Variável dependente
Y = df['IEngajamento'].dropna()
# Remove colunas que não entram no modelo
X = df[variaveis_independentes]
X = pd.get_dummies(X, drop_first=True)
X = sm.add_constant(X).loc[Y.index]
X = X.astype(float)  # Garante que todas as colunas são float

# Regressão com controle
ols = sm.OLS(Y, X).fit(cov_type="HAC", cov_kwds={"maxlags":5})
print(ols.summary())

# ==========================
# Modelos por região
# ==========================
resultados_regiao = {}
regiao_cols = [col for col in df.columns if col.startswith("regiao_")]
# Recupera o nome da região original para cada linha
df["regiao_nome"] = df[["Profile"]].apply(lambda row: mapa_regiao.get(row["Profile"], np.nan), axis=1)

for regiao in df["regiao_nome"].dropna().unique():
    subset = df[df["regiao_nome"] == regiao]
    Y_sub = subset["IEngajamento"].dropna()
    X_sub = subset[variaveis_independentes]
    X_sub = pd.get_dummies(X_sub, drop_first=True)
    X_sub = sm.add_constant(X_sub)
    X_sub = X_sub.astype(float)  # Garante que todas as colunas são float
    modelo = sm.OLS(Y_sub, X_sub).fit(cov_type="HAC", cov_kwds={"maxlags":5})
    resultados_regiao[regiao] = modelo
    print(f"\n=== Região {regiao} ===")
    print(modelo.summary())

# ==========================
# Tabela comparativa dos modelos por região
# ==========================
comparativo = pd.DataFrame({
    regiao: {
        "R²": resultados_regiao[regiao].rsquared,
        "Adj R²": resultados_regiao[regiao].rsquared_adj,
        **{f"{var}_pval": resultados_regiao[regiao].pvalues[var] for var in resultados_regiao[regiao].params.index}
    }
    for regiao in resultados_regiao
}).T

print("\n=== TABELA COMPARATIVA POR REGIÃO ===")
comparativo.sort_values("R²", ascending=False)