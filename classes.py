from lxml import html
from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random import randint
from time import sleep
import os

class Driver:
    def __init__(self):
        self.driver = None

    def define_chrome_driver(self, headless=None):
        chrome_version = os.popen("/opt/google/chrome/google-chrome --version | awk '{print $3}'").read() # linux

        service = Service(ChromeDriverManager(driver_version=chrome_version[:-1]).install())

        options = webdriver.ChromeOptions()

        options.binary_location = "/opt/google/chrome/google-chrome"

        if headless == True:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-fullscreen")

        options.add_argument('user-data-dir=/home/iagonmic/.config/google-chrome')

        # WINDOWS: options.add_argument('user-data-dir=C:/Users/User/AppData/Local/Google/Chrome/User Data')

        options.add_experimental_option('detach', True)

        self.driver = webdriver.Chrome(service=service, options=options)
        
        return self.driver
    
    def get_url(self, url:str):
        return self.driver.get(url)
    
    def get_element(self, xpath:str, time=20, click=False):
        element = None
        try:
            element = (WebDriverWait(self.driver,time)
                        .until(EC.presence_of_element_located((By.XPATH, xpath))))
        except:
            return element

        if click is not False:
            element.click()

        return element
    
    def get_element_list(self, xpath:str, time=20, click:int=False):
        elements = None
        try:
            elements = (WebDriverWait(self.driver,time)
                        .until(EC.presence_of_all_elements_located((By.XPATH, xpath))))
        except:
            return elements

        if click is not False:
            elements[click].click()

        return elements
    
    def type(self, input):
        return ActionChains(self.driver).send_keys(input).perform()

    def facebook_login(self, email, password):
        # clicar no campo de email e digitar
        self.get_element_list('//input[contains(@class, "inputtext")]', click=0)
        self.type(email)

        sleep(randint(2,4))

        # clicar no campo de senha
        self.get_element_list('//input[contains(@class, "inputtext")]', click=1)
        self.type(password)
        
        # clicar no botão entrar
        self.get_element('//button[@value=1]', click=True)

    def get_page_html(self):
        return self.driver.page_source
    
class Scraper(Driver):
    def __init__(self):
        super().__init__()
        self.html = None
        self.soup = None
        self.structure = None
        self.posts = {} # ex: 'janeiro': [post(id=1), post(id=2)...]

    def get_post_text(self, id):
        # Seleciona todas as divs que estão dentro de um span com texto que tenha tamanho maior que 50
        self.renew_html()

        # Encontrar texto pelo xpath
        base_xpath = f'/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{id}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div/div/span'

        texts = [text.text_content() for text in self.structure.xpath(base_xpath + '/div/div') + self.structure.xpath(base_xpath + '/div/div/span') 
                 if type(text.text) == str]

        full_text = " ".join(texts).replace('\u200c', '')

        return full_text

    def renew_html(self):
        self.html = super().get_page_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.structure = html.fromstring(str(self.soup))

    def get_post_number_by_month(self, month):
        # função para verificar quantos posts existem naquele mês

        # Passo 1: descer a página até o ultimo post daquele mês
        # Passo 2: verificar o número de posts
        pass

    def collect_posts(self, month):
        # função para coletar e armazenar os dados dos posts do mês escolhido
        pass


class Post:
    def __init__(self):
        self.month = None
        self.id = None
        self.text = None
        self.img_type = None
        self.likes = None
        self.comments_quantity = None
        self.shares = None
        self.comments = []
        
    def __repr__(self) -> str:
        pass
