import requests
from bs4 import BeautifulSoup
import time
from pprint import pp, pprint
import os


BASE = 'https://cveawg.mitre.org/api/cve/'
IN = 'logs/cve_list_CVE.txt'
OUTPATH = 'bak/cve/'
if not os.path.exists(OUTPATH):
    os.mkdir(OUTPATH)


def req(url):
    attempts = 0
    while True:  # and attempts < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            break

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                attempts += 1
                time.sleep(5)  # wait 5s
                print(f'{url} 503 Server Error, attempt {attempts}')
            else:
                return None
                # raise e
    return response


def getCVEList():
    with open(IN, 'r') as cve_file:
        return cve_file.read().splitlines()


def main():
    cveList = getCVEList()
    for idx, cve in enumerate(cveList):
        if idx >= len(cveList)//2:
            break
        if cve[:3] != 'CVE':
            continue
        url = BASE + cve
        response = req(url)
        if response is None:
            continue
        output = OUTPATH+cve+'.json'
        with open(output, 'w', encoding='utf-8') as out:
            out.write(response.text)
        print(idx, cve)


main()
exit(0)

PKGKEY = 'Package'
VERKEY = 'Version'
CODEKEY = 'Code'


def processTable(table):
    if table is None:
        return []
    res = []
    pkgID = -1
    pkg = ''
    headers = []
    for idx, th in enumerate(table.find_all('th')):
        header = th.text.strip()
        headers.append(header)
        if PKGKEY in header:
            pkgID = idx  # record index of pkg
    for tr in table.find_all('tr')[1:]:  # skip header
        tmp = {}
        for idx, td in enumerate(tr.find_all('td')):
            content = td.text.strip()
            if idx == pkgID:  # if current attr is pkg
                if content:  # if current pkg is not None, record
                    pkg = content
                tmp[headers[idx]] = pkg  # assign pkg
            else:
                tmp[headers[idx]] = content
        res.append(tmp)
    return res


def postProcessTable(table: list):
    res = []
    pkgs = []
    for entry in table:
        tmp = {}
        for key in entry.keys():
            item = entry[key]
            if PKGKEY in key:
                tmp[PKGKEY] = item
            elif VERKEY in key:
                tmp[VERKEY] = item
        currPkg = tmp[PKGKEY]
        if currPkg not in pkgs:
            pkgs.append(currPkg)
            res.append(tmp)
    return res


def insertTable(table, key, value):
    for entry in table:
        entry[key] = value


def dedupTable(table):
    pkgs = []
    res = []
    for entry in table:
        currPkg = entry[PKGKEY]
        if currPkg not in pkgs:
            pkgs.append(currPkg)
            res.append(entry)
    return res


def processHTML(html):
    soup = BeautifulSoup(html, 'html.parser')

    table_heading = soup.find('h2', string='Vulnerable and fixed packages')
    table1 = table_heading.find_next('table') if table_heading else None
    table2 = table1.find_next('table') if table1 else None

    t1 = processTable(table1)
    t1 = postProcessTable(t1)
    insertTable(t1, CODEKEY, 1)
    t2 = processTable(table2)
    t2 = postProcessTable(t2)
    insertTable(t2, CODEKEY, 2)
    res = t2+t1
    res = dedupTable(res)
    return res


def collect():
    cveList = getCVEList()
    res = [['CVE', CODEKEY, PKGKEY, VERKEY]]
    for idx, cve in enumerate(cveList):
        html = ''
        try:
            fn = OUTPATH+cve+'.html'
            fp = open(fn)
            html = fp.read()
        except:
            res.append([cve, 404, '', ''])
            continue
        table = processHTML(html)
        tmp = []
        for entry in table:
            try:
                tmp.append([cve,
                            entry[CODEKEY],
                            entry[PKGKEY],
                            entry[VERKEY]])
            except:
                continue
        if tmp:
            # print(fn)
            # pprint(table)
            # break
            res += tmp
        else:
            res.append([cve, 0, '', ''])
    import csv
    with open('output.csv', 'w', newline='') as wp:
        writer = csv.writer(wp)
        writer.writerows(res)


# collect()
