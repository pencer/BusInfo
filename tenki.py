#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
#import requests
import re
import talk
import subprocess
import time

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
    url = "http://www.jma.go.jp/jp/yoho/320.html"
    try:
        st = time.time()
        weather_info = {}
        print("Fetch URL: " + url)
        #r = requests.get(url)
        #r.encoding = r.apparent_encoding
        ##r.encoding = "shift_jis"
        ##print(r.text)
        ##print(r.encoding)
        nav_id = 0
        p = re.compile(r"<[^>]*?>")
        flg_startweather = 0
        flg_firstweather = 0
        msg_pref = ""
        msg_place = ""
        msg_time = ""
        msg_weather = ""
        msg_info = ""
        msg_city = ""
        msg_min = ""
        msg_max = ""
        wgetcmd = ["wget", url, "-O", "-"]
        res = subprocess.run(wgetcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print("Start parsing")
        #for line in r.text.splitlines():
        for line in res.stdout.decode('utf-8').splitlines():
            if line.find("</h1>") > -1:
                res = re.sub(r"<[^>]*?>", "", line.strip()).split(" ")
                msg_pref = res[1]
            elif line.find("<div style=\"float: left\">") > -1:
                if flg_startweather == 1:
                    # store already parsed data
                    #print("store weather")
                    weather_info[msg_place].append((msg_time, msg_weather, msg_info, msg_city, msg_min, msg_max))
                    msg_time = ""
                    msg_weather = ""
                    msg_info = ""
                    msg_city = ""
                    msg_min = ""
                    msg_max = ""
                msg_place = re.sub(r"<[^>]*?>", "", line.strip())
                weather_info[msg_place] = []
            elif line.find("<th class=\"weather\">") > -1:
                #print("start weather")
                if flg_startweather == 1:
                    # store already parsed data
                    #print("store weather")
                    weather_info[msg_place].append((msg_time, msg_weather, msg_info, msg_city, msg_min, msg_max))
                    msg_time = ""
                    msg_weather = ""
                    msg_info = ""
                    msg_city = ""
                    msg_min = ""
                    msg_max = ""
                flg_startweather = 1
                flg_firstweather = 1
            elif line.find("class=\"fortemplate\"") > -1:
                print("end weather")
                if flg_startweather == 1:
                    # store already parsed data
                    #print("store weather")
                    weather_info[msg_place].append((msg_time, msg_weather, msg_info, msg_city, msg_min, msg_max))
                    msg_time = ""
                    msg_weather = ""
                    msg_info = ""
                    msg_city = ""
                    msg_min = ""
                    msg_max = ""
                flg_startweather = 0
            elif line.find("class=\"info\"") > -1:
                tmp = line.strip().split("<br>")
                msg_info = re.sub(r"<[^>]*?>", "", tmp[0])
            elif line.find("class=\"city\"") > -1:
                msg_city = re.sub(r"<[^>]*?>", "", line.strip())
            elif line.find("class=\"max\"") > -1:
                msg_max = re.sub(r"<[^>]*?>", "", line.strip())
            elif line.find("class=\"min\"") > -1:
                msg_min = re.sub(r"<[^>]*?>", "", line.strip())
            elif flg_firstweather == 1:
                res = line.strip()
                msg_weather = res
                tmp2 = res.split("\"")
                tmp1 = res.split("<")
                msg_time = tmp1[0]
                if len(tmp2) > 6:
                    msg_weather = tmp2[5]
                flg_firstweather = 0
        #print(msg_place)
        #print(msg_weather)
        #print(weather_info)

        target_area = '東部'
        wi = weather_info[target_area]
        msg_forecast = ""
        itemcnt = 0
        for item in wi:
            val = item[1].replace(u'後', u'のち')
            val = val.replace(u'一時雨', u'一時あめ')
            msg_forecast += item[0] + u'、' + val + u'。'
            val = item[2].replace(u'後', u'のち')
            val = val.replace(u'海上　では', u'海上では')
            val = val.replace(u'　から', u'から')
            val = val.replace(u'一時雨', u'一時あめ')
            if short_mode != 1:
                msg_forecast += val + u'。' # details
            if item[3] != "":
                msg_forecast += item[3] + u'の気温。'
            if item[4] != "":
                msg_forecast += u'最低、' + item[4] + u'。'
            if item[5] != "":
                msg_forecast += u'最高、' + item[5] + u'。'
            if itemcnt >= 1:
                break # upto two items are used
            itemcnt += 1
        if short_mode == 1:
            msg_speak = msg_pref + target_area + u'の天気予報をお伝えします。' + msg_forecast + u'以上、ショートバージョンでお伝えしました。じゃぁね。バイバイ。'
        else:
            msg_speak = msg_pref + target_area + u'の天気予報をお伝えします。' + msg_forecast + u'以上です。バイバイ。'
        dt = time.time() - st
        print(dt)
        #print(msg_speak)
        talk.speak_message(msg_speak)

    #except requests.exceptions.RequestException as err:
    #    print(err)
    except:
        print("Error.")
