import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#from parameters import max_try,data_to_stop
from time import sleep
import pandas as pd
import os
from datetime import datetime

from lxml import html
from pdb import set_trace
from platform import system

if system() == 'Windows':
    from parameters import max_try, data_to_stop

if system() == 'Linux':
    max_try = 5

class crawler:
    def __init__(self,chrome,link,df,prefeitura,facelink):
        self.link = link
        self.facelink = facelink
        self.df = df
        self.prefeitura = prefeitura
        self.chrome = chrome
        self.twitter_posts = []


    def locate(self,xpath):
        while True:
            try:
                element = self.chrome.find_element(By.XPATH, xpath)
                return element
            except Exception as erro:
                print(f"Elemento {xpath} não encontrado")
                continue

    def LocateTag(self,tag):
        while True:
            try:
                element = self.chrome.find_element(By.TAG_NAME, tag)
                return element
            except Exception as erro:
                print(f"Elemento {tag} não encontrado")
                continue

    def TempLocate(self,xpath,tries):
        for i in range(tries):
            print(f"Tentativa {i+1}")
            try:
                element = self.chrome.find_element(By.XPATH, xpath)
                return element
            except Exception as erro:
                print(f"Elemento {xpath} não encontrado")
                sleep(1)

    def RollDown(self):
        self.chrome.execute_script("window.scrollBy(0, 500);")
        return self.chrome.page_source
    
    # Twitter methods
    def TwitterRunner(self):
        self.twitter_posts = []
        runner = True
        tries = 0
        run = self.GetTwitter()
        if run == []:
            runner = False
        while runner:
            print('runner')
            posts = self.TwitterCrawler()
            new_posts = [x for x in posts if x not in self.twitter_posts]
            self.RollDown()
            self.twitter_posts.extend(new_posts)
            if new_posts==[]:
                tries += 1
            else:
                tries = 0

            if tries==max_try:
                runner = False
        if run != []:
            self.TwitterCommentsRunner()
            # for post in self.twitter_posts:
            #     if not post.get("Comentários"):
            #         post["Comentários"] = ["Sem comentários"]
            #     post["Comentários"] = list(set(post["Comentários"]))

        return pd.DataFrame(self.twitter_posts)

    def open_incognito(self):
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        chrome = uc.Chrome(executable_path=ChromeDriverManager().install(),options=options)
        return chrome

    def TwitterCommentsRunner(self):
        xpath_spam = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[16]/div/div/button"
        #chrome = self.open_incognito()
        chrome = self.chrome
        stop = False
        for post in self.twitter_posts:
            print(post)
            if stop:
                break
            post["Comentários"] = []
            tries = 0
            postlink = post["Link"]
            if postlink is None:
                continue
            chrome.get(postlink)

            while True:
                sleep(5)
                print(tries)
                spam = self.TempLocate(xpath_spam,1)
                if spam:
                    spam.click()
                sopa = BeautifulSoup(chrome.page_source, "html.parser")

                date = sopa.find("a", {
                    "class": "css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"})
                if date:
                    date = date.find("time").get("datetime")
                    data_input = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    data_yymmdd = data_input.strftime("%d/%m/%Y")
                    data_to_stop_obj = datetime.strptime(data_to_stop, "%d/%m/%Y")
                    if data_input < data_to_stop_obj:
                        stop = True
                        run = False
                        break
                    post["Data"] = data_yymmdd
                else:
                    post["Data"] = "Sem data"
                comments = sopa.find_all("div",{"class":"css-175oi2r"})

                commenttext = [x.find("div",{"class":"css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim"}) for x in comments]
                commenttext = [comment.text for comment in commenttext if comment is not None and comment.text not in post["Comentários"]]
                imgdiv = sopa.find("div",{"class":"css-175oi2r r-1niwhzg r-vvn4in r-u6sd8q r-1p0dtai r-1pi2tsx r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-13qz1uu r-1wyyakw r-4gszlv"})
                if imgdiv is not None:
                    img = imgdiv.find("img")
                    if img is not None:
                        post["Imagem"] = img.find("img").get("src")
                    else:
                        post["Imagem"] = "Sem imagem"
                if commenttext!=[]:
                    post["Comentários"].extend(commenttext)
                print(f"Post: {post['Post']}\nComentários: {commenttext}\nData:{post['Data']}")
                if len(commenttext)==post["QTD_Comentários"]:
                    break
                if commenttext==[]:
                    tries += 25
                self.rollDown()
                if tries==max_try:
                    if not post.get("Comentários"):
                        post["Comentários"] = ["Sem comentários"]
                    post["Comentários"] = list(set(post["Comentários"]))
                    post["PagFacebook"] = self.facelink
                    self.df = self.df._append(post,ignore_index=True)
                    self.df.to_csv("twitter_posts.csv", index=False,encoding="utf-8-sig",sep=";")
                    break
                sleep(1)




    def GetTwitter(self):
        xpath_image = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div[1]/div[2]/div/div[2]/div/a/div[4]/div"
        xpath_nonexist= "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span"
        self.chrome.get(self.link)
        if self.TempLocate(xpath_nonexist,3):
            if self.chrome.find_element(By.XPATH,xpath_nonexist).text == "This account doesn’t exist":
                return []
        posts = self.LocateTag("article")

    def TwitterCrawler(self):
        post_list = []

        sopa = BeautifulSoup(self.chrome.page_source, "html.parser")

        articles = sopa.find_all("article")
        for article in articles:
            title = article.find("div",{"class":"css-175oi2r r-zl2h9q"})
            post = article.find("div",{"class":"css-175oi2r"})
            data = article.find('time').get('datetime')[:10]
            if not post or not title: continue
            else:
                post = post.text
                title = title.text
            post = post.replace(title,"")
            comments,retwets,likes,saw = [x.text for x in article.find_all("div",{"class":"css-175oi2r r-18u37iz r-1h0z5md r-13awgt0"})][:4]
            postlink = article.find("a",{"class":"css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"})
            if postlink:
                postlink = postlink.get("href")
                postlink = "https://x.com"+postlink
            post_dict = {
                "Plataforma":"Twitter",
                "Post": post,
                "QTD_Comentários": comments,
                "QTD_Compartilhamentos": retwets,
                "Curtidas": likes,
                "Link": postlink,
                "Data": data
            }
            post_list.append(post_dict)
            print(f"Post: {post}\nComentários: {comments}\nCompartilhamentos: {retwets}\nCurtidas: {likes}\nVisualizações: {saw}\nLink: {postlink}\nData: {data}")
        return post_list
    def rollDown(self):
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
        pesquisa_tw = input("Digite o link do twitter: ")

        if system() == 'Windows':
            cookies_folder = os.path.join(os.getcwd(), "cookies")
            chrome = uc.Chrome(user_data_dir=cookies_folder)

        if system() == 'Linux':
            cookies_folder = '/home/iagonmic/.config/google-chrome/Default'
            chrome = uc.Chrome(driver_executable_path='/home/iagonmic/data_science/UFPB/dialogic_accounting_pibic/chromedriver-linux64/chromedriver', user_data_dir=cookies_folder)

        if os.path.exists("twitter_posts.csv"):
            posts = pd.read_csv("twitter_posts.csv",encoding="utf-8-sig",sep=";")
        else:
            posts = pd.DataFrame()
        __crawler = crawler(chrome,pesquisa_tw,posts,pesquisa_tw,"")
        posts = __crawler.TwitterRunner()
        __crawler.chrome.quit()
        del __crawler

