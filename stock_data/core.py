#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

'''
采集用户订单信息, 定义了一些工具函数及变量。定义了Coll基类
'''

#from bs4 import BeautifulSoup

import cStringIO as StringIO
import collections
import datetime
import urlparse
import urllib2
import urllib
import json
import time
import gzip

import re

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


class URLResponse(urllib.addinfourl):

    __content_type_re = re.compile(r"charset\s*=\s*([\w-]+)")
    def __init__(self, fp):

        ret = fp
        if fp.headers.get("Content-Encoding") == "gzip":
            ret = gzip.GzipFile(fileobj=StringIO.StringIO(fp.read()))
        elif fp.headers.get("Content-Encoding") == "deflate":
            ret = StringIO.StringIO(zlib.decompress(fp.read()))

        if 'Content-Type' in fp.headers:
            self.encoding = URLResponse.__content_type_re.search(fp.headers["Content-Type"]) 
            if self.encoding != None:
                self.encoding = self.encoding.group(1).lower()

        urllib.addinfourl.__init__(self, ret, fp.headers, fp.geturl(), 
                fp.getcode())


    def getencoding(self, default):
        '''helper function
        return @default if self.encoding == None
        else return self.encoding'''
        if self.encoding == None:
            return default

        return self.encoding

    
def urlopen(url, cookie, user_agent=None, referer=None, data=None, **kv):
    if not url.startswith("http://") and not url.startswith("https://"):
        #test develop just open file
        return open(url)

    header = {}
    header["Cookie"] = cookie
    header["Accept-Encoding"] = "gzip, deflate"

    if user_agent != None:
        header["User-Agent"] = user_agent

    if referer != None:
        header["Referer"] = referer

    for k, v in kv.items():
        header[k] =v

    req = urllib2.Request(url, data, header)
    ret = urllib2.urlopen(req, timeout=15)
    return URLResponse(ret)


def rawhttp(url, data=None, **kv):
    header = {}
    for k,v in kv.items():
        header[k] = v
    req = urllib2.Request(url, data, header)
    ret = urllib2.urlopen(req, timeout=15)
    return URLResponse(ret)


if __name__ == '__main__':
    print 'ok...'
    url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=[[%22hq%22,%22hs_a%22,%22%22,0,4,40]]&callback=FDC_DC.theTableData"
    rep = rawhttp(url, None, **_sinajs_header)
    rep_str = rep.read()
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
            print "sid:%s, scode:%s, sname:%s" % (sid, scode, sname)
            break
        break
    print len(json_data)
    print 'end...'
