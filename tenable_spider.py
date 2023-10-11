import csv
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


def get_all_id():
    res = []
    max_page = 2877
    page = 1
    url = 'https://www.tenable.com/plugins/search?q=cve&sort=&page=%d' % page
    while page <= max_page:
        print(page, end='')
        soup = req(url)
        ids = soup.find_all('a', class_='no-break')
        if len(ids) == 0:
            print('id not found at page: ', page)
            return res
        id_strs = [id_.text for id_ in ids]
        res += id_strs
        # print(res)
        # return
        page += 1
        url = 'https://www.tenable.com/plugins/search?q=cve&sort=&page=%d' % page
    print()
    return res


LOG = 'logs/tenable_ids.log'


def main():
    # global OUT
    ids = get_all_id()
    with open(LOG, 'w') as wt:
        wt.write('\n'.join(ids))
    # print('\n>> reptile done, results are shown in '+OUT)


def html_download():
    with open(LOG) as fp:
        for line in fp:
            url = 'https://www.tenable.com/plugins/nessus/'+line.strip()


main()
