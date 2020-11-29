#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import re
import talk
import subprocess
import json
import os

if __name__ == '__main__':
    argv = sys.argv
    short_mode = 1
    if len(argv) == 2:
        if argv[1] == "-s":
            short_mode = 1
        elif argv[1] == "-l":
            short_mode = 0
        elif argv[1] == "-h":
            print("Usage: script [-s|-l|-h]")
            print("  -s: short version (default)")
            print("  -l: long version")
            print("  -h: show this message")
            sys.exit()
    url1 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP0200"
    url2 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP1000"
    try:
        dirname = os.path.dirname(os.path.abspath(__file__))
        json_open = open(dirname + '/library_ids.json', 'r')
        json_data = json.load(json_open)
        for k in sorted(json_data.keys()):
            username = json_data[k]['NAME']
            userid = json_data[k]['USERID']
            passwd = json_data[k]['PASSWORD']
            checkcmd = [dirname + "/checklibrary.sh", userid, passwd]
            res = subprocess.run(checkcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #print (res.stdout.decode('utf-8'))

            msg_speak = ""
            phase = 0
            book_cnt = 0
            book_titles = ""
            p = re.compile(r"<[^>]*?>")
            for line in res.stdout.decode('utf-8').splitlines():
                if line.find('<FORM NAME="EXTEND"') > -1:
                    phase = 1
                if line.find('<FORM NAME="DELETE"') > -1:
                    phase = 2
                if phase == 1 and line.find('<a href="OPP1500') > -1:
                    data = p.sub(" ", line.strip())
                    book_titles += data + u'、'
                    book_cnt += 1

            msg_speak = username + u'さんが現在貸出中の本は' + str(book_cnt) + u'冊です。' + book_titles
            talk.speak_message(msg_speak)

# requests package is slow... use wget command instead.
#        print("Fetch URL: " + url1)
#        r = requests.get(url1)
#        r.encoding = r.apparent_encoding
#        #r.encoding = "shift_jis"
#        #print(r.text)
#        #print(r.encoding)
#        reCheckID = ""
#        for line in r.text.splitlines():
#            if line.find("reCheck") > -1:
#                dat = line.strip().split('"')
#                reCheckID = dat[3]
#                print("reCheck={}".format(reCheckID))
#                res = re.sub(r"<[^>]*?>", "", line.strip()).split('"')
#                break
#        postdata = {
#            'USERID' : userid,
#            'PASSWORD' : passwd,
#            'LOGIN' : '',
#            'MENUNO' : '0',
#            'URI' : '/opac/OPP0100',
#            'SELDATA' : '',
#            'SEARCHID' : '',
#            'START' : '',
#            'LISTCNT' : '',
#            'MAXCNT' : '',
#            'ORDER' : '',
#            'ORDER_ITEM' : '',
#            'ID' : '',
#            'SEARCHMETHOD' : '',
#            'HLDBID' : '',
#            'N_URI' : '',
#            'N_PAGE' : '',
#            'N_VIEW' : '',
#            'N_DATA' : '',
#            'N_RANGE' : '',
#            'N_ORDER' : '',
#            'N_ITEM' : '',
#            'reCheck' : reCheckID,
#            'HEADBGCOLOR' : '',
#            'RMFLAG' : '',
#            'SKBN' : '',
#            'RMSNO' : ''}
#
#        print("Login URL: " + url1)
#        r = requests.post(url1, data = postdata)
#        r.encoding = r.apparent_encoding
#        print(r.text)
#
#        print("Fetch URL: " + url2)
#        r = requests.post(url2, data = postdata)
#        r.encoding = r.apparent_encoding
#        print(r.text)

    except requests.exceptions.RequestException as err:
        print(err)
