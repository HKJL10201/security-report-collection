import os

bak='bak'
root='cved'
root=os.path.join(bak,root)
def filter_empty_lines():
    files = os.listdir(root)
    for f in files:
        f = os.path.join(root,f)
        res = []
        with open(f) as rd:
            for line in rd:
                if line.strip() == '':
                    continue
                res.append(line)
        with open(f,'w') as wt:
            wt.writelines(res)

def find_duplicated():
    years=list(range(2013,2024))
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for y in years:
        for m in months:
            print(y,m)
            curr = os.path.join(root,str(y),m)
            if not os.path.exists(curr):
                continue
            files=os.listdir(curr)
            file_list=[]
            for fn in files:
                fidx=fn.split('.')[0].split('_')[-1]
                file_list.append((int(fidx),os.path.join(curr,fn)))
            file_list=sorted(file_list)
            file_list=[_[1] for _ in file_list]
            records=[]
            for fn in file_list:
                try:
                    with open(fn,encoding='utf-8') as rd:
                        text=rd.read()
                        if text in records:
                            print(fn)
                        else:
                            records.append(text)
                except:
                    print(fn)
                    return
# find_duplicated()

def new_format():
    import csv
    outpath='cvedetails'
    outpath=os.path.join(bak,outpath)
    header=['CVE','Published','Last Update','Max CVSS Base Score','EPSS Score','CISA KEV Added','Public Exploit Exists','Summary']
    years=list(range(2013,2024))
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for year in years:
        for month in months:
            curr = os.path.join(root,str(year),month)
            if not os.path.exists(curr):
                continue
            print(year,month)
            files=os.listdir(curr)
            file_list=[]
            for fn in files:
                fidx=fn.split('.')[0].split('_')[-1]
                file_list.append((int(fidx),os.path.join(curr,fn)))
            file_list=sorted(file_list)
            file_list=[_[1] for _ in file_list]

            records=[]
            for fn in file_list:
                try:
                    with open(fn,encoding='utf-8') as rd:
                        head_flag=True
                        for line in rd:
                            if head_flag:
                                head_flag=False
                                continue
                            records.append(line.strip().split('\t'))
                except:
                    print(fn)
                    return
            newpath=os.path.join(outpath,str(year))
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            with open(os.path.join(newpath,month+'.csv'),'w',encoding='utf-8',newline='') as wfp:
                writer=csv.writer(wfp)
                writer.writerow(header)
                writer.writerows(records)

# new_format()

def count():
    years=list(range(2013,2024))
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    count=0
    for y in years:
        for m in months:
            print(y,m)
            curr = os.path.join(root,str(y),m)
            if not os.path.exists(curr):
                continue
            files=os.listdir(curr)
            file_list=[]
            for fn in files:
                fidx=fn.split('.')[0].split('_')[-1]
                file_list.append((int(fidx),os.path.join(curr,fn)))
            file_list=sorted(file_list)
            file_list=[_[1] for _ in file_list]
            
            for fn in file_list:
                try:
                    with open(fn,encoding='utf-8') as rd:
                        text=rd.read()
                        count+=len(text.split('\n'))-1
                except:
                    print(fn)
                    return
    print(count)

count()