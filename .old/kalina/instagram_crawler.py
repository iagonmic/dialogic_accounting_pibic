import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#from parameters import max_try, data_to_stop
from fake_useragent import UserAgent
from time import sleep
import pandas as pd
from datetime import datetime, timedelta
import os
from selenium.webdriver.common.action_chains import ActionChains
import random

from lxml import html
from pdb import set_trace
from platform import system

if system() == 'Windows':
    from parameters import max_try, data_to_stop

if system() == 'Linux':
    max_try = 5

class crawler:
    links = {"insta_login": "https://www.instagram.com/accounts/login/?source=auth_switcher",
             "instagram": "https://www.instagram.com/{0}"}

    def __init__(self, chrome, link, df, prefeitura, facelink):
        self.df = df
        self.pagfacelink = facelink
        self.prefeitura = prefeitura
        self.links["instagram"] = link
        self.chrome = chrome
        self.instagram_posts = []

    def LocateTag(self, tag):
        while True:
            try:
                element = self.chrome.find_element(By.TAG_NAME, tag)
                return element
            except Exception as error:
                print(f"Elemento {tag} não encontrado")
                continue

    def TempLocate(self, xpath, tries):
        for i in range(tries):
            print(f"Tentativa {i + 1}")
            try:
                element = self.chrome.find_element(By.XPATH, xpath)
                return element
            except Exception as error:
                print(f"Elemento {xpath} não encontrado")
                sleep(1)

    def LocateClass(self, classname, tries):
        for n in range(tries):
            try:
                element = self.chrome.find_element(By.CLASS_NAME, classname)
                return element
            except Exception as error:
                print(f"Elemento {classname} não encontrado")
                sleep(1)
                continue

    def RollDown(self):
        footer_classes = "x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye x1fhwpqd xo1l8bm x1roi4f4 x1s3etm8 x676frb x10wh9bi x1wdrske x8viiok x18hxmgj"
        footer_selector = "." + ".".join(footer_classes.split())

        try:
            footer_element = self.chrome.find_element(By.CSS_SELECTOR, footer_selector)
            self.chrome.execute_script("arguments[0].scrollIntoView(true);", footer_element)
            print("Elemento trazido para a visualização com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar trazer o elemento para a visualização: {e}")

    # Instagram methods
    def LoginInsta(self, email, senha):
        self.chrome.get(self.links["insta_login"])
        xpath_email = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input"
        xpath_password = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input"
        xpath_submit = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button"
        xpath_loaded = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div[2]/div/div[1]/div/div/div/div/div/div[2]/div/div/div/a"
        xpath_save = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/div"
        _email = self.TempLocate(xpath_email, 3)
        if not _email:
            pass
        else:
            _password = self.TempLocate(xpath_password, 10)
            _email.send_keys(email)
            _password.send_keys(senha)
            _submit = self.TempLocate(xpath_submit, 10)
            _submit.click()
            save = self.TempLocate(xpath_save, 6)
            if save:
                save.click()
            self.TempLocate(xpath_loaded, 10)

    def open_incognito(self):
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        #options.add_argument("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        chrome = uc.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        return chrome

    def MiningInsta(self, post_links):
        possibles_classes = ["x6s0dn4 x78zum5 xdt5ytf xdj266r xkrivgy xat24cr x1gryazu x1n2onr6 xh8yej3",
                             "x78zum5 xdt5ytf x1q2y9iw x1n2onr6 xh8yej3 x9f619 x1iyjqo2 x18l3tf1 x26u7qi xy80clv xexx8yu x4uap5 x18d9i69 xkhd6sd",
                             "x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x1qjc9v5 x1oa3qoh xl56j7k"]
        xpath_loaded = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]"
        # chrome = self.open_incognito()
        chrome = self.chrome
        for linkpost in post_links:
            chrome.get(linkpost)
            container = None

            comments = []
            self.TempLocate(xpath_loaded, 10)
            sopa = BeautifulSoup(chrome.page_source, "html.parser")
            for possible_class in possibles_classes:
                container = sopa.find("div", {"class": possible_class})
                print(container)
                if container:
                    break
            if not container:
                continue

            textdiv = container.find("div", {"class": "x4h1yfo"}).find("div")
            if not textdiv:
                continue
            if len(textdiv.find_all("div", recursive=False)) == 4:
                title, texts, likes, comment = textdiv.find_all("div", recursive=False)
            elif len(textdiv.find_all("div", recursive=False)) == 3:
                title, texts, likes = textdiv.find_all("div", recursive=False)
            else:
                input("erro")
                continue
            try:
                post, comment_box = texts.find("div").find_all("div", recursive=False)
            except:
                continue
            date = sopa.find_all("span", {
                "class": "x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp xo1l8bm x1roi4f4 x10wh9bi x1wdrske x8viiok x18hxmgj"})
            for dat in date:
                if dat.find("time"):
                    date = dat.find("time").get("datetime")
                    break
                else:
                    date = "Não encontrada"
            post = post.find("div").find_all("div", recursive=False)[-1].find("div").find("span").find("div")
            postText = post.find_all("span", recursive=False)[-1].text

            for c in comment_box.find_all("div", recursive=False):
                try:
                    comment_tag = c.find_all("span", {
                        "class": "x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"})
                    _dict = comment_tag[1].text
                    comments.append(_dict)
                except:
                    continue
            # post = container.find("span",{"class":"x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"}).text
            # comments = [(name_comment.find("a",{"class":"x1i10hfl xjqpnuy xa49m3k xqeqjp1 x2hbi6w xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x1lku1pv x1a2a7pz x6s0dn4 xjyslct x1ejq31n xd10rxx x1sy0etr x17r0tee x9f619 x1ypdohk x1f6kntn xwhw2v2 xl56j7k x17ydfre x2b8uid xlyipyv x87ps6o x14atkfc xcdnw81 x1i0vuye xjbqb8w xm3z3ea x1x8b98j x131883w x16mih1h x972fbf xcfux6l x1qhh985 xm0m39n xt0psk2 xt7dq6l xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x1n5bzlp xqnirrm xj34u2y x568u83"}).text,
            #              name_comment.find("span",{"class":"_ap3a _aaco _aacu _aacx _aad7 _aade"}).text) for name_comment in container.find_all("li",{"class":"_a9zj _a9zl"})]
            curtidas = sopa.find("section", {"class": "x12nagc"}).text.split(" ")[0]
            img = sopa.find("img", {"class": "x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3"})
            if img:
                img = img.get("src")
            else:
                img = None
            print(f"Post: {postText}\nComentários: {comments}\nCurtidas: {curtidas}\n,Link: {linkpost}")
            data_input = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            self.instagram_posts.append(
                {"Post": postText, "Comentários": comments, "Curtidas": curtidas, "Link": linkpost,
                 "Plataforma": "Instagram", "QTD_Comentários": len(comments), "QTD_Compartilhamentos": 0, "Imagem": img,
                 "Data": data_input})
            post_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            stop_date = datetime.strptime(data_to_stop, "%d/%m/%Y")

            print(post_date, stop_date)
            
            if post_date < stop_date:
                break
        # chrome.quit()

    def MiningInsta2(self):
        #xpath_base = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div[1]/div[1]"
        xpath_base = '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div[1]/div[1]/a/div[1]/div[2]'
        xpath_nodispnoivel = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/span"
        xpath_close_1 = "/html/body/div[7]/div[1]/div/div[2]"
        xpath_close_2 = "/html/body/div[8]/div[1]/div/div[2]"
        _posts = []
        tries = 0
        run = True
        nodisponivel = self.templocate(xpath_nodispnoivel, 3)
        if nodisponivel:
            if nodisponivel.text.strip() == "Esta página não está disponível.":
                run = False
        xpath_post = xpath_base
        post = self.TempLocate(xpath_post, 1)
        while not post and run:
            post = self.TempLocate(xpath_post, 2)
            tries += 1
            if tries >= max_try:
                run = False
            nodisponivel = self.templocate(xpath_nodispnoivel, 3)
            if nodisponivel:
                if nodisponivel.text.strip() == "Esta página não está disponível.":
                    run = False
        while run:
            # for number in range(qtd_posts):
            #     n = number+1
            #     xpath = xpath_base.format(actual_post,n)
            #     post = self.TempLocate(xpath,1)
            #     while not post:
            #         __tries = 0
            #         post = self.TempLocate(xpath,2)
            #         if not post:
            #             __tries +=1
            #             while actual_post>1:
            #                 xpath = xpath_base.format(__tries, n)
            #                 post = self.TempLocate(xpath, 1)
            #                 if post and post not in _posts:
            #                     actual_post = __tries
            #                     break
            #                 if __tries>=10:
            #                     __tries = 0
            #                     self.RollDown()
            #                     sleep(1)
            #                     tries += 1
            #                     if tries>=max_try:
            #                         run = False
            #                         break
            #     if not run:
            #         break
            tries = 0
            post.click()
            sleep(random.randint(4, 12))
            sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            post_info = sopa.find("div", {
                "class": "x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x1qjc9v5 x1oa3qoh xl56j7k"})
            if not post_info:
                class_next = "_aaqg "
                post = self.LocateClass(class_next, 50)
                if not post:
                    run = False
                    break
            class_past = "_aaqf"
            past = self.LocateClass(class_past, 2)
            if past:
                choice = random.choice([False,False,False,False,True])
                if choice:
                    if past:
                        class_next = "_aaqg "
                        past.click()
                        next = self.LocateClass(class_next, 3)
                        if not next:
                            run = False
                            break
                        else:
                            sleep(random.randint(2, 4))
                            next.click()
            imgdiv, textdiv = post_info.find_all("div", recursive=False)
            img = imgdiv.find("img")
            if img:
                img = img.get("src")
            else:
                try:
                    img = imgdiv.find("video").get("src")
                    if img:
                        img = "Video"
                except:
                    img = "Video"
            textdiv = textdiv.find("div", {
                "class": "x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1"}).find(
                "div")
            title, comments = textdiv.find_all("div", recursive=False)
            post = comments.find("ul")
            try:
                postDiv, useless, commentsDiv = post.find_all("div", recursive=False)[:3]
            except:
                class_next = "_aaqg "
                post = self.LocateClass(class_next, 3)
                if not post:
                    run = False
                    break
                post.click()
                continue
            postText = postDiv.find("li").find("div").find("div").find_all("div", recursive=False)[-1].find_all("div",
                                                                                                                recursive=False)[
                0]
            postData = postDiv.find("li").find("div").find("div").find_all("div", recursive=False)[-1].find_all("div",
                                                                                                                recursive=False)[
                -1].find("time").get("datetime")
            commentsDiv = commentsDiv.find("div").find("div")
            commentsTexts = [x.find("span", {"class": "_ap3a _aaco _aacu _aacx _aad7 _aade"}) for x in
                             commentsDiv.find_all("div", recursive=False)]
            commentsTexts = [x.text for x in commentsTexts if x is not None]
            data_input = datetime.strptime(postData, "%Y-%m-%dT%H:%M:%S.%fZ")
            data_yymmdd = data_input.strftime("%d/%m/%Y")
            data_to_stop_obj = datetime.strptime(data_to_stop, "%d/%m/%Y")

            print(data_yymmdd)
            
            if data_input < data_to_stop_obj:
                run = False
                break
            link = self.chrome.current_url
            try:
                
                
                # primeira maneira (classes)
                qtd_curtidas = post_info.find("span", {
                    "class": "x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"}).text.replace(
                    " curtidas", "")
                '''

                # segunda maneira (usando lxml)
                estrutura = html.fromstring(str(sopa))
                    
                curtidas_text_list = list(dict.fromkeys(estrutura.xpath(f'/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span/span')))                
                qtd_curtidas = curtidas_text_list[0].text_content()

                if qtd_curtidas == '0':
                    # primeira maneira (antiga)
                    qtd_curtidas = post_info.find("span", {
                        "class": "x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"}).text.replace(
                        " curtidas", "")
                '''
                

            except:
                qtd_curtidas = 0
            # print(f"Post: {postText.text}\nComentários: {commentsTexts}\nCurtidas: {qtd_curtidas}\nLink: {link}\nData: {data_yymmdd}")
            _posts.append(post)
            _dict = {"Post": postText.text, "Comentários": commentsTexts, "Curtidas": qtd_curtidas, "Link": link,
                     "Plataforma": "Instagram", "QTD_Comentários": len(commentsTexts), "QTD_Compartilhamentos": 0,
                     "Imagem": img, "Data": data_yymmdd, "Prefeitura": self.prefeitura, "PagFacebook": self.pagfacelink}
            self.df = self.df._append(_dict, ignore_index=True)
            self.df.to_csv("instagram_posts.csv", index=False, encoding="utf-8-sig", sep=";")
            # close = self.TempLocate(xpath_close_1,1)
            # if not close:
            #     close = self.TempLocate(xpath_close_2,1)
            # ActionChains(self.chrome).move_to_element(close).click().perform()
            class_next = "_aaqg "
            post = self.LocateClass(class_next, 3)
            # post = False
            if not post:
                self.chrome.refresh()
                post = self.LocateClass(class_next, 3)
                # post = False
                if not post:
                    run = False
        return self.instagram_posts

    def templocate(self, xpath, tries):
        for i in range(tries):
            print(f"Tentativa {i + 1}")
            try:
                element = self.chrome.find_element(By.XPATH, xpath)
                return element
            except Exception as error:
                print(f"Elemento {xpath} não encontrado")
                sleep(1)

    def InstaRunner(self):
        self.instagram_posts = []
        xpath_notexist = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div/span"
        insta_links = []
        # self.LoginInsta(login,senha)
        self.GetInstagram()
        print('trying')
        if self.templocate(xpath_notexist, 3):
            if self.templocate(xpath_notexist, 2).text == "Esta página não está disponível.":
                return pd.DataFrame()
        # post_links = [x for x in self.InstagramCrawler()]
        # insta_links.extend(post_links)
        # self.MiningInsta(post_links)
        posts = self.MiningInsta2()
        return pd.DataFrame(posts)

    def GetInstagram(self):
        xpath_loaded = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[2]/section/main/div/div[1]"
        print(self.chrome)
        self.chrome.get(self.links["instagram"])
        posts = self.TempLocate(xpath_loaded, 10)
        return posts

    def InstagramCrawler(self):
        xpath_moreload = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/section/main/div/div[3]/div[1]/div/button"
        runner = True
        tries = 0
        links = []
        links_placeholder = []
        while runner:
            print(tries)
            temp = self.TempLocate(xpath_moreload, 1)
            if temp:
                try:
                    temp.click()
                except:
                    pass
            script = """
            var element = document.querySelector('.x1n2onr6.xzkaem6');
            if (element) {
                element.parentNode.removeChild(element);
            }
            """
            self.chrome.execute_script(script)
            sopa = BeautifulSoup(self.chrome.page_source, "html.parser")
            posts = sopa.find_all("a", {
                "class": "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd"})
            for post in posts:
                link = post.get("href")
                if str(link).startswith(f"/p/") or str(link).startswith(f"/reel/") or str(link).startswith(
                        f"/prefeiturademaceio/"):
                    full_link = f"https://www.instagram.com{link}"
                    links_placeholder.append(full_link)
            new_links = [x for x in links_placeholder if x not in links]
            links.extend(new_links)
            if tries >= max_try:
                runner = False
            if new_links == []:
                tries += 1
                self.RollDown()
                continue
            else:
                tries = 0
        return links


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
        pesquisa_insta = input("Digite o link do instagram: ")

        if system() == 'Windows':
            cookies_folder = os.path.join(os.getcwd(), "cookies")
            chrome = uc.Chrome(user_data_dir=cookies_folder)

        if system() == 'Linux':
            userAgent = UserAgent.random
            chrome_options = Options()
            chrome_options.add_argument("--headless") # modo headless
            chrome_options.add_argument("--no-sandbox")  # Necessário para alguns ambientes de contêiner
            chrome_options.add_argument("--disable-dev-shm-usage")  # Reduz o uso de /dev/shm
            chrome_options.add_argument("--disable-gpu")  # Desativa aceleração de GPU
            chrome_options.add_argument("--disable-software-rasterizer")  # Desativa renderização de software
            chrome_options.add_argument("--disable-extensions")  # Desativa extensões desnecessárias
            chrome_options.add_argument(f"--user-agent={userAgent}")
            cookies_folder = '/home/iagonmic/.config/google-chrome/Default'
            chrome = uc.Chrome(chrome_options=chrome_options, driver_executable_path='/home/iagonmic/data_science/UFPB/dialogic_accounting_pibic/chromedriver-linux64/chromedriver', user_data_dir=cookies_folder)

        if os.path.exists("instagram_posts.csv"):
            posts = pd.read_csv("instagram_posts.csv", encoding="utf-8-sig",sep=";")
        else:
            posts = pd.DataFrame()
        __crawler = crawler(chrome, pesquisa_insta, posts, "", "")
        __crawler.InstaRunner()
        __crawler.chrome.quit()
        del __crawler
