import pandas as pd
from tkinter import Tk, filedialog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from imblearn.over_sampling import SMOTE
from glob import glob
from nltk.corpus import stopwords
import os


def escolher_arquivo():
    root = Tk()
    root.withdraw()
    caminho_inicial = r"C:"
    arquivo = filedialog.askopenfilename(initialdir=caminho_inicial,
                                         title="Selecione o arquivo Excel",
                                         filetypes=[("Arquivos Excel", "*.xlsx")])
    return arquivo

def classificar_similaridade(texto, referencias, classificacoes, limite_similaridade=0.90):
    if pd.isna(texto):
        return 'Não'

    stop_words = stopwords.words('portuguese')
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    textos_comparar = [texto] + referencias
    tfidf_matrix = vectorizer.fit_transform(textos_comparar)
    cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    for i, sim in enumerate(cos_sim[0]):
        if sim >= limite_similaridade and classificacoes[i] == 'Sim':
            return 'Sim'
    return 'Não'

def main(file):
    dados = pd.read_excel(file)

    coluna_texto = 'Message'
    coluna_classificacao = 'Informação Financeira'
    dados[coluna_texto] = dados[coluna_texto].fillna('')

    X = dados[coluna_texto]
    y = dados[coluna_classificacao].apply(lambda x: 1 if x == 'Sim' else 0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(stop_words=stopwords.words('portuguese'))

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train_tfidf, y_train)

    logistic_regression = LogisticRegression()
    logistic_regression.fit(X_train_res, y_train_res)

    y_pred = logistic_regression.predict(X_test_tfidf)

    precision = precision_score(y_test, y_pred)
    recall_s = recall_score(y_test, y_pred)
    f1_s = f1_score(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)

    print(f'Precision: {precision_score(y_test, y_pred):.2f}')
    print(f'Recall: {recall_score(y_test, y_pred):.2f}')
    print(f'F1-Score: {f1_score(y_test, y_pred):.2f}')
    print(f'Accuracy: {accuracy_score(y_test, y_pred):.2f}')

    return precision, recall_s, f1_s, accuracy

if __name__ == "__main__":
    files = glob('C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/interim/2024_classified_tf_idf/' + '*.xlsx')
    results = []
    for file in files:
        print(os.path.basename(file))
        precision, recall_s, f1_s, accuracy = main(file)
        results.append({
            "arquivo": os.path.basename(file),
            "precision": precision,
            "recall": recall_s,
            "f1_score": f1_s,
            "accuracy": accuracy
        })
    df_results = pd.DataFrame(results)
    df_results.to_excel('C:/Users/iagof/Desktop/Data Science/dialogic_accounting_pibic/data/interim/tf-idf-analysis_2.xlsx', index=False)


    
