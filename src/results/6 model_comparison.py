import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


data_path = 'C:/Users/Usuario/Desktop/data-science/dialogic_accounting_pibic/data'

# Carrega o dataframe
df = pd.read_excel(data_path + '/results/2_independent_variable_4024.xlsx')
df = df.dropna(subset=['IEngajamento'])

# ==========================
# 1. Modelo original (sem PIB/região)
# ==========================
variaveis_originais = [
    'classify_5_inverted',
    'content_type',
    'posts_per_day',
    'period_of_day',
    'num_hashtags',
    'flesch_index',
    'call_to_action',
    'gov_commented',
    'mean_comment_sentiment'
]

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


df["regiao"] = df["Profile"].map(mapa_regiao)
df["PIB_regiao"] = df["regiao"].map(pib_regiao)

# --------------------------
# Variáveis independentes sem região/PIB
# --------------------------
variaveis_base = [
    'classify_5_inverted',
    'content_type',
    'posts_per_day',
    'period_of_day',
    'num_hashtags',
    'flesch_index',
    'call_to_action',
    'gov_commented',
    'mean_comment_sentiment'
]

# --------------------------
# Função para rodar regressão
# --------------------------
def rodar_regressao(df, variaveis, label, regiao=False):
    X = df[variaveis].copy()
    if regiao is not False:
        X = df[df['regiao'] == regiao][variaveis].copy()

    X = pd.get_dummies(X, drop_first=True)
    X = sm.add_constant(X).astype(float)
    Y = df["IEngajamento"]

    modelo = sm.OLS(Y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    print(f"\n=== Modelo {label} ===")
    print(modelo.summary())

    print("\n=== VIF (Multicolinearidade) ===")
    vif = pd.DataFrame()
    vif["Variável"] = X.columns
    vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    print(vif)
    return modelo

# --------------------------
# Opção A → só PIB_regiao
# --------------------------
variaveis_A = variaveis_base + ["PIB_regiao"]
modelo_A = rodar_regressao(df, variaveis_A, "A - Apenas PIB")

# --------------------------
# Opção B → só Região
# --------------------------
variaveis_B = variaveis_base + ["regiao"]
modelo_B = rodar_regressao(df, variaveis_B, "B - Apenas Região")

# --------------------------
# Comparação final (Opção C)
# --------------------------
comparativo = pd.DataFrame({
    "Modelo A - PIB": {
        "R²": modelo_A.rsquared,
        "Adj R²": modelo_A.rsquared_adj,
        **{f"{var}_pval": modelo_A.pvalues[var] for var in modelo_A.params.index if "PIB_regiao" in var}
    },
    "Modelo B - Região": {
        "R²": modelo_B.rsquared,
        "Adj R²": modelo_B.rsquared_adj,
        **{f"{var}_pval": modelo_B.pvalues[var] for var in modelo_B.params.index if "regiao" in var}
    }
}).T

print("\n=== COMPARAÇÃO FINAL ===")
print(comparativo)

# gráficos

import matplotlib.pyplot as plt

# Dados de R²
r2_scores = {
    "Modelo A - PIB": modelo_A.rsquared,
    "Modelo B - Região": modelo_B.rsquared
}

# Plot
plt.bar(r2_scores.keys(), r2_scores.values())
plt.ylabel("R²")
plt.title("Comparação de R² - Controle por PIB vs. Região")
plt.ylim(0, max(r2_scores.values()) * 1.2)

for i, v in enumerate(r2_scores.values()):
    plt.text(i, v + 0.005, f"{v:.3f}", ha='center')

plt.show()

# --------------------------
# Opção B → só Região
#----------------------------

import statsmodels.api as sm

# Lista base de variáveis (sem regiao e PIB)
variaveis_base = [
    'posts_per_day','num_hashtags','flesch_index','call_to_action',
    'gov_commented','mean_comment_sentiment',
    'classify_5_inverted_Nível 2 (Baixo Detalhe Intermediário)',
    'classify_5_inverted_Nível 3 (Detalhe Moderado/Médio)',
    'classify_5_inverted_Nível 4 (Alto Detalhe)',
    'classify_5_inverted_Nível 5 (Extremo Detalhe)',
    'content_type_Vídeo',
    'period_of_day_Manhã','period_of_day_Noite','period_of_day_Tarde'
]

regioes = df['regiao'].unique()
resultados_regioes = {}

for reg in regioes:
    df_reg = df[df['regiao'] == reg].copy()
    
    # Cria X com todas as variáveis base, preenchendo faltantes com 0
    X_reg = df_reg.reindex(columns=variaveis_base, fill_value=0)
    X_reg = sm.add_constant(X_reg)

    X_reg = X_reg.loc[:, (X_reg != X_reg.iloc[0]).any()]
    
    y_reg = df_reg['IEngajamento']
    
    modelo_reg = sm.OLS(y_reg, X_reg).fit(cov_type='HAC', cov_kwds={'maxlags':5})
    
    resultados_regioes[reg] = {
        "R²": modelo_reg.rsquared,
        "Adj R²": modelo_reg.rsquared_adj,
        "N": len(df_reg),
        "Resumo": modelo_reg.summary()
    }

# Mostrar apenas os R² para comparar
for reg, res in resultados_regioes.items():
    print(f"=== {reg} ===")
    print(f"R²: {res['R²']:.3f} | Adj R²: {res['Adj R²']:.3f} | N = {res['N']}")
    print("-"*50)

import numpy as np

for reg in regioes:
    df_reg = df[df['regiao'] == reg].copy()
    
    # Reindex com todas as dummies possíveis
    X_reg = df_reg.reindex(columns=variaveis_base, fill_value=0)
    X_reg = X_reg.loc[:, (X_reg != X_reg.iloc[0]).any()]

    X_reg = sm.add_constant(X_reg)
    
    # Remove colunas constantes (sem variabilidade)
    
    y_reg = df_reg['IEngajamento']
    
    modelo_reg = sm.OLS(y_reg, X_reg).fit(cov_type='HAC', cov_kwds={'maxlags':5})
    
    resultados_regioes[reg] = {
        "R²": modelo_reg.rsquared,
        "Adj R²": modelo_reg.rsquared_adj,
        "N": len(df_reg),
        "Vars": X_reg.columns.tolist(),
        "Resumo": modelo_reg.summary()
    }

import matplotlib.pyplot as plt
import numpy as np

# Dados originais
regioes = ['Sul', 'Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste']
r2 = [0.043, 0.128, 0.094, 0.075, 0.051]

# Ordenar do maior para o menor
r2_sorted, regioes_sorted = zip(*sorted(zip(r2, regioes), reverse=True))

# Configurações do gráfico
x = np.arange(len(regioes_sorted))
largura = 0.6

plt.figure(figsize=(10,6))
barras = plt.bar(x, r2_sorted, width=largura, color='royalblue')

# Títulos e labels
plt.ylabel('R²')
plt.xlabel('Região')
plt.title('Comparação de R² por Região')
plt.xticks(x, regioes_sorted)

# Valores sobre as barras
for barra in barras:
    altura = barra.get_height()
    plt.text(barra.get_x() + barra.get_width()/2, altura + 0.005, f'{altura:.3f}', 
             ha='center', va='bottom', fontsize=10)

plt.ylim(0, max(r2_sorted)*1.2)  # deixa espaço para os números
plt.tight_layout()
plt.show()