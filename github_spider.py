from utils import req
import pprint
import time
import json
def test():
    page=1
    categories = ['composer', 'erlang', 'actions', 'go', 'maven',
                   'npm', 'nuget', 'pip', 'pub', 'rubygems', 'rust', 'swift']
    pages = [95,1,1,53,168,129,22,88,1,31,27,2]
    url = 'https://github.com/advisories?page=%d&query=type%3Areviewed+ecosystem%3A%s'%(page,categories[0])
    soup = req(url)
    # print(soup)
    with open('test.html','w',encoding='utf=8') as w:
        w.write(str(soup))
# test()

def spider(category,pages):
    def get_links(url):
        soup = req(url)
        links = soup.find_all('a',class_='Link--primary v-align-middle no-underline h4 js-navigation-open')
        return links
    tm=5
    res = {}
    for page in pages:
        res[page] = []
        url = 'https://github.com/advisories?page=%d&query=type%3Areviewed+ecosystem%3A%s'%(page,category)
        links = get_links(url)
        while links is None:
            time.sleep(tm)
            links = get_links(url)
        for a in links:
            res[page].append((a['href'],a.text))
    return res

def main():
    categories = ['composer', 'erlang', 'actions', 'go', 'maven', 'npm', 
                   'nuget', 'pip', 'pub', 'rubygems', 'rust', 'swift']
    pages = [95,1,1,53,168,129,22,88,1,31,27,2]
    outpath = 'bak/github/'
    for i in range(len(categories)):
        category = categories[i]
        max_page = pages[i]
        res = spider(category,max_page)
        with open(outpath+'%s-%d.json'%(category,max_page), 'w', encoding='utf-8') as wt:
            json.dump(res, wt, indent=4)