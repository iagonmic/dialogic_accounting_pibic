from dotenv import find_dotenv, dotenv_values
from playwright.sync_api import Playwright, sync_playwright
import os
import json

from fake_useragent import UserAgent

from time import sleep
from random import randint
import requests

config = dotenv_values(find_dotenv())

ua = UserAgent()

def check_query(response):
    if 'query' in response.url:
        return response.json()

def login_insta(page):
    page.goto("https://www.instagram.com/")
    page.get_by_label("Telefone, nome de usuário ou").click()
    page.get_by_label("Telefone, nome de usuário ou").fill(config['email'])
    page.get_by_label("Senha").click()
    page.get_by_label("Senha").fill(config['senha'])
    page.get_by_role("button", name="Entrar", exact=True).click()

def run(playwright: Playwright) -> None:
    
    url = 'https://www.instagram.com/governope'
    cookies_folder = '/home/iagonmic/.config/google-chrome/Default'

    cookies = os.path.join(os.getcwd(), 'cookies.json')
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(user_agent=ua.random)

    page = browser.new_page()

    login_insta(page)
    
    page.goto(url)

    query_responses = []
    used_json = []

    while True:
        query_responses.append(page.on("response", lambda response: check_query(response)))

        print(query_responses, len(query_responses))

        #for json in query_responses:
        #    if json not in used_json:
        #        used_json.append()

        page.locator("body").press("End")
        sleep(randint(5,15))

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

