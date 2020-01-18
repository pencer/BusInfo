#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import re
import talk
 
if __name__ == '__main__':
    #talk.speak_message(u'あいう')
    #talk.speak_message(u'上矢部')
    #talk.speak_message(u'富士山下に あと9分で到着  運行中')
    #quit();
    argv = sys.argv
    bs_Fujiyamashita = 12117
    bs_HigashitotsukaekiHigashiguchi = 12101
    bs_Kamiyabe = 12203
    bs_TotsukaekiHigashiguchi = 12001
    fromNO = bs_Fujiyamashita
    toNO = bs_HigashitotsukaekiHigashiguchi
    fromNO = bs_Kamiyabe
    toNO = bs_TotsukaekiHigashiguchi
    if len(argv) == 3:
        fromNO = argv[1]
        toNO   = argv[2]
    #fromNO = bs_Kamiyabe
    #toNO = bs_TotsukaekiHigashiguchi
    url = "http://real.kanachu.jp/sp/DisplayApproachInfo?fNO={}&tNO={}&fNM=&tNM=".format(fromNO, toNO)
    try:
        print("Fetch URL: " + url)
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        r.encoding = "shift_jis"
        #print(r.text)
        #print(r.encoding)
        nav_id = 0
        p = re.compile(r"<[^>]*?>")
        msg_curtime = ""
        msg_approach = ""
        msg_destination = ""
        flg_destination = 0
        flg_find_approach = 0
        print("Start parsing")
        for line in r.text.splitlines():
            if flg_destination == 0 and line.find("<dt class=\"bg02\">目的地</dt>") > -1:
                flg_destination = 1
            if flg_destination == 1 and line.find("<p><strong>") > -1:
                res = p.sub(" ", line.strip())
                msg_destination = res.strip()
                flg_destination = 2
            if line.find("<nav id=early1>") > -1:
                nav_id = 1
            if line.find("<nav id=early2>") > -1:
                nav_id = 2
            if nav_id == 1:
                if line.find("time01") > -1:
                    res = p.sub(" ", line.strip())
                    msg_curtime = res.replace(':', u'時').replace(u'現在', u'分現在の').strip()
                    msg_approach = ""
                    flg_find_approach = 1
                #elif flg_find_approach == 1 and line.find("<p class=\"font13\">") > -1:
                elif flg_find_approach == 1 and line.find("<div class=\"frameArea12\">") > -1:
                    flg_find_approach = 2
                elif flg_find_approach == 2 and len(line.strip()) > 0:
                    if line.find("</p>") > -1:
                        flg_find_approach = 0
                    else:
                        res = p.sub(" ", line.strip())
                        msg_approach += res
        talk.speak_message(msg_destination + u'行き、' + msg_curtime + u'情報です。' + msg_approach)
    except requests.exceptions.RequestException as err:
        print(err)
