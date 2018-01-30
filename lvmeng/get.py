# -*- coding: utf-8 -*-
#from Crypto.Cipher import AES
#import base64
import requests
import xlwt
from bs4 import BeautifulSoup

styleh = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
stylem = xlwt.easyxf('font: name Times New Roman, color-index orange, bold on')
stylen = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')


def getip(url):
    index = requests.get(url)
    i= BeautifulSoup(index.content,'lxml')
    iplist=i.find_all("img",{ "title" : "非常危险" })
    ipall=[]
    for i in iplist:
        u=i.find_next_sibling('a')
        if u==None:
            continue
        ipall.append(u.getText())
    return ipall

def genexcel(ip):
    wbk = xlwt.Workbook(style_compression=2)
    ws = wbk.add_sheet('sheet 1',cell_overwrite_ok=True)
    n=0
    for i in ip:
        host = requests.get('http://172.20.45.115/host/%s.html'%i)
        d = BeautifulSoup(host.content, 'lxml')
        listh=d.find(id='vul_detail').find_all("span",{ "class" : "level_danger_high" })
        lh=[link.string for link in listh]
        listm=d.find(id='vul_detail').find_all("span",{ "class" : "level_danger_middle" })
        lm=[link.string for link in listm]
        print (lm)
        lenall = len(lh) + len(lm)
        ws.write_merge(n, n + lenall-1, 1, 1, i,stylen)
        for index,text in enumerate(lh,start=n):
           ws.write(index, 0, text, styleh)
        for index,text in enumerate(lm,start=n+len(lh)):
           print (index)
           ws.write(index, 0, text, stylem)
        n = n + lenall
    wbk.save('test.xls')

genexcel(getip("http://172.20.45.115/index.html"))