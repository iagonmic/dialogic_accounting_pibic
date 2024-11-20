from instaloader import Instaloader, Profile
from dotenv import dotenv_values, find_dotenv
from itertools import dropwhile, takewhile
from datetime import datetime
import pandas as pd
import re
import os
from time import sleep
from random import randint
from fake_useragent import UserAgent
import numpy as np

def remove_strange_characters(text:str):
    # Regex para identificar emojis com base nos intervalos Unicode
        emoji_pattern = re.compile(
            "["
            u"\n"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200c"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            u"\xa0"
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.sub(r'', text)

env = dotenv_values(find_dotenv())

UNTIL = datetime.strptime(input('Digite a data final em d/m/y: '), '%d/%m/%Y')

profiles = {
    1: "governo.acre",
    2: "governodealagoas",
    3: "governoamapa",
    4: "governo_do_amazonas",
    5: "govba",
    6: "governodoceara",
    7: "gov_df",
    8: "governo_es",
    9: "governogoias",
    10: "governoma",
    11: "govmatogrosso",
    12: "governoms",
    13: "governomg",
    14: "governopara",
    15: "govparaiba",
    16: "governoparana",
    17: "governope",
    18: "governodopiaui",
    19: "govrj",
    20: "governodorn",
    21: "governo_rs",
    22: "governoro",
    23: "govroraima",
    24: "governosc",
    25: "governosp",
    26: "governosergipe",
    27: "governodotocantins",
}

for key, value in profiles.items():
    print(f'{key}: {value}')

profile_user = profiles[int(input('Digite o número de um dos governos acima para pegar os dados: '))]

def main():
    instaloader = Instaloader(user_agent=UserAgent().random, fatal_status_codes=[400], iphone_support=False)
    #instaloader.login(user=env['user'], passwd=env['senha'])
    instaloader.load_session_from_file(username=env['user'], filename='/home/iagonmic/data_science/UFPB/dialogic_accounting_pibic/insta_session')

    posts = Profile.from_username(instaloader.context, profile_user).get_posts()

    df = None

    since = None
    if os.path.exists(os.path.join(os.getcwd(), f'estados/{profile_user}.csv')):
        df = pd.read_csv(f'estados/{profile_user}.csv')
        since = datetime.strptime(df['data'].iloc[-1], '%d/%m/%Y') # continuar a partir da última data do csv
        since = since.replace(day=since.day-1)
    else:
        df = pd.DataFrame()
        since = datetime.now()

    print(f'Since = {since}')

    n = 0
    for post in takewhile(lambda p: p.date > UNTIL, dropwhile(lambda p: p.date > since, posts)):

        comments = [remove_strange_characters(comment.text) for comment in post.get_comments()]

        post_content = {
            'post': remove_strange_characters(post.caption),
            'qtd_curtidas': post.likes,
            'qtd_comentarios': post.comments,
            'data': datetime.strftime(post.date, '%d/%m/%Y'),
            'video': 'Sim' if post.is_video == True else 'Não',
            'url': f'https://www.instagram.com/p/{post.shortcode}/',
            'media_url': post.url,
            'comentarios': [comments]
        }
        
        sleep(max(15, np.random.normal(40, 10)))

        if randint(1, 20) == 1:  # 5% de chance
            tempo_espera = randint(120, 300)  # Pausa longa de 2 a 5 minutos
            print(f"Pausa longa de {tempo_espera} segundos...")
            sleep(tempo_espera)


        print(f"Data atual do post: {datetime.strftime(post.date, '%d/%m/%Y')}")

        df = pd.concat([df, pd.DataFrame(post_content)])

        df.to_csv(f'estados/{profile_user}.csv', index=False)

        print(f'{n} requisições feitas até o momento...')
        
        n += 1

        if n == 200:
            # a cada 200 requisições
            tempo = randint(1800,3600)
            print(f'Dormindo {tempo} segundos')
            sleep(tempo)
            main()
            

if __name__ == '__main__':
    main()