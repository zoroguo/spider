#crawl the newest source of guazi

from urllib.request import urlopen
from urllib.request import HTTPError,URLError
from bs4 import BeautifulSoup
import re

def get_car_num(url):
    html=urlopen(url)
    #print(html)
    bsobj=BeautifulSoup(html.read(),'lxml')
    #print(bsobj)
    car_num=bsobj.findAll('p',{"class":"fr seqtype"})
    car_num=re.findall('\d+',str(car_num))
    print(car_num)


if __name__=='__main__':
    get_car_num(r'https://www.guazi.com/www/buy/')
