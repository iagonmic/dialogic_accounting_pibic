import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#from parameters import max_try,data_to_stop
from time import sleep
import pandas as pd
from datetime import datetime,timedelta
import os
from selenium.webdriver.common.action_chains import ActionChains
import itertools
import re

from lxml import html
from pdb import set_trace
from platform import system

max_try = 5

def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    if element is None:
        return None
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)
class crawler:
    links = {"facebook": "https://facebook.com/{0}"}


    def __init__(self,chrome,link,tag,df,prefeitura,facelink):
        self.df = df
        self.prefeitura = prefeitura
        self.pagfacebook = facelink
        self.horarios = []
        self.facebook_posts = []
        self.links["facebook"] = link
        self.basepost =  "https://www.facebook.com/{}/posts/".format(tag)
        # self.links["facebook"] = self.links["facebook"].format(link)
        self.chrome = chrome
        self.array_datas = []


    def LocateTag(self, tag):
        while True:
            try:
                element = self.chrome.find_element(By.TAG_NAME, tag)
                return element
            except Exception as error:
                print(f"Elemento {tag} não encontrado")
                continue



    def TempLocate(self, xpath,tries):
        for i in range(tries):
            print(f"Tentativa {i+1}")
            try:
                element = self.chrome.find_element(By.XPATH, xpath)
                return element
            except Exception as error:
                print(f"Elemento {xpath} não encontrado")
                sleep(1)
    
    # Facebook methods
    def GetFacebook(self):
        self.chrome.get(self.links["facebook"])

    def LoginFacebook(self, login, password):
        xpath_login = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[3]/div/label/div/div/input"
        xpath_password = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[4]/div/label/div/div/input"
        xpath_submit = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[5]/div"

        _login = self.TempLocate(xpath_login, 10)
        if not _login:
            return
        _login.send_keys(login)
        _password = self.TempLocate(xpath_password, 10)
        _password.send_keys(password)
        _submit = self.TempLocate(xpath_submit, 10)
        _submit.click()

    def GetPosts(self):
        last_index = 0
        base_post_url = self.basepost
        sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
        all_posts = sopa.find_all("div", {"class": "x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"})
        #data_sopa = xpath_soup(all_posts[0].find("span",{"class":"x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"}))
        "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]"
        print("**")
        for index,post in enumerate(all_posts):
            #data_sopa = [xpath_soup(x.find("span",{"class":"x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"})) for x in posts]
            a_tag = post.find("a", {"class": "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1rg5ohu x1a2a7pz x1ey2m1c xds687c x10l6tqk x17qophe x13vifvy x1pdlv7q"})
            if not a_tag:
                a_tag = post.find("a",{"class":"x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1lliihq x1pdlv7q"})
                if not  a_tag:
                    a_tag = post.find_all("a")
                    if not a_tag:
                        continue
            try:match = re.search(r'fbid=([^&]+)', a_tag.get("href"))
            except:
                continue
            if match:
                tag_id = match.group(1)
            else:
                continue
            url = f"{base_post_url}{tag_id}"
            if url not in self.urls:
                self.urls.append(url)
                print("____")
                print(self.urls)
            sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            
            

    def FacebookRoller(self):
        max_posts = 9999999999
        last_post = None
        posts = [0,0,0]
        runner = True
        tries = 0
        #self.LocateTag("body").click()
        while runner:
            xpath_nonexist = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/h2/span"
            if self.TempLocate(xpath_nonexist,3):
                if self.TempLocate(xpath_nonexist,3).text=="Este conteúdo não está disponível no momento":
                    break
            sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            posts = sopa.find_all("div", { "class" : "x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"})
            print(len(posts))
            print(last_post is not None)
            print(last_post == posts[-1])
            print(posts[-1] != 0)
            if last_post is not None and last_post == posts[-1] and posts[-1] != 0:
                print(last_post.text)
                print(posts[-1].text)
                print("+1 Try")
                print(f"Tries: {tries}")
                tries +=1
            else:
                tries = 0
                self.GetPosts()
            self.chrome.execute_script("window.scrollBy(0, 99999)")

            post_count = len(posts)
            print(post_count)
            if post_count >= max_posts:
                runner = False
            if posts == []:
                posts = [0,0,0]
            last_post = posts[-1]
            if tries == max_try:
                runner = False
                print("Rolagem Finalizada")

    
    def FacebookCrawler(self):

        print('------------ CHEGUEI NO FACEBOOK CRAWLER ---------------')
        meses = {
            "janeiro":1,
            "fevereiro":2,
            "março":3,
            "abril":4,
            "maio":5,
            "junho":6,
            "julho":7,
            "agosto":8,
            "setembro":9,
            "outubro":10,
            "novembro":11,
            "dezembro":12,
        }
        xpath_morefilter = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[2]/div[2]/div/div"
        xpath_alloption = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[3]"
        xpath_load = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[2]/div[3]/div[2]/div/div/div"
        xpathgenerateid = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span/span"
        xpath_body = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[2]/div/div[3]/div/div[1]"
        xpathbuggfreeze = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div/div/span"
        # urls =self.GetPosts()
        urls = self.urls
        for index,url in enumerate(urls):
            self.chrome.get(url)
            sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            # data = [x.get("aria-labelledby") for x in
            #         sopa.find_all("span") if
            #         x.get("aria-labelledby")]
            # data = False
            # if data:
            #     id = data[0]
            #     sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            #     data_text = sopa.find("span", {"id": id})
            #     ActionChains(self.chrome).move_to_element(
            #         self.chrome.find_element(By.XPATH, xpathgenerateid)).perform()
            #     sleep(3)
            #     ActionChains(self.chrome).move_to_element(
            #         self.chrome.find_element(By.XPATH, xpath_body)).perform()
            #     while not data_text:
            #         sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            #         data_text = sopa.find("span", {"id": id})
            #     data = data_text.text
            #     data_year = data.split(" ")[-1]
            #     if int(data_year) <= data_to_stop.split("/")[-1]-1:
            #         break
            comments_shares = sopa.find_all("span",{"class":"x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa"})
            comments = [x.text for x in comments_shares if "comentário" in x.text]
            shares = [x.text for x in comments_shares if "compartilhamento" in x.text]
            comments = int(comments[0].split(" ")[0]) if comments else 0
            shares = int(shares[0].split(" ")[0]) if shares else 0
            textcomments = []
            if comments > 0:
                morefilter = self.TempLocate(xpath_morefilter, 2)
                if morefilter:
                    try:morefilter.click()
                    except Exception as erro:
                        input("Por favor ative as notificações")
                    alloption = self.TempLocate(xpath_alloption, 10)
                    if alloption:
                        alloption.click()
                    self.TempLocate(xpath_load, 10)
                    sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
                    commentsBoxes = sopa.find_all("div", {
                        "class": "xmjcpbm x1tlxs6b x1g8br2z x1gn5b1j x230xth x9f619 xzsf02u x1rg5ohu xdj266r x11i5rnm xat24cr x1mh8g0r x193iq5w x1mzt3pk x1n2onr6 xeaf4i8 x13faqbe"})
                    for commentBox in commentsBoxes:
                        usercommented = commentBox.find("span", {"class": "xt0psk2"})
                        textcomment = commentBox.find("div", {"class": "x1lliihq xjkvuk6 x1iorvi4"})
                        _dict = textcomment.text
                        textcomments.append(_dict)
            curtidas = sopa.find("span",{"class":"xt0b8zv x2bj2ny xrbpyxo xl423tq"})
            if curtidas:
                curtidas = curtidas.text
            else:
                curtidas = 0
            post = sopa.find("div",{"class":"x1iorvi4 x1pi30zi x1l90r2v x1swvt13"})
            if not post:
                continue
            post = post.text
            imagem = sopa.find("img",{"class":"xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3"})
            if imagem:
                imagem = imagem.get("src")
            else:
                imagem = None
            data_span = sopa.find("span",{"class":"x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa xo1l8bm xi81zsa x1yc453h"}).find("span",{"class":"x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"})
            data_xpath = xpath_soup(data_span)
            data = self.TempLocate("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a", 10)
            if data:
                ActionChains(self.chrome).move_to_element(data).perform()
                sleep(2)
                sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
                data_span = sopa.find("span", {
                    "class": "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa xo1l8bm xi81zsa x1yc453h"}).find(
                    "span", {
                        "class": "x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"}).get("aria-describedby")
                data = sopa.find("div", {"id": data_span})
                try:
                    data = data.text
                    useless,util = data.split(",")
                    data,hora = util.split(" às ")
                    dia,mes,ano = data.split(" de ")
                    data = datetime(int(ano),meses[mes.lower()],int(dia))
                    data_input = data.strftime("%d/%m/%Y")
                    hora = hora.split(" ")[0]
                except:
                    data = None
                    data_input = None
                print(f"Post: {post}\nCurtidas: {curtidas}\nQuantidade Comentários: {comments}\nQuantidade Compartilhamentos: {shares},\nComentários: {textcomments},\nData: {data_input}")
            _dict = {"Post":post,"Curtidas":curtidas,"QTD_Comentários":comments,"QTD_Compartilhamentos":shares,"Comentários":textcomments,"Data":data_input,"Link":url,"Plataforma":"Facebook","Imagem":imagem,"PagFacebook":self.pagfacebook}
            self.df = self.df._append(_dict,ignore_index=True)
            #set_trace()
            self.df.to_excel(f"facebook_posts.xlsx",index=False)
            self.facebook_posts.append({"Post":post,"Curtidas":curtidas,"QTD_Comentários":comments,"QTD_Compartilhamentos":shares,"Comentários":textcomments,"Data":data_input,"Link":url,"Plataforma":"Facebook","Imagem":imagem})
        return self.facebook_posts

    def FacebookRunner(self, login, password):
        self.urls = []
        self.facebook_posts = []
        self.GetFacebook()
        self.LoginFacebook(login, password)
        self.FacebookRoller()
        faceposts = self.FacebookCrawler()
        return pd.DataFrame(faceposts)

    def RollDown(self):
        self.chrome.execute_script("window.scrollBy(0, 500);")
        return self.chrome.page_source



if __name__ == "__main__":
    while True:
        data_to_stop = input("Digite a data de parada (dd/mm/aaaa): ")
        while True:
            try:
                datetime.strptime(data_to_stop, "%d/%m/%Y")
                break
            except:
                print("Data inválida")
                data_to_stop = input("Digite a data de parada (dd/mm/aaaa): ")
        pesquisa_face = input("Digite o link do facebook: ")
        tag_face = input("Digite a tag do facebook: ")

        if system() == 'Windows':
            cookies_folder = os.path.join(os.getcwd(), "cookies")
            chrome = uc.Chrome(user_data_dir=cookies_folder)

        if system() == 'Linux':
            cookies_folder = '/home/iagonmic/.config/google-chrome/Default'
            chrome = uc.Chrome(driver_executable_path='/home/iagonmic/data_science/UFPB/dialogic_accounting_pibic/chromedriver-linux64/chromedriver', user_data_dir=cookies_folder)

        if os.path.exists("facebook_posts.xlsx"):
            posts = pd.read_excel("facebook_posts.xlsx")
        else:
            posts = pd.DataFrame()
        __crawler = crawler(chrome,pesquisa_face,tag_face,posts,pesquisa_face,"")
        __crawler.FacebookRunner("user","password")
        __crawler.chrome.quit()
        del __crawler