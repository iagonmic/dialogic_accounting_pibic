from classes import Scraper
from getpass import getpass

self = Scraper()

self.define_chrome_driver()

self.get_url('https://www.facebook.com')

# se não estiver logado no facebook
if self.get_element_list('//input[contains(@class, "inputtext")]', time=5) != None:
    email = input('Digite o email para fazer login no facebook: ')
    senha = getpass("Digite sua senha: ")

    self.facebook_login(email, senha)

# entrar nos sites dos governos
self.get_url('https://www.facebook.com/GovernoParaiba')

for i in range(1,21):
    print(self.get_text(i))

self.get_url('https://www.facebook.com/governosp')

for i in range(1,21):
    print(self.get_text(i))