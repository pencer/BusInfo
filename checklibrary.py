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
    silent_mode = 0
    if len(argv) == 2:
        if argv[1] == "-s":
            silent_mode = 1
        elif argv[1] == "-h":
            print("Usage: script [-s|-l|-h]")
            print("  -s: silent mode")
            print("  -h: show this message")
            sys.exit()
    #url1 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP0200"
    #url2 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP1000"
    outhtml = "out.html"
    try:
        dirname = os.path.dirname(os.path.abspath(__file__))
        json_open = open(dirname + '/library_ids.json', 'r')
        json_data = json.load(json_open)
        out_file = open("out.html", 'w')
        out_file.write("<html><head></head><body>")
        for k in sorted(json_data.keys()):
            username = json_data[k]['NAME']
            userid = json_data[k]['USERID']
            passwd = json_data[k]['PASSWORD']
            checkcmd = [dirname + "/checklibrary.sh", userid, passwd]
            #checkcmd = ["cat", "01.html"]
            res = subprocess.run(checkcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #print (res.stdout.decode('utf-8'))

            msg_speak = ""
            phase = 0
            flag_yoyaku = 0
            mode = 0
            book_cnt = 0
            book_titles = ""
            book_duedate = ""
            book_data = [];
            dbg_msg = ""
            p = re.compile(r"<[^>]*?>")
            for line in res.stdout.decode('utf-8').splitlines():
                if line.find('貸出中</FONT>の資料：') > -1:
                    data = p.sub(" ", line.strip())
                    print(data)
                    rent_cnt = int(data[10])
                    #print(rent_cnt)
                    if rent_cnt == 0:
                        flag_yoyaku = 1
                    dbg_msg += data
                if line.find('予約中</FONT>の資料：') > -1:
                    data = p.sub(" ", line.strip())
                    print(data)
                    reserve_cnt = int(data[10])
                    #print(reserve_cnt)
                    dbg_msg += data
                if line.find('<TR class="middleAppArea">') > -1:
                    phase = 1
                    mode = 1
                elif phase == 1 and line.find('<TD ALIGN="CENTER">') > -1:
                    phase = 2
                elif phase == 2 and line.find('<TD ALIGN="CENTER">') > -1:
                    phase = 3
                elif phase == 3:
                    data = p.sub(" ", line.strip()).replace('/0','/')
                    book_duedate = data[5:].replace('/', u'月') + u'日'
                    phase = 4
                if phase == 4 and line.find('<A class="linkcolor_v"') > -1:
                    data = p.sub(" ", line.strip())
                    if flag_yoyaku == 1:
                        book_titles += data + u'、予約日' + book_duedate + u'、'
                    else:
                        book_titles += data + u'、返却期限日' + book_duedate + u'、'
                        #book_data.append(data)
                        book_data.append((data, book_duedate))
                    book_cnt += 1
                    phase = 0
                elif mode == 1 and line.find('</TABLE>') > -1:
                    phase = 0
                    break

            msg_speak = username + u'さんが現在' + dbg_msg + book_titles
            #msg_speak = username + u'さんが現在貸出中の本は' + str(book_cnt) + u'冊です。' + dbg_msg + book_titles
            if silent_mode == 1:
                print(msg_speak)
            else:
                talk.speak_message(msg_speak)
            out_file.write("<h2>{}さんが現在貸出中{}冊</h2><table>".format(username, book_cnt))
            for m in (book_data):
                print(m)
                out_file.write("<tr><td>{}</td><td>{}</td></tr>".format(m[0], m[1]))
            out_file.write("</table>")

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
