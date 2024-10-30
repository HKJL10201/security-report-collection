import requests
from bs4 import BeautifulSoup
import time
import csv
import os

BASE = 'https://nvd.nist.gov/vuln/detail/'
IN = 'logs/cve_list.txt'
IN = 'inputSeverity.csv'
IN = 'logs/cve_list_Debian.txt'
OUTPATH = 'bak/nvd2/'
if not os.path.exists(OUTPATH):
    os.mkdir(OUTPATH)


def req(url):
    success = False
    attempts = 0
    while not success:  # and attempts < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            success = True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                attempts += 1
                time.sleep(5)  # wait 5s
                print(f'{url} 503 Server Error, attempt {attempts}')
            else:
                return None
                # raise e
    # if not success:
    #     print(f"Failed to fetch data for {cve_id} after 5 attempts.")
    #     continue
    return response


def getCVEList():
    with open(IN, 'r') as cve_file:
        return cve_file.read().splitlines()


def getCVECsv():
    with open(IN, 'r') as fp:
        reader = csv.reader(fp)
        return [row for row in reader]


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
        output = OUTPATH+cve+'.html'
        with open(output, 'w', encoding='utf-8') as out:
            out.write(response.text)
        print(idx, cve)


main()
exit(0)


def processHTML(html):
    soup = BeautifulSoup(html, 'html.parser')

    tag = soup.find('a', id='Cvss3NistCalculatorAnchor')
    if not tag:
        tag = soup.find('a', id='Cvss2CalculatorAnchor')
    severity = tag.text.strip() if tag else ''

    return severity


def collect():
    cveList = getCVEList()
    res = [['CVE', 'Code', 'Severity']]
    for idx, cve in enumerate(cveList):
        html = ''
        try:
            fn = OUTPATH+cve+'.html'
            fp = open(fn, encoding='utf-8')
            html = fp.read()
        except:
            res.append([cve, 404, ''])
            continue
        severity = processHTML(html)
        code = 1 if severity else 0
        res.append([cve, code, severity])
    with open('outputSeverity.csv', 'w', newline='') as wp:
        writer = csv.writer(wp)
        writer.writerows(res)


def collect2():
    cveList = getCVECsv()
    res = [['CVE', 'Code', 'Severity']]
    for idx, row in enumerate(cveList[1:]):
        print(f'\r{idx}', end='')
        cve, code, svt = row
        html = ''
        if svt:
            res.append(row)
            continue
        try:
            fn = OUTPATH+cve+'.html'
            fp = open(fn, encoding='utf-8')
            html = fp.read()
        except:
            res.append([cve, 404, ''])
            continue
        severity = processHTML(html)
        code = 1 if severity else 0
        res.append([cve, code, severity])
    with open('outputSeverity.csv', 'w', newline='') as wp:
        writer = csv.writer(wp)
        writer.writerows(res)
    print('\ndone')


# collect2()
