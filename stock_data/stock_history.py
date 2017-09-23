#!/usr/bin/python
#coding:utf-8
import pdb
import re
import sys
import random
import datetime
import requests
import argparse
import logging
from pymongo import MongoClient
from bs4 import BeautifulSoup

LOG_PATH = "/data/log/shistory/log"

re_year = r"[\d]{4}-[\d]{2}-[\d]{2}"

_headers = {
        'Host': 'money.finance.sina.com.cn',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/600000.phtml',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cookie': 'UOR=www.baidu.com,astro.sina.com.cn,; SINAGLOBAL=218.240.128.48_1500254263.56856; SUB=_2AkMuMJ9zf8NxqwJRmP4Tzm_qb4h1wgzEieKYbG6oJRMyHRl-yD83qkwAtRBznhtlDrQRhxmuIBxVM-QIbWACDw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WF8ELJks7VTVqI9Cd8TmYJF; U_TRS1=00000033.d6714ed.596c10de.2f87d670; lxlrtst=1501236289_o; Apache=172.16.118.83_1501245742.381549; U_TRS2=00000042.c3f57126.59804a73.04d553b6; ULV=1501579879495:5:1:1:172.16.118.83_1501245742.381549:1501233035508; SGUID=1501579879770_4cbfeeaf; SR_SEL=1_511; lxlrttp=1501462726; FIN_ALL_VISITED=sh600000%2Csh600019; FINA_LV2_S_2=0; FINA_LV2_S_2_B=0; FINANCE2=f26ebf573f99277bb5d2417d1d6b446a; FINA_V_S_2=sh600000,sh600019,sh600001',
        }

proxy_hosts = [
            {"http":"http://161.63.0.90:1128"},
            {"http":"http://161.63.0.91:1128"},
            {"http":"http://161.63.0.92:1128"},
            {"http":"http://161.63.0.93:1128"},
            {"http":"http://161.63.0.94:1128"},
            {"http":"http://161.63.0.95:1128"},
            {"http":"http://161.63.0.96:1128"},
            {"http":"http://161.63.0.97:1128"},
            {"http":"http://161.63.0.98:1128"},
            {"http":"http://161.63.0.99:1128"},
        ]

def get_history(scode,year,quarter):
    url = "http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{0}.phtml?year={1}&jidu={2}"
    print url.format(scode,year,quarter)
    req = None
    re_try = 30
    for i in range(re_try):
    	try:
	    req = requests.get(url.format(scode,year,quarter),headers=_headers,timeout=10) #, proxies=random.choice(proxy_hosts))
            break
	except Exception,e:
	    print e
    html = req.text
    soup = BeautifulSoup(html)
    table = soup.find(id="FundHoldSharesTable")
    if not table:
        return None
    trs = table.find_all("tr")
    if len(trs) < 3:
        return None
    ret = []
    for tr in trs[2:]:
        tds = tr.find_all("td")
        m = re.search(re_year,tds[0].text)
        if not m:
            print url.format(scode,year,quarter)
            print 'Error:not find year!'
            sys.exit(-1)
        rdate = m.group()
        p_open = float(tds[1].text)
        p_high = float(tds[2].text)
        p_close = float(tds[3].text)
        p_low = float(tds[4].text)
        volumn = int(tds[5].text)
        money = int(tds[6].text)
        ret.append({"rdate":rdate,"p_open":p_open,"p_high":p_high,"p_close":p_close,"p_low":p_low,"volumn":volumn,"money":money})
    return ret

def update_stock_history(coll,stock):
    sid = stock[0]
    scode = stock[1]
    year = 1998
    for i in range(19):
        year += 1
        quarter = 0
        for j in range(4):
            if year == 2017 and j == 4:
                continue
            quarter += 1
            rets = get_history(scode,year,quarter)
            if not rets:
                continue
            for ret in rets:
                ret["_id"] = scode+"_"+ret["rdate"]
                ret["scode"] = scode
                ret["ctime"] = datetime.datetime.strptime(ret["rdate"],"%Y-%m-%d")
                try:
                    coll.insert(ret)
                except Exception,e:
                    print e
            print 'Insert {0} of {1}-{2}.'.format(scode,year,quarter)


if __name__ == "__main__":
    #print get_history("600000",2016,1)

    parser = argparse.ArgumentParser(prog="Stock", description = "hehe wo de ming zi jiao zhiyi")
    parser.add_argument("--address", action="store", required=False, default="mongodb://127.0.0.1:10011", help='''mongodb connection string
            mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database]
            forexample: 
            mongodb://root:dagewocuole@250.250.250.250:2500/admin''')
    parser.add_argument('--level', action='store',required=False,default='INFO',help='log message level')
    op = vars(parser.parse_args())
    logging.basicConfig(filename = LOG_PATH, level = getattr(logging, op['level']),
            format = "%(asctime)s %(levelname)s %(message)s")
    
    
    client = MongoClient(op["address"])
    if not client:
        print 'Mongo client is None !'
        sys.exit(0)
    
    db = client["test"]
    coll = db["stock_info"] 
    
    lst_stock = []
    for item in coll.find():
        sid = item['_id']
        lst_stock.append([sid,item["scode"]])
    skip_n = 0
    for index,stock in enumerate(lst_stock[skip_n:]):
        print "index:."+str(index)
        update_stock_history(db["stock_history"],stock)
        

