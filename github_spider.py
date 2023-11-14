from utils import req
from utils import write
from utils import load
from bs4 import BeautifulSoup
import pprint
import time
import json
import os


def is_github_error(soup):
    return True if 'Rate limit · GitHub' == soup.find('title').text.strip() else False


def is_404(soup):
    return True if 'Page not found · GitHub · GitHub' == soup.find('title').text.strip() else False


def spider(category, pages):
    def get_links(url):
        soup = req(url)
        links = soup.find_all(
            'a', class_='Link--primary v-align-middle no-underline h4 js-navigation-open')
        return links, soup
    tm = 5
    res = {}
    for page in range(1, pages+1):
        print('\rpage: %d' % page, end='')
        res[page] = []
        url = 'https://github.com/advisories?page=%d&query=type%%3Areviewed+ecosystem%%3A%s' % (
            page, category)
        links, soup = get_links(url)
        while is_github_error(soup):
            print('\rwait: %d' % page, end='')
            time.sleep(tm)
            links, soup = get_links(url)
        for a in links:
            res[page].append((a['href'], a.text.strip()))
    print()
    return res


LOGPATH = 'bak/github/logs/'
LOG = 'logs/github_links.log'


def main():
    categories = ['composer', 'erlang', 'actions', 'go', 'maven', 'npm',
                  'nuget', 'pip', 'pub', 'rubygems', 'rust', 'swift']
    pages = [95, 1, 1, 53, 168, 129, 22, 88, 1, 31, 27, 2]
    outpath = LOGPATH
    for i in range(len(categories)):
        category = categories[i]
        print(category)
        max_page = pages[i]
        res = spider(category, max_page)
        with open(outpath+'%s-%d.json' % (category, max_page), 'w', encoding='utf-8') as wt:
            json.dump(res, wt, indent=4)


def data_checker():
    path = LOGPATH
    files = os.listdir(path)
    all = 0
    res = []
    for file in files:
        fpath = path+file
        print(fpath)
        with open(fpath, encoding='utf-8') as rd:
            dic = json.load(rd)
            sum = 0
            non25 = []
            for k in dic.keys():
                value = dic[k]
                res += [', '.join(item) for item in value]
                lenk = len(value)
                sum += lenk
                if lenk != 25:
                    non25.append(k)
            print(non25)
            print('>>items:', sum)
            all += sum
    print('>>>all:', all)
    res = list(set(res))
    print('>>> all unique:', len(res))
    write(LOG, '\n'.join(res))


HTMLPATH = 'bak/github/html/'
JSONPATH = 'bak/github/json/'


def html_download():
    outpath = HTMLPATH
    http = 'https://github.com'
    tm = 10
    rd = load(LOG)
    cnt = 0
    for line in rd:
        cnt += 1
        # if cnt<13372:
        #     continue
        print('\rindex: %d' % cnt, end='')
        url = http+line[:31]
        soup = req(url)
        while is_github_error(soup):
            print('\rwait:  %d' % cnt, end='')
            time.sleep(tm)
            soup = req(url)
        if is_404(soup):
            print('\n404 not found at: ', cnt)
            print(url)
            return
        write(outpath+url.split('/')[-1]+'.html', str(soup))
    print()
    return


def html2json(soup):
    def get_all_next_nodes(node, stops=['h2', 'h3']):
        res = []
        next_node = node.find_next_sibling()
        while next_node != None and next_node.name not in stops:
            res.append(next_node)
            next_node = next_node.find_next_sibling()
        return res

    def get_inner_text(element):
        output = ""
        if element.name is None:
            return str(element).strip()
        elif element.name == 'a':
            output += f"[{element.text.strip()}]({element['href']})"
        # elif element.name == 'strong':
        #     # print(element.text.replace(': ',bar))
        #     output += element.text.replace(': ',bar)
        elif element.name == 'svg':
            pass
        else:
            # if element.name == 'p' and 'class' in element.attrs.keys():
            #     print(element)
            for sub_element in element.contents:
                output += get_inner_text(sub_element)
        return output

    def list2strlist(nodelist: list):
        res = []
        for node in nodelist:
            text = get_inner_text(node)
            res.append(text)
        return res

    def get_meta(soup):
        meta_div = soup.find(
            'div', class_='col-12 col-md-9 float-left').find('div', class_='Box Box--responsive')
        # , calss_='text-small color-fg-muted mb-1'
        all_h2 = meta_div.find_all('h2')
        res = {}
        for h2 in all_h2:
            header = h2.text.strip()
            content = get_all_next_nodes(h2)
            content_strlist = list2strlist(content)
            res[header] = content_strlist
        return res

    def get_description(soup):
        import html2text
        desc_div = soup.find('div', class_='Box Box--responsive mt-3')
        content_div = desc_div.find(
            'div', class_='markdown-body comment-body p-0')
        content_str = html2text.html2text(str(content_div))
        return content_str

    def get_severity(soup):
        def get_score(node):
            score = node.find(
                'div', class_='lh-condensed d-flex flex-items-baseline ml-2 color-fg-subtle f5')
            score = get_inner_text(score) if score is not None else ''
            res = score
            level = node.find('span')
            if level is not None:
                level = get_inner_text(level)
                res += ' (%s)' % level
            return res.strip()

        def get_CVSS_matrics(node):
            res = {}
            items = node.find_all(
                'div', class_='d-flex p-1 flex-justify-between')
            for item in items:
                key = item.find('span')
                value = item.find(
                    'div', class_='color-fg-default text-semibold ml-2')
                key = get_inner_text(key)
                value = get_inner_text(value)
                res[key] = value
            return res
        res = {}
        severity_div = soup.find(
            'div', class_='discussion-sidebar-item js-repository-advisory-details')
        score_div = severity_div.find(
            'div', class_='d-flex flex-items-baseline pb-1')
        if score_div is not None:
            res['Score'] = get_score(score_div)
        CVSS_matrics_div = severity_div.find(
            'div', class_='d-flex flex-column mt-2 p-2 border rounded-2')
        if CVSS_matrics_div is not None:
            res['CVSS base metrics'] = get_CVSS_matrics(CVSS_matrics_div)
        CVSS_str = severity_div.find_all('div', class_='mt-2')
        if CVSS_str is not None and len(CVSS_str) >= 2:
            res['CVSS string'] = CVSS_str[-1].text.strip()

        return res

    def get_weaknesses(soup):
        res = []
        weak_div = soup.find_all(
            'div', class_='discussion-sidebar-item js-repository-advisory-details')[1]
        weaks = weak_div.find('div').find_all('a')
        for weak in weaks:
            res.append(get_inner_text(weak))
        return res
    js = {}
    title = soup.find('h2', class_='lh-condensed Subhead-heading').text.strip()
    meta = get_meta(soup)
    description = get_description(soup)
    severity = get_severity(soup)
    weaknesses = get_weaknesses(soup)
    js['Title'] = title
    js['Meta'] = meta
    js['Description'] = description
    js['Severity'] = severity
    js['Weaknesses'] = weaknesses
    misc = soup.find('div', class_='col-12 col-md-3 float-left pt-3 pt-md-0').find_all(
        'div', class_='discussion-sidebar-item')
    for mis in misc[2:5]:
        key = mis.find('h3')  # , class_='mb-2 f6'
        value = mis.find('div')  # , class_='color-fg-muted'
        key = get_inner_text(key)
        value = get_inner_text(value)
        js[key] = value
    return js


def convert_all_html():
    import json
    dir = HTMLPATH
    outpath = JSONPATH
    files = os.listdir(dir)
    files = sorted(files)
    for cnt, fn in enumerate(files):
        print('\r%d: %s' % (cnt, fn), end='')
        fpath = dir+fn
        soup = None
        # fpath = dir+'156262.html'
        # fpath = dir+'103044.html'
        # fpath = dir+'104557.html'
        with open(fpath, encoding='utf-8') as rd:
            html = rd.read()
            soup = BeautifulSoup(html, 'html.parser')
        dic = html2json(soup)
        # return
        with open(outpath+fn.replace('.html', '.json'), 'w', encoding='utf-8') as wt:
            json.dump(dic, wt, indent=4)
    print('\ndone.')


def test():
    fn = HTMLPATH+'GHSA-72hg-5wr5-rmfc'+'.html'
    with open(fn, encoding='utf-8') as rd:
        html = rd.read()
        soup = BeautifulSoup(html, 'html.parser')
        js = html2json(soup)
        print(js)


# main()
# data_checker()
# html_download()
# test()
convert_all_html()
