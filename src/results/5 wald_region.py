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

Y = df['IEngajamento']

X_orig = df[variaveis_originais]
X_orig = pd.get_dummies(X_orig, drop_first=True)
X_orig = sm.add_constant(X_orig).loc[Y.index]
X_orig = X_orig.astype(float)


X = df[variaveis_independentes]
X = pd.get_dummies(X, drop_first=True)
X = sm.add_constant(X).loc[Y.index]
X = X.astype(float)

modelo_orig = sm.OLS(Y, X_orig).fit(cov_type="HAC", cov_kwds={"maxlags":7})

print("=== Modelo Original (sem controles) ===")
print(modelo_orig.summary())
print(f"AIC: {modelo_orig.aic}, BIC: {modelo_orig.bic}")

# ==========================
# 2. Modelo com PIB e região (já rodado antes)
# ==========================
# X com controles já foi criado anteriormente como X
ols = sm.OLS(Y, X_orig).fit(cov_type="HAC", cov_kwds={"maxlags":7})
print("\n=== Modelo com PIB e região ===")
print(ols.summary())
print(f"AIC: {ols.aic}, BIC: {ols.bic}")

# ==========================
# 3. Wald Test para dummies de região
# ==========================
regiao_dummies = [col for col in X_orig.columns if col.startswith("regi")]
if len(regiao_dummies) > 0:
    # Cria a string de hipóteses: cada dummy = 0
    hypotheses = " = 0, ".join(regiao_dummies) + " = 0"
    wald_test = ols.wald_test(hypotheses)
    print("\n=== Wald Test: todas as dummies de região = 0 ===")
    print(wald_test)
else:
    print("Não há dummies de região para o Wald Test.")
