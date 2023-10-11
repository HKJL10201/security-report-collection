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
    max_page = 239
    page = 1
    url = 'https://www.kb.cert.org/vuls/bypublished/desc/?page=%d' % page
    while page <= max_page:
        print(page, end='')
        soup = req(url)
        table = soup.find('table', class_='searchby unstriped scroll')
        if table == None:
            print('table not found at page: ', page)
            return res
        rows = table.find('tbody').find_all('tr')
        id_strs = [row.find_all('td')[3].text.strip() for row in rows]
        res += id_strs
        # print(res)
        # return res
        page += 1
        url = 'https://www.kb.cert.org/vuls/bypublished/desc/?page=%d' % page
    print()
    return res


LOG = 'logs/cert_ids.log'


def main():
    # global OUT
    ids = get_all_id()
    with open(LOG, 'w') as wt:
        wt.write('\n'.join(ids))
    # print('\n>> reptile done, results are shown in '+OUT)


def html_download():
    with open(LOG) as fp:
        for line in fp:
            url = 'https://www.kb.cert.org/vuls/id/' + \
                line.strip().split('#')[-1]


main()
