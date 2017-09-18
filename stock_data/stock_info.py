#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

'''
采集用户订单信息, 定义了一些工具函数及变量。定义了Coll基类
'''
import argparse
from core import *
import re
import sys
import time
import requests
from pymongo import MongoClient

_sinajs_r = re.compile(r'FDC_DC.theTableData\(([^\(]*)\)')

_sinajs_header = {
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, sdch",
    "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Connection":"keep-alive",
    "Cookie":"U_TRS1=00000004.ace87445.56dce555.0672ac7e; U_TRS2=00000004.acf87445.56dce555.52559ff4; dpha=usrmdinst_10; UOR=,finance.sina.com.cn,; SINAGLOBAL=221.229.175.52_1457317205.842108; Apache=221.229.175.52_1457317205.842111; vjuids=-28584cc33.1534edfe426.0.f66ee83c; vjlast=1457317209; SGUID=1457317209653_8f76a0d8; ULV=1457317210413:2:2:2:221.229.175.52_1457317205.842111:1457317208738; SUB=_2AkMhgGptf8NhqwJRmPwcxWPmZYl-zAHEiebDAH_sJxJjHn0n7DxnqKWPtjTkcLNC7u0hKDaFLAqvvFIn; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5SwK4CFXkPvyPyOouPn.cl; lxlrtst=1457312560_o; lxlrttp=1457312560",
    #"Host":"money.finance.sina.com.cn",
    "Referer":"http://finance.sina.com.cn/data/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"
    }


def get_info(page=1):
    url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=[[%22hq%22,%22hs_a%22,%22%22,0,"+str(page)+",80]]&callback=FDC_DC.theTableData"
    #rep = rawhttp(url, None, **_sinajs_header)
    #rep_str = rep.read()
    print url
    rep = requests.get(url, headers=_sinajs_header)
    rep_str = rep.text
    json_str = _sinajs_r.search(rep_str).group(1)
    #print json_str
    fp = open('json.data', 'wb')
    fp.write(json_str)
    fp.close()
    json_data = json.loads(json_str)
    for data in json_data:
        items = data["items"]
        for item in items:
            sid = item[0]
            scode = item[1]
            sname = item[2]
            #print "sid:%s, scode:%s, sname:%s" % (sid, scode, sname)
            yield {'_id':sid, 'scode':scode, 'sname':sname}


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="Stock", description = "hehe wo de ming zi jiao zhiyi")
    parser.add_argument("--address", action="store", required=False, default="mongodb://127.0.0.1:10011", help='''mongodb connection string
            mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database]
            forexample: 
            mongodb://root:dagewocuole@250.250.250.250:2500/admin''')
    op = vars(parser.parse_args())
    client = MongoClient(op["address"])
    if not client:
        print 'Mongo client is None !'
        sys.exit(0)
    db = client["test"]
    coll = db["stock_info"]
    #print op
    #sys.exit(0)
    #fp = open("stock.data","wb")
    for i in range(0,83):
        time.sleep(1)
        items = []
        for d in get_info(i):
            try:
                coll.insert_one(d)
                print 'insert info:%s' % d['_id']
            except Exception,e:
                print e
            #fp.write(str(d)+'\n')
            #items.append(d)
        #print len(items)
        #break
    print 'Done...'
    #fp.close()
