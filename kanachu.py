#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import re
import subprocess

def speak_message(msg):
    #open_jtalk = ['/usr/bin/open_jtalk']
    open_jtalk = ['/home/pi/open_jtalk/open_jtalk-1.11/bin/open_jtalk']
    htsvoice   = ['-m',  '/usr/share/hts-voice/mei/mei_normal.htsvoice']
    #mech       = ['-x',  '/var/lib/mecab/dic/open-jtalk/naist-jdic']
    mech       = ['-x',  '/home/pi/open_jtalk/open_jtalk-1.11/mecab-naist-jdic']
    volume     = ['-g',  '-40']
    volume     = ['-g',  '0']
    outfile    = ['-ow', '/dev/stdout']
    outtrace   = ['-ot', 'ttt']
    cmd_jtalk  = open_jtalk + htsvoice + mech + volume + outfile + outtrace
    aplay      = ['aplay']
    device     = ['-D',  'plughw:1,0']
    cmd_aplay  = aplay + device
    print("speak_message: " + msg)
    p1 = subprocess.Popen(cmd_jtalk, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_aplay, stdin=p1.stdout)
    p1.stdin.write(msg.encode('utf-8'))
    p1.stdin.close()
    p2.wait()
 
if __name__ == '__main__':
    #speak_message(u'あいう')
    #speak_message(u'上矢部')
    #speak_message(u'富士山下に あと9分で到着  運行中')
    #quit();
    bs_Fujiyamashita = 12117
    bs_HigashitotsukaekiHigashiguchi = 12101
    bs_Kamiyabe = 12203
    bs_TotsukaekiHigashiguchi = 12001
    fromNO = bs_Fujiyamashita
    toNO = bs_HigashitotsukaekiHigashiguchi
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
        speak_message(msg_destination + u'行き、' + msg_curtime + u'情報です。' + msg_approach)
    except requests.exceptions.RequestException as err:
        print(err)
