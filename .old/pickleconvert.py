import browser_cookie3
import pickle

# Capturar cookies do navegador (escolha o navegador que você usa)
cookies = browser_cookie3.chrome()  # ou browser_cookie3.firefox(), etc.

# Nome do arquivo onde os cookies serão salvos
cookie_file = "insta_session"

# Salvar os cookies no arquivo
with open(cookie_file, "wb") as file:
    pickle.dump(cookies, file)

print(f"Cookies salvos no arquivo '{cookie_file}' com sucesso!")
