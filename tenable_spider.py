import csv
import requests
from bs4 import BeautifulSoup
import os

import shutil


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
        print(page)
        soup = req(url)
        ids = soup.find_all('a', class_='no-break')
        if len(ids) == 0:
            print('id not found at page: ', page)
            return res
        # id_strs = [id_.text for id_ in ids]
        id_strs = [id_['href'] for id_ in ids]
        res += id_strs
        # print(res)
        # return
        page += 1
        url = 'https://www.tenable.com/plugins/search?q=cve&sort=&page=%d' % page
    print()
    return res


# LOG = 'logs/tenable_ids.log'
LOG = 'logs/tenable_links.log'


def load(filename):
    logs = []
    with open(filename, encoding='utf-8') as fp:
        for line in fp:
            logs.append(line.strip())
    return logs


def get_set(filename):
    return list(set(load(filename)))


def main():
    # global OUT
    ids = get_all_id()
    with open(LOG, 'w') as wt:
        wt.write('\n'.join(ids))
    # print('\n>> reptile done, results are shown in '+OUT)


def write(filename, tar: list):
    with open(filename, 'w', encoding='utf-8') as wt:
        wt.write('\n'.join(tar))


def html_download():
    import time
    dir = 'bak/tenable_html/'
    log = LOG
    # log = 'logs/tenable_error.log'
    cnt = 0
    error = []
    for line in get_set(log):
        cnt += 1
        try:
            # id = line.strip()
            # url = 'https://www.tenable.com/plugins/nessus/'+id
            link = line
            id = link.split('/')[-1]
            url = link
            print(cnt, id)
            soup = req(url)
            # wait = 5
            # while True:
            #     if is404(soup):
            #         time.sleep(wait)
            #         wait+=5
            #         soup = req(url)
            #     else:
            #         break
            if is404(soup):
                error.append(id)
            with open(dir+id+'.html', 'w', encoding='utf-8') as wt:
                wt.write(str(soup))
        except Exception as e:
            print(e)
            print('error in', id)
            break
        # time.sleep(1)

# def diff():
#     logs=[]
#     with open(LOG) as fp:
#         for line in fp:
#             logs.append(line.strip())
#     files=os.listdir('bak/tenable_html/')
#     res=[]
#     for id in logs:
#         found=False
#         for f in files:
#             if id == f.split('.')[0]:
#                 found=True
#                 break
#         if not found:
#             res.append(id)
#     with open('tenable_diff.log','w') as wt:
#         wt.write('\n'.join(res))

# def diff2():
#     logs=[]
#     with open(LOG) as fp:
#         for line in fp:
#             logs.append(line.strip())
#     print(len(logs))
#     print(len(set(logs)))
#     # Output:
#     # 10000
#     # 7784


def is404(soup):
    title = soup.find('title')
    return '404 Error' in title.text


def error404_detection():
    dir = 'bak/tenable_html/'
    files = os.listdir(dir)
    res = []
    for fn in files:
        fpath = dir+fn
        print(fpath)
        with open(fpath, encoding='utf-8') as rd:
            html = rd.read()
            soup = BeautifulSoup(html, 'html.parser')
            if is404(soup):
                res.append(fn.split('.')[0])
    with open('logs/tenable_error2.log', 'w') as wt:
        wt.write('\n'.join(res))


def error_filter():
    error = load('logs/tenable_error.log')
    dir = 'bak/tenable_html.bak/'
    files = os.listdir(dir)
    res = []
    for fn in files:
        fpath = dir+fn
        fid = fn.split('.')[0]
        if fid in error:
            # os.system('mv %s %s'%(fpath,dir+'error/'+fn))
            shutil.move(fpath, dir+'error/'+fn)
            print(fpath)


def file_combine():
    # error=load('logs/tenable_error.log')
    dir = 'bak/tenable_html.bak/'
    tard = 'bak/tenable_html/'
    files = os.listdir(dir)
    target_files = os.listdir(tard)
    res = []
    for fn in files:
        fpath = dir+fn
        # fid=fn.split('.')[0]
        if fn not in target_files:
            # os.system('mv %s %s'%(fpath,dir+'error/'+fn))
            shutil.copy(fpath, dir+'new/'+fn)
            print(fpath)


def link_combine():
    ids = get_set('logs/tenable_ids.log')
    error = get_set('logs/tenable_error.log')
    new = get_set('logs/tenable_links.log')
    res = []
    for idx, id in enumerate(ids):
        if id in error:
            continue
        url = 'https://www.tenable.com/plugins/nessus/'+id
        if url in new:
            continue
        res.append(url)
        print(idx+1, id)
    with open('logs/tenable_links_.log', 'w') as wt:
        wt.write('\n'.join(res))


def count():
    a = get_set('logs/tenable_links.log')
    b = get_set('logs/tenable_links_.log')
    aa = [_.split('/')[-1] for _ in a]
    bb = [_.split('/')[-1] for _ in b]
    all_ids = aa+bb
    c = len(set(a+b))
    a = len(a)
    b = len(b)

    print(a, b, c)
    aa = len(aa)
    bb = len(bb)
    print(aa, bb, len(set(all_ids)))


def dup_name():
    a = get_set('logs/tenable_links.log')
    b = get_set('logs/tenable_links_.log')
    dup = []
    cnt = 0
    for link in b:
        for tar in a:
            id1 = link.split('/')[-1]
            id2 = tar.split('/')[-1]
            if id1 == id2:
                cnt += 1
                dup.append(link)
                old_name = id1+'.html'
                new_name = '.'.join([id1, tar.split('/')[-2], 'html'])
                dir = 'bak/tenable_html/'
                shutil.copy(dir+old_name, dir+new_name)

                soup = req(link)
                with open(dir+old_name, 'w', encoding='utf-8') as wt:
                    wt.write(str(soup))
                print(cnt, old_name)


def delete_dup_name():
    a = get_set('logs/tenable_links.log')
    b = get_set('logs/tenable_links_.log')
    dup = []
    cnt = 0
    dedup = []
    for link in b:
        is_dup = False
        for tar in a:
            id1 = link.split('/')[-1]
            id2 = tar.split('/')[-1]
            if id1 == id2:
                cnt += 1
                is_dup = True
                break
                dup.append(link)
                new_name = '.'.join([id1, tar.split('/')[-2], 'html'])
                dir = 'bak/tenable_html/'
                trash = 'bak/trash/'
                shutil.move(dir+new_name, trash+new_name)
                print(cnt, new_name)
                break
        if not is_dup:
            dedup.append(link)
    write('logs/tenable_links_all.log', dedup+a)


def html2json(soup: BeautifulSoup):
    def get_all_next_nodes(node, stops=['h4','section']):
        res = []
        next_node = node.find_next_sibling()
        while next_node != None and next_node.name not in stops:
            res.append(next_node)
            next_node = next_node.find_next_sibling()
        return res
    def all_p_filter(nodes:list):
        # only flatten the div
        def p_selector(element):
            # if element.name == 'p' and 'class' in element.attrs.keys():
            #     all_p_res.append(element)
            if element.name == 'div':
                for sub_element in element.contents:
                    p_selector(sub_element)
            else:
                all_p_res.append(element)
        all_p_res = []
        for node in nodes:
            p_selector(node)
        return all_p_res
    def get_inner_text(element):
        output = ""
        if element.name is None:
            return str(element)
        elif element.name == 'a':
            output += f"[{element.text}]({element['href']})"
        elif element.name == 'strong':
            # print(element.text.replace(': ',bar))
            output += element.text.replace(': ',bar)
        else:
            # if element.name == 'p' and 'class' in element.attrs.keys():
            #     print(element)
            for sub_element in element.contents:
                output += get_inner_text(sub_element)
        return output
    def list2strlist(nodelist: list):
        res=[]
        for node in nodelist:
            text=get_inner_text(node)
            res.append(text)
        return res
    def list2str(key:str,value:list):
        def zero_filter(strs:list):
            res=[]
            for s in strs:
                if len(s) == 0:
                    continue
                res.append(s)
            return res
        def list2dict(strs:list):
            def is_dict(strs:list):
                for s in strs:
                    if bar not in s:
                        return False
                return True
            if not is_dict(strs):
                return '\n'.join(strs)
            res={}
            for s in strs:
                try:
                    k,v=s.split(bar)
                except:
                    print(s)
                    exit()
                res[k]=v
            return  res
        
        # bar = ' : '
        value = zero_filter(value)
        if key == 'Risk Information':
            res=[]
            bar_idx=[]
            for idx, v in enumerate(value):
                if bar not in v:
                    bar_idx.append(idx)
            bar_idx.append(len(value))
            for idx, bi in enumerate(bar_idx[:-1]):
                tmp=value[bi:bar_idx[idx+1]]
                tmp[0]='Name'+bar+tmp[0]
                res.append(list2dict(tmp))
            return res
        else:
            return list2dict(value)

    bar = '<!-- -->: '
    res = {}
    title = soup.find('title').text.replace(' | Tenable®', '')
    res['Title'] = title
    all_h4 = soup.findAll('h4', class_="border-bottom pb-1")
    for h4 in all_h4:
        key=h4.text
        # if h4.text=='Reference Information':
        res[key] = list2str(key,list2strlist(all_p_filter(get_all_next_nodes(h4))))
    # print(res)
    return res


def convert_all_html():
    import json
    dir = 'bak/tenable_html/'
    outpath = 'bak/tenable_json/'
    files = os.listdir(dir)
    files = sorted(files)
    for cnt,fn in enumerate(files):
        print(cnt,fn)
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

def json_formatter():
    import json
    dir = 'bak/tenable_json/'
    files = os.listdir(dir)
    files = sorted(files)
    for cnt,fn in enumerate(files):
        print(cnt,fn)
        fpath = dir+fn
        dic=None
        with open(fpath, encoding='utf-8') as rd:
            dic=json.load(rd)
        updated = False
        key='See Also'
        if key in dic.keys():
            value=dic[key]
            dic[key] = value.split('\n')
            updated=True
        # return
        if not updated:
            continue
        with open(fpath, 'w', encoding='utf-8') as wt:
            json.dump(dic, wt, indent=4)
# main()
# html_download()
# error404_detection()
# error_filter()
# file_combine()
# link_combine()
# count()
# dup_name()
# delete_dup_name()
# convert_all_html()
json_formatter()
