#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import requests
import json
import re
import time
import subprocess
cookie_string=""
cook=""
headers_m = {
    "Accept-Language" : "en-US,en;q=0.8,pt;q=0.6",
    "Connection" : "close",
    "Cookies": cookie_string,
    "Host": "edu.51cto.com",
    "X-Requested-With": "XMLHttpRequest",
    'User-Agent': ''
}
headers_j= {

    "Connection" : "close",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": cook,
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://edu.51cto.com/center/wejob/usr/course-info?train_id=134&train_course_id=362",
    'User-Agent': ''
}
headers_ts= {
    "Connection" : "close",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    'User-Agent': '',
    'Cookie':''
}
# train_id=sys.argv[1]
# start=int(sys.argv[2])
# end=int(sys.argv[3])
path=""

for i in range(3,5):
    page_url = "http://edu.51cto.com/center/wejob/usr/course-infoajax?train_id=134&train_course_id=369&page=%s&size=20"%i
    resp=requests.get(page_url,headers=headers_j)
    lesson_d = json.loads(resp.text)
    lesson_list=lesson_d['data']['data']
    print (len(lesson_list))
    for lesson in lesson_list:
        lesson_id=lesson["lesson_id"]
        raw_name=str(lesson["lesson_name"]).replace("&nbsp",'') #remove html spaces
        lesson_name=re.sub(r'[^\w\s]','',raw_name).strip()
        clean_name=lesson_name.replace(" ","")
        print(clean_name)#remove punctuations
        video_id=lesson["video_id"]
        if video_id != 0:
            m3u8_url="http://edu.51cto.com//center/player/play/m3u8?lesson_id=362_{0}&id={1}&dp=general&type=wejoboutcourse&lesson_type=course".format(lesson_id,video_id)
            resp_m=requests.get(m3u8_url,headers=headers_m)
            resp_content=resp_m.text
            print (resp_content)
            pat=re.compile('https:.*.ts')
            ts_list=pat.findall(resp_content)
            newpath = path + str(lesson_id) + '.ts'
            s=requests.Session()
            for ts in ts_list:
                file_name=ts.split('/')[-1]
                headers_ts['Host']=ts.split('/')[2]
                resp_ts = s.get(ts, headers=headers_ts)
                with open(newpath, "ab") as f:
                    f.write(resp_ts.content) #combine all ts to lesson_id.ts
                time.sleep(0.5)
            subprocess.call('ffmpeg -i %s -bsf:a aac_adtstoasc -vcodec copy '%newpath + str(lesson_id)+"-%s.mp4"%clean_name, shell=True)
            time.sleep(0.5)