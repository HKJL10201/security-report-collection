import csv
import requests
from bs4 import BeautifulSoup

OUT = 'logs/report_links_ICS_Advisory.csv'


def req(url):
    # define header
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # create Request with header
    req = requests.get(url, headers=header)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def reptile(max_idx=3000, page=1, idx=1, tm=10):
    res = []
    url = 'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A95&search_api_fulltext=&sort_by=field_release_date&page=0'

    while idx <= max_idx:
        print("\r{0: <8}".format(idx), end="")
        soup = req(url)
        links = soup.find_all('h3', class_='c-teaser__title')
        if links == None:
            break
        for link in links:
            href = link.find('a')['href'][1:]
            tar_url = 'https://www.cisa.gov/'+href
            name = link.find('span').text
            res.append([name, tar_url])
            idx += 1

        next_page = soup.find('a', rel='next')
        if next_page == None:
            break
        else:
            url = 'https://www.cisa.gov/news-events/cybersecurity-advisories' + \
                next_page['href']
    return res


def main():
    global OUT
    links = reptile()
    writer = csv.writer(open(OUT, 'w', newline='', encoding='utf-8'))
    writer.writerows(sorted(links))
    print('\n>> reptile done, results are shown in '+OUT)


main()
