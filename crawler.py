import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import redis
import random
import threading
import time
import os
import csv

ua = UserAgent()
db = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
cookie_pool=[]
proxy_pool={}
NUM=5000

def spider(number):
    header = {
        'User-Agent': ua.random,
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
        'accept': 'text/html,application/xhtml+xml,application/xml;\
        q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
    }
    movie_id=db.spop('productID')
    url = 'https://www.amazon.com/dp/' + movie_id
    r = requests.get('http://127.0.0.1:5010/get_all/').json()
    if not r:
        proxy = '127.0.0.1:1087'
    else:
        proxy = random.choice(r)['proxy']
    try:
        proxier={'https':proxy}
        response = requests.get(url, headers=header, proxies=proxier)
    except Exception:
        db.sadd('productID',movie_id)
        requests.get('http://127.0.0.1:5010/delete?proxy=' + proxy)
        print(len(r))
        print('Requests Failure!\n\n')
    else:
        if response.status_code == 404:
            print('Getting ' + url)
            print('Number ' + str(number))
            print('Page 404' + '\n\n')
        elif response.status_code == 200:
            if parser(response.text, movie_id, proxy):
                print('Getting ' + url)
                print('Number ' + str(number))
                print('Success!' + '\n\n')
            else:
                print('Getting ' + url)
                print('Number ' + str(number))
                print('Failure!' + '\n\n')
        else:
            print('Getting ' + url)
            print('Number ' + str(number))
            print('Something Wrong!')
            db.sadd('raw_movie_id', movie_id)
            print(str(response.status_code) + '\n\n')


def parser(html, movie_id, proxy):
    soup=BeautifulSoup(html, 'lxml')
    element=soup.find(id='productTitle')
    movie={'id': movie_id}
    if element is None:
        element=soup.find('h1', attrs={'data-automation-id':'title'})
        if element is None:
            print(soup)
            db.sadd('productID', movie_id)
            print('Robot Check!')
            if proxy in proxy_pool:
                proxy_pool[proxy]+=1
                if proxy_pool[proxy]>10:
                    requests.get('http://127.0.0.1:5010/delete?proxy=' + proxy)
            else:
                proxy_pool[proxy]=1
            return False
        else:
            try:
                movie=get_prime_page(soup)
            except Exception:
                print(movie_id)
    else:
        try:
            movie=get_normal_page(soup)
        except Exception:
            print(movie_id)


    if 'title' not in movie:
        print(soup.find('div',class_='content'))
        return False
    save_movie(movie,movie_id)
    return True

def save_movie(movie, movie_id):
    if 'genres' not in movie:
            movie['genres'] = []
    if 'actors' not in movie:
            movie['actors'] = []
    if 'format' not in movie:
            movie['format'] = []
    if 'date' not in movie:
            movie['date'] = []
    if 'directors' not in movie:
            movie['directors'] = []
    with open('./spiderInformation.csv','a+', newline='') as f:
        csv_write = csv.writer(f)
        csv_row=[movie_id, movie['title'],movie['date'],'|'.join(movie['directors']),'|'.join(movie['actors']),'|'.join(movie['genres']),'|'.join(movie['format'])]
        csv_write.writerow(csv_row)

def get_normal_page(soup):
    movie={}
    movie['title'] = soup.find(id='productTitle').text.strip()
    for element in soup.find('div', id='detail-bullets').find('div',class_='content').ul.find_all('li'):
        text=element.text.strip()
        if 'Actors' in text:
            movie['actors']=[item.strip() for item in text.split(':')[1].split(',')]
        elif 'Directors' in text:
            movie['directors']=[item.strip() for item in text.split(':')[1].split(',')]
        elif 'Format' in text:
            movie['format']=[item.strip() for item in text.split(':')[1].split(',')]
        elif 'Genres' in text:
            movie['genres']=[item.strip() for item in text.split(':')[1].split(',')]
        elif 'Release Date' in text:
            movie['date']=text.split(':')[1].strip()

    return movie

def get_prime_page(soup):
    movie={}
    movie['title']=soup.find('h1',attrs={'data-automation-id':'title'}).text
    movie['date']=soup.find('span',attrs={'data-automation-id':'release-year-badge'}).text
    for elements in soup.find('div', attrs={'data-automation-id':'meta-info'}).find_all('dl'):
        text=elements.dd.text.strip()
        if 'Director' in elements.dt.text:
            movie['directors']=[item.strip() for item in text.split(',')]
        elif 'Starring' in elements.dt.text:
            movie['actors']=[item.strip() for item in text.split(',')]
        elif 'Genres' in elements.dt.text:
            movie['genres']=[item.strip() for item in text.split(',')]

    return movie


if __name__=='__main__':
    if not os.path.exists('./spiderInformation.csv'):
        with open('./spiderInformation.csv','w', newline='') as f:
            csv_write = csv.writer(f)
            csv_head = ["ID","Title","Date","Director","Actor","Genres","Format"]
            csv_write.writerow(csv_head)

    for i in range(NUM):
        while threading.active_count() > 30:
            t = 4 * random.random()
            if t < 0.5:
                t += 1.5
            elif t > 3.5:
                t -= 2.5
            time.sleep(t)
        t = threading.Thread(target=spider, args=(i,))
        t.start()

    while threading.active_count() > 1:
        time.sleep(0.2)
    print('------------Finish-----------')

