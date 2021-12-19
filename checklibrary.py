#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import re
import talk
import subprocess
import json
import os
import datetime
import getopt

if __name__ == '__main__':
    argv = sys.argv
    htmlfilename = "out.html"
    silent_mode = 0
    try:
        options, args = getopt.getopt(sys.argv[1:], 'so:h', ['silent', 'outhtml', 'help'])
    except getopt.GetoptError:
        print("Error: given options are not correct.")
        sys.exit()
    for option, value in options:
        if option in ('-s', '--silent'):
            silent_mode = 1
        elif option in ('-o', '--outhtml'):
            htmlfilename = value
        elif option in ('-h', '--help'):
            print("Usage: script [-s|-l|-h]")
            print("  -s: silent mode")
            print("  -o <filename>: specify output HTML file name")
            print("  -h: show this message")
            sys.exit()
    #url1 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP0200"
    #url2 = "https://opac.lib.city.yokohama.lg.jp/opac/OPP1000"
    try:
        dirname = os.path.dirname(os.path.abspath(__file__))
        json_open = open(dirname + '/library_ids.json', 'r')
        json_data = json.load(json_open)
        out_file = open(htmlfilename, 'w')
        out_file.write("<html><head>\n")
        out_file.write("<style type=\"text/css\">\n<!--\n")
        out_file.write("table {font-size:2vw; font-weight:bold;}\n")
        out_file.write("body {height: 100vh;}\n")
        out_file.write(".lv1 {width: 49vw;}\n")
        out_file.write(".lv2 {width: 46vw;}\n")
        out_file.write(".lv2b {width: 10vw;}\n")
        out_file.write("-->\n</style>\n")
        #out_file.write("<meta http-equiv=\"refresh\" content=\"60\">\n")
        out_file.write("</head><body>\n")
        today_dt = datetime.datetime.now()
        out_file.write("<p>{}\時点の情報</p>\n".format(today_dt.strftime('%Y/%m/%d %H:%M:%S')))
        out_file.write("<table><tr>\n")
        idx = 0
        for k in sorted(json_data.keys()):
            username = json_data[k]['NAME']
            userid = json_data[k]['USERID']
            passwd = json_data[k]['PASSWORD']
            checkcmd = [dirname + "/checklibrary.sh", userid, passwd]
            #checkcmd = ["cat", "04.html"]
            res = subprocess.run(checkcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #print (res.stdout.decode('utf-8'))

            msg_speak = ""
            phase = 0
            flag_yoyaku = 0
            mode = 0
            book_cnt = 0
            book_titles = ""
            book_duedate = ""
            book_title = ""
            book_flag_cannotextend = False
            book_flag_reserved = False
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
                    dbg_msg += data + u'、'
                if line.find('予約中</FONT>の資料：') > -1:
                    data = p.sub(" ", line.strip())
                    print(data)
                    reserve_cnt = int(data[10])
                    #print(reserve_cnt)
                    dbg_msg += data
                if line.find('<TR class="middleAppArea">') > -1:
                    phase = 1
                    mode = 1
                elif phase == 1 and line.find('<TD ALIGN="RIGHT">') > -1:
                    # 貸出延長ボックス列(CENTER)が存在する場合としない場合があるため読み飛ばす
                    phase = 2
                elif phase == 2 and line.find('<TD ALIGN="CENTER">') > -1:
                    phase = 3
                elif phase == 3:
                    data = p.sub(" ", line.strip()).strip().replace('/0','/')
                    book_duedate = data
                    phase = 4
                elif phase == 4 and line.find('<A class="linkcolor_v"') > -1:
                    data = p.sub(" ", line.strip())
                    print(data)
                    jbook_duedate = book_duedate[5:].replace('/', u'月') + u'日'
                    if flag_yoyaku == 1:
                        book_titles += data + u'、予約日' + jbook_duedate + u'、'
                    else:
                        book_titles += data + u'、返却期限日' + jbook_duedate + u'、'
                        book_title = data
                    phase = 5
                elif phase == 5:
                    if line.find('延長不可') > -1:
                        book_flag_cannotextend = True
                    if line.find('予約が入っている資料です') > -1:
                        book_flag_reserved = True
                    if line.find('</TR>') > -1:
                        if book_title != "":
                            book_data.append((book_title, book_duedate, book_flag_cannotextend, book_flag_reserved))
                        book_cnt += 1

                        # clear temporary variables
                        book_title = ""
                        book_flag_cannotextend = False
                        book_flag_reserved = False

                        phase = 0
                elif mode == 1 and line.find('</TABLE>') > -1:
                    phase = 0
                    break

            #msg_speak = username + u'さんが現在' + dbg_msg + book_titles
            msg_speak = username + u'さんが現在' + dbg_msg.replace(' ', '').replace(u'：', '') 
            prev_dt = today_dt
            for m in (book_data):
                bookname_str = m[0]
                duedate_str = m[1]
                duedate_dt = datetime.datetime.strptime(duedate_str, '%Y/%m/%d')
                if prev_dt != duedate_dt:
                    jbook_duedate = duedate_str[5:].replace('/', u'月') + u'日'
                    msg_speak += u'、返却期限日' + jbook_duedate + u'、'
                msg_speak += bookname_str + u'、'
                prev_dt = duedate_dt
            #msg_speak = username + u'さんが現在貸出中の本は' + str(book_cnt) + u'冊です。' + dbg_msg + book_titles
            if silent_mode == 1:
                print(msg_speak)
            else:
                talk.speak_message(msg_speak)

            # Output HTML
            out_file.write("<td class=\"lv1\">\n")
            out_file.write("<h2>{}さんが現在貸出中{}冊</h2><table class=\"lv2\">".format(username, book_cnt))
            for m in (book_data):
                print(m)
                duedate_dt = datetime.datetime.strptime(m[1], '%Y/%m/%d')
                if duedate_dt <= today_dt:
                    strflag = u'予約あり' if m[3] == True else u''
                    out_file.write("<tr><td>{}</td><td class=\"lv2b\" style=\"color: red\">{}{}</td></tr>".format(m[0], m[1], strflag))
                else:
                    out_file.write("<tr><td>{}</td><td class=\"lv2b\">{}</td></tr>".format(m[0], m[1]))
            out_file.write("</table>\n")
            out_file.write("</td>\n")
            if (idx%2) == 1:
                out_file.write("</tr><tr>")
            idx += 1
        out_file.write("</tr></table>\n")
        out_file.write("</body></html>\n")

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
