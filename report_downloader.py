import csv
import requests
from bs4 import BeautifulSoup
import time
import re

IN = 'logs/report_links_Analysis_Report.csv'
IN = 'logs/report_links_ICS_Advisory.csv'
PATH = 'reports/Analysis_Report/'
PATH = 'reports/ICS_Advisory/'

ENCODING = 'utf-8'


def req(url):
    # define header
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # create Request with header
    req = requests.get(url, headers=header)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def csv_init(filename: str) -> list:
    res = []
    reader = csv.reader(open(filename, 'r', encoding=ENCODING))
    for line in reader:
        res.append(line)
    return res


def main():
    scale = 50

    print("START".center(scale, "-"))
    start = time.perf_counter()
    reader = csv_init(IN)
    max_idx = len(reader)
    for idx, line in enumerate(reader):
        i = int((idx+1)/max_idx*scale)
        a = "*" * i
        b = "." * (scale - i)
        c = (i / scale) * 100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, dur), end="")

        name, url = line
        name = re.sub(
            u"([^\u0041-\u005a\u0061-\u007a\u0030-\u0039])", "", name)
        name = name.replace(' ', '')+url.split('/')[-1]
        soup = req(url)
        with open(PATH+name+'.html', 'w', encoding=ENCODING) as w:
            w.write(soup.prettify())
    print("\n"+"END".center(scale, "-"))


main()
