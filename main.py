from classes import Scraper
from getpass import getpass

scraper = Scraper()

scraper.define_chrome_driver()

scraper.get_url('https://www.facebook.com')

# se não estiver logado no facebook
if scraper.get_element_list('//input[contains(@class, "inputtext")]', time=5) != None:
    email = input('Digite o email para fazer login no facebook: ')
    senha = getpass("Digite sua senha: ")

    scraper.facebook_login(email, senha)

# entrar nos sites dos governos
scraper.get_url('https://www.facebook.com/governosp')