import requests
from bs4 import BeautifulSoup


def req(url: str) -> BeautifulSoup:
    html = req_raw(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def req_raw(url: str) -> str:
    # define header
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # create Request with header
    req = requests.get(url, headers=header)
    html = req.text
    return html


def write(filename: str, content: str):
    with open(filename, 'w', encoding='utf=8') as w:
        w.write(content)


def load(filename: str) -> list:
    res = []
    with open(filename, 'r', encoding='utf=8') as r:
        for line in r:
            res.append(line.strip())
    return res
