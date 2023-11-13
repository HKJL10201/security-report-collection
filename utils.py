import requests
from bs4 import BeautifulSoup


def req(url):
    # define header
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # create Request with header
    req = requests.get(url, headers=header)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup