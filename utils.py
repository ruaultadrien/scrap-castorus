
import datetime

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import pandas as pd
import numpy as np

from constants import BASE_URL


def build_search_url(location, radius, n_rooms, type_, price_min, price_max, min_m_2=0):
    radius_dic = {0: '', 5: 1, 10: 2, 15: 2, 30: 4}
    type_dic = {'house': 1, 'farm': 5, 'immeuble': 9}
    type_code = type_dic[type_]
    radius_code = radius_dic[radius]

    return f"https://www.castorus.com/s/{location[0]},{location[1]},{type_code}-{radius_code}-{min_m_2}--{price_min}-{price_max}-{n_rooms}----------------------"


def get_dataframe_from_url(url, center, type_):
    ppties_dic = {'price': [], 'price_m2': [], 'date_in': [], 'title': [], 'link_castorus': [], 'n_rooms': [],
                  'surface': [], 'evolution': [], 'n_days_up': [], 'link_ad': [], 'center': [], 'type': []}

    res = requests.get(url)
    soup = BeautifulSoup(res.content)
    soup_res = soup.find('table', id='myTableResult')

    if soup_res == None:
        print('No data available...')
        return pd.DataFrame(ppties_dic)
    soup_res = soup_res.find('tbody')

    for res in tqdm(soup_res, desc='Iterating over properties'):
        ppties_dic['price'] += [int(res.find('td', {"class": 'price'}).string)]

        pm2_classes = iter(
            ['hide_mobile price', 'hide_mobile price green', 'hide_mobile price red'])
        pm2 = None
        while pm2 == None:
            curr_class = next(pm2_classes)
            pm2 = res.find('td', {"class": curr_class})
        ppties_dic['price_m2'] += [int(pm2.string)]

        parsed_date = res.find('span').string.split('/')
        d = [int(i) for i in parsed_date]
        ppties_dic['date_in'] += [datetime.datetime(
            year=int(d[2]), month=int(d[1]), day=int(d[0]))]

        title_field = res.find('td', {"class": 'title'})
        ppties_dic['title'] += [title_field.string]
        castorus_url = BASE_URL + title_field.find('a')['href']
        ppties_dic['link_castorus'] += [castorus_url]

        next_castorus_soup = BeautifulSoup(requests.get(castorus_url).content)
        link_element = next_castorus_soup.find('a', {'id': 'Redir_A'})
        if link_element == None:
            print('Link broken at castorus_url', castorus_url)
            print(ppties_dic['price'][-1], ppties_dic['title'][-1])
            ppties_dic['link_ad'] += [None]
        else:
            url_ad_redir = link_element['href']
            ppties_dic['link_ad'] += [BASE_URL + '/' + url_ad_redir]

        ppties_dic['n_rooms'] += [res.find('td',
                                           {"class": 'hide_mobile piece'}).string]

        ppties_dic['surface'] += [res.find('td', {"class": 'surf'}).string]

        evol = res.find('td', {"class": 'hide_mobile evol'}).string
        if evol != None and evol != 'stable':
            for char in ['(', ')', '%']:
                evol = evol.replace(char, '')
            evol = float(evol)
        else:
            evol = np.nan
        ppties_dic['evolution'] += [evol]

        ppties_dic['n_days_up'] += [res.find('td', {"class": 'since'}).string]

        ppties_dic['center'] += [center]
        ppties_dic['type'] += [type_]

    return pd.DataFrame(ppties_dic)


def build_df_from_centers(centers, radius):
    types = ['house', 'immeuble', 'farm']
    df = pd.DataFrame()
    for c in tqdm(centers, desc='Iterating over centers'):
        print('Current center:', c)
        for type_ in types:
            target_url = build_search_url(c, radius=radius, n_rooms=10, type_=type_,
                                          price_min=200000, price_max=1200000, min_m_2=200)
            print('Current url:', target_url)
            df_ = get_dataframe_from_url(target_url, c, type_)
            df = df.append(df_)
    return df
