from instaloader import Instaloader, Profile
from dotenv import dotenv_values, find_dotenv
from itertools import dropwhile, takewhile
from datetime import datetime
import pandas as pd
import re
import os
from time import sleep
from random import randint

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

SINCE = datetime.now()
UNTIL = datetime(2024, 11, 12)

instaloader = Instaloader()
#instaloader.login(user=env['user'], passwd=env['senha'])
instaloader.load_session_from_file(username=env['user'], filename='/home/iagonmic/data_science/UFPB/dialogic_accounting_pibic/insta_session')

profile_user = 'governope'

posts = Profile.from_username(instaloader.context, profile_user).get_posts()

post_content_list = []

df = None

if os.path.exists(os.path.join(os.getcwd(), f'estados/{profile_user}.csv')):
    df = pd.read_csv(f'estados/{profile_user}.csv')
else:
    df = pd.DataFrame()

n = 0
for post in takewhile(lambda p: p.date > UNTIL, dropwhile(lambda p: p.date > SINCE, posts)):

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
    
    sleep(randint(10,40))

    print(f"\nData atual do post: {datetime.strftime(post.date, '%d/%m/%Y')}\n")

    post_content_list.append(post_content)

    df = pd.concat([df, pd.DataFrame(post_content)])

    df.to_csv(f'estados/{profile_user}.csv', index=False)