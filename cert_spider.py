import csv
import requests
from bs4 import BeautifulSoup
import pprint
import json


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
    dir = 'bak/cert/'
    with open(LOG) as fp:
        for line in fp:
            try:
                id = line.strip().split('#')[-1]
                url = 'https://www.kb.cert.org/vuls/id/' + id
                soup = req(url)
                with open(dir+id+'.html', 'w', encoding='utf-8') as wt:
                    wt.write(str(soup))
            except Exception as e:
                print(e)
                print('error in', id)
                break


# def html2json():
#     import html_to_json
#     import os
#     outpath = 'bak/json/'
#     root = 'bak/cert/'
#     files = os.listdir(root)
#     for filename in files:
#         html = open(root+filename, encoding='utf-8').read()
#         js = html_to_json.convert(html)
#         with open(outpath+filename.replace('.html', '.json'), 'w', encoding='utf-8') as wt:
#             json.dump(js, wt, indent=4)


# main()
# html_download()
# html2json()
'''
Title: str
Overview: str
Description: str
Impact: str
Solution: str
Vendor Information: list
[{
- Name: str
- Status: str
- Vendor Statement: str
- Vendor Information: str
- Addendum: str
}]
CVSS Metrics: list
[{
- Group: str
- Score: str
- Vector: str
}]
References: list[str]
Acknowledgements: str
Other Information: dict
{
- CVE IDs: str
- Severity Metric: str
- Date Public: str
- Date First Published: str
- Date Last Updated: str
- Document Revision: str
}
'''


def parseHTML(filename):
    def load(filename):
        with open(filename, encoding='utf-8') as rd:
            return rd.read()

    def get_inner_text(element):
        output = ""
        if element.name is None:
            return str(element)
        if element.name == 'a':
            output += f"[{element.text}]({element['href']})"
        else:
            for sub_element in element.contents:
                output += get_inner_text(sub_element)
        return output

    def get_title(soup):
        title = soup.find('title', class_='swiftype').text
        return title

    def get_next_node(soup, id):
        node = soup.find('h3', id=id)
        # print(id)
        return node.find_next_sibling()

    def get_next_content(soup, id):
        content = get_next_node(soup, id)
        text = get_inner_text(content)
        return text.strip()

    def get_references(soup):
        links = get_next_content(soup, 'references')
        link_list = links.split('\n')
        return link_list

    def get_other_information(soup):
        def table2dict(element):
            res = {}
            table = element.find('table')
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    res[key] = value
            return res

        content = get_next_node(soup, id='other-information')
        return table2dict(content)

    def get_CVSS_Metrics(soup):
        def table2list(element):
            res = []
            table = element.find('table')
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 3:
                    group = cells[0].get_text(strip=True)
                    score = cells[1].get_text(strip=True)
                    vector = cells[2].get_text(strip=True)
                    dic = {'Group': group,
                           'Score': score,
                           'Vector': vector}
                    res.append(dic)
            return res

        content = get_next_node(soup, id='cvss-metrics')
        return table2list(content)

    def get_vendor_info(soup):
        def vendor2dict(vendor):
            res = {}
            name = vendor['name']
            res['Name'] = name
            keys = ['Status', 'Vendor Statement',
                    'Vendor Information', 'Addendum']
            for h3 in vendor.find_all('h3'):
                for key in keys:
                    if key == h3.text.strip():
                        content = h3.find_next_sibling()
                        text = get_inner_text(content)
                        res[key] = text.strip()
                        break
            return res

        res = []
        node = soup.find('div', id='vendorinfo')
        vendors = node.find_all('div', {'data-type': 'accordion-section'})
        for vendor in vendors:
            res.append(vendor2dict(vendor))
        return res

    res = {}
    html = load(filename)
    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = get_title(soup)
    except:
        title = None
    res['Title'] = title

    for id in ['overview', 'description', 'impact', 'solution']:
        try:
            content = get_next_content(soup, id)
        except:
            content = None
        res[id.capitalize()] = content

    try:
        vendors = get_vendor_info(soup)
    except:
        vendors = None
    try:
        cvss = get_CVSS_Metrics(soup)
    except:
        cvss = None
    try:
        references = get_references(soup)
    except:
        references = None
    try:
        acknowledgements = get_next_content(soup, 'acknowledgements')
    except:
        acknowledgements = None
    try:
        other = get_other_information(soup)
    except:
        other = None

    res['Vendor Information'] = vendors
    res['CVSS Metrics'] = cvss
    res['References'] = references
    res['Acknowledgements'] = acknowledgements
    res['Other Information'] = other
    # print(res)
    return res


def parse_all_html2json():
    import os
    outpath = 'bak/json/'
    root = 'bak/cert/'
    files = os.listdir(root)
    files = sorted(files)
    # i = 0
    for filename in files:
        # if filename<'114757.html':
        #     continue
        print(filename)
        filepath = root+filename
        dic = parseHTML(filepath)
        with open(outpath+filename.replace('.html', '.json'), 'w', encoding='utf-8') as wt:
            json.dump(dic, wt, indent=4)


parse_all_html2json()
