from lxml import html
from bs4 import BeautifulSoup
import re

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
from numpy import nan
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
    
    def get_element_list(self, xpath, time=20, element_number_click:int=None, click_all=False):
        elements = None
        if isinstance(xpath, str):
            try:
                elements = (WebDriverWait(self.driver,time)
                            .until(EC.presence_of_all_elements_located((By.XPATH, xpath))))
            except:
                return elements
            
        if isinstance(xpath, list):
            for i in xpath:
                try:
                    elements = (WebDriverWait(self.driver,time)
                                .until(EC.presence_of_all_elements_located((By.XPATH, i)))) #retorna o primeiro que ele encontrar do xpath_list
                    
                    return elements
                except:
                    pass

        if element_number_click is not None:
            try:
                elements[element_number_click].click() # message: element not iteractable
            except:
                pass

        if click_all is not False:
            for element in elements:
                element.click()

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


    def go_to_element(self, xpath_list:list=None, time=5, tries=10, tries_count=0):
        # ir para o elemento, caso esteja disponivel no html
        elements = self.get_element_list(xpath_list, time)

        if elements is not None:
            for element in elements:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                sleep(randint(2,4))
                return 'Elemento encontrado'

        # caso contrário, rolar a tela para baixo e executar novamente a função
        tries_count += 1
        if tries_count == tries:
            return 'Elemento não encontrado'

        # Rolar a página para baixo
        self.driver.execute_script("window.scrollBy(0, 200);")

        sleep(randint(2,4))
        self.go_to_element(xpath_list, time, tries, tries_count)


    def go_to_html_head(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def get_page_html(self):
        return self.driver.page_source
    
    def click_vermais(self, position_change=False):
        position_before = self.driver.execute_script("return [window.pageXOffset, window.pageYOffset];")
        
        self.get_element_list('//div[text()="Ver mais"]', time=5, element_number_click=0)
        sleep(randint(2,4))
        
        if position_change is not True:
            self.driver.execute_script("window.scrollTo(arguments[0], arguments[1]);", position_before[0], position_before[1])

    
class Scraper(Driver):

    # funções para integração do chrome com o html
    def __init__(self):
        super().__init__()
        self.html = None
        self.soup = None
        self.structure = None
        self.posts = {} # ex: 'janeiro': [post(id=1), post(id=2)...]
        self.xpaths = {'facebook_post_text': '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{id}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div/div/span/div/div',
                       'facebook_reels_text': '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{id}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[1]/div/a/div[1]/div[2]/div/div/div[2]/span//div',
                       'facebook_reels_date': '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{id}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[1]/div/a/div[1]/div[3]/div/div/div[1]/div/div/div[2]/div/div[2]/span/span/span/span[2]'
        }

    def renew_html(self):
        self.html = super().get_page_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.structure = html.fromstring(str(self.soup))

    # funções de regex para tratamento de texto
    def remove_emoji(self, text:str):
    # Regex para identificar emojis com base nos intervalos Unicode
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200c"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.sub(r'', text)


    # funções para coletar os elementos do post
    def get_text(self, id):
        # função para conseguir o texto do post
        self.renew_html()

        self.click_vermais()
        
        self.go_to_element([
            self.xpaths['facebook_post_text'].format(id=id),
            self.xpaths['facebook_reels_text'].format(id=id)
            ])
        

        self.renew_html() # pois clicou em ver mais e alterou o texto

        # Encontrar texto pelo xpath (caminho de um post normal de facebook)
        elements = list(dict.fromkeys(self.structure.xpath(self.xpaths['facebook_post_text'].format(id=id))))

        if len(elements) == 0: # se o elemento for um reel no facebook
            elements = list(dict.fromkeys(self.structure.xpath(self.xpaths['facebook_reels_text'].format(id=id))))

        if len(elements) > 0:

            texts = [self.remove_emoji(element.text_content()).strip() for element in elements]

            full_text = self.remove_emoji(" ".join(texts).lstrip().replace('Ver menos', ''))

            if "… Ver mais" in full_text:
                self.driver.execute_script("window.scrollBy(0, 300);")
                sleep(randint(2,4))
                self.click_vermais(position_change=True)

                sleep(randint(2,4))
                self.renew_html()

                elements = list(dict.fromkeys(self.structure.xpath(self.xpaths['facebook_post_text'].format(id=id))))

                if len(elements) == 0: # se o elemento for um reel no facebook
                    elements = list(dict.fromkeys(self.structure.xpath(self.xpaths['facebook_reels_text'].format(id=id))))

                if len(elements) > 0:

                    texts = [element.text_content().strip() for element in elements]

                    full_text = " ".join(texts).replace('Ver menos', '').strip()
                
                    return full_text

            return full_text
        
        else:
            return nan
        
    def get_img_type(self):
        pass

    def get_post_length_by_month(self, month):
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
        
    def __repr__(self) -> str: # ao retornar o post como string
        pass
