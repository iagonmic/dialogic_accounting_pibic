import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random import randint
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
    
    def get_element(self, xpath:str, click=False):
        element = None
        try:
            element = (WebDriverWait(self.driver,20)
                        .until(EC.presence_of_element_located((By.XPATH, xpath))))
        except:
            pass

        if click is not False:
            element.click()

        return element
    
    def get_element_list(self, xpath:str, click:int=False):
        elements = None
        try:
            elements = (WebDriverWait(self.driver,20)
                        .until(EC.presence_of_all_elements_located((By.XPATH, xpath))))
        except:
            pass

        if click is not False:
            elements[click].click()

        return elements
    
    def type(self, input):
        return ActionChains(self.driver).send_keys(input).perform()

    def facebook_login(self, email, password):
        self.get_url('https://www.facebook.com/')

        # clicar no campo de email e digitar
        self.get_element_list('//input[contains(@class, "inputtext")]', click=0)
        self.type(email)

        # clicar no campo de senha
        self.get_element_list('//input[contains(@class, "inputtext")]', click=1)
        self.type(password)
        
        

driver = Driver()

driver.define_chrome_driver()



