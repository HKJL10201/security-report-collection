from utils import req
import pprint
def test():
    url = 'https://github.com/advisories'
    soup = req(url)
    # print(soup)
    with open('test.html','w',encoding='utf=8') as w:
        w.write(str(soup))
test()