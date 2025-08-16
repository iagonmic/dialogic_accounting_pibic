import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy.stats import shapiro

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
    'mean_comment_sentiment'
]

# Carrega o dataframe
df1 = pd.read_excel(data_path + '/results/2_independent_variable_4024.xlsx')

# Removendo 314 linhas com valores NaN em iengajamento
df1 = df1.dropna(subset=['IEngajamento'])

# Variável dependente
y = df1['IEngajamento']
# Variáveis independentes
X = df1[variaveis_independentes]

# Converte variáveis categóricas em dummies
X = pd.get_dummies(X, drop_first=True)

# Normaliza variáveis para facilitar interpretação
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
y_scaled = y  # opcional: também pode padronizar y se quiser comparar magnitudes

# Adiciona constante
X_const = sm.add_constant(X_scaled)


# =====================
# 1. Multicolinearidade
# =====================
print("\n=== VIF (Multicolinearidade) ===")
vif = pd.DataFrame()
vif["Variável"] = X_const.columns
vif["VIF"] = [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])]
print(vif)

# nesse caso não temos nada com VIF > 10, então não há multicolinearidade severa

# =====================
# 2. Regressão múltipla
# =====================
modelo = sm.OLS(y_scaled, X_const).fit()
print("\n=== RESUMO MODELO MÚLTIPLO ===")
print(modelo.summary())

# =====================
# 3. Regressões simples
# =====================
print("\n=== REGRESSÕES SIMPLES (uma variável por vez) ===")
for var in X.columns:
    X_single = sm.add_constant(X_scaled[[var]])
    modelo_single = sm.OLS(y_scaled, X_single).fit()
    print(f"\nModelo com {var}:")
    print(modelo_single.summary())

# =====================
# 4. Normalidade dos resíduos
# =====================
residuos = modelo.resid
stat, p = shapiro(residuos)
print("\n=== TESTE DE NORMALIDADE (Shapiro-Wilk) ===")
print(f"Estatística={stat:.4f}, p-valor={p:.4f}")
sns.histplot(residuos, kde=True)
plt.title("Distribuição dos resíduos")
plt.show()

# =====================
# 5. Heterocedasticidade
# =====================
bp_test = het_breuschpagan(residuos, modelo.model.exog)
labels = ['LM Statistic', 'LM-Test p-value', 'F-Statistic', 'F-Test p-value']
bp_results = dict(zip(labels, bp_test))
print("\n=== TESTE DE HETEROCEDASTICIDADE (Breusch-Pagan) ===")
for k, v in bp_results.items():
    print(f"{k}: {v:.4f}")

# =====================
# 6. Resíduos vs Ajustados
# =====================
ajustados = modelo.fittedvalues
plt.scatter(ajustados, residuos)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Valores Ajustados')
plt.ylabel('Resíduos')
plt.title('Resíduos vs Valores Ajustados')
plt.show()

# =====================
# 7. Observações influentes (Cook's Distance)
# =====================
influence = modelo.get_influence()
cooks_d = influence.cooks_distance[0]

plt.stem(np.arange(len(cooks_d)), cooks_d, markerfmt=",")
plt.title("Distância de Cook")
plt.xlabel("Observação")
plt.ylabel("Cook's Distance")
plt.show()

limite = 4 / len(cooks_d)
outliers = np.where(cooks_d > limite)[0]
print("\n=== OBSERVAÇÕES INFLUENTES ===")
print(f"Limite Cook's D: {limite:.4f}")
print(f"Índices influentes: {outliers}")

# =====================
# 8. Modelo com erros robustos (opcional)
# =====================
modelo_robusto = modelo.get_robustcov_results(cov_type='HC3')
print("\n=== RESUMO MODELO ROBUSTO (HC3) ===")
print(modelo_robusto.summary())