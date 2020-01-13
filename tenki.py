#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import re
import subprocess

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 3:
        fromNO = argv[1]
        toNO   = argv[2]
    url = "http://www.jma.go.jp/jp/yoho/320.html"
    try:
        weather_info = {}
        print("Fetch URL: " + url)
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        #r.encoding = "shift_jis"
        #print(r.text)
        #print(r.encoding)
        nav_id = 0
        p = re.compile(r"<[^>]*?>")
        flg_startweather = 0
        flg_startweather = 0
        msg_place = ""
        msg_weather = ""
        print("Start parsing")
        for line in r.text.splitlines():
            if flg_startweather == 0 and line.find("<div style=\"float: left\">") > -1:
                msg_place = re.sub(r"<[^>]*?>", "", line.strip())
                print("place: '{}'".format(msg_place))
                weather_info[msg_place] = {}
            elif flg_startweather == 0 and line.find("<th class=\"weather\">") > -1:
                print("start weather")
                flg_startweather = 1
            elif flg_startweather == 1 and line.find("</th>") > -1:
                print("end weather")
                flg_startweather = 0
            elif flg_startweather == 1 :#and line.find("</th>") > -1:
                print("weather1: '{}'".format(line.strip()))
                #res = p.sub(" ", line.strip())
                res = line.strip()
                msg_weather = res
                tmp2 = res.split("\"")
                tmp1 = res.split("<")
                #print(tmp1)
                #print(tmp2)
                time = tmp1[0]
                weather = tmp2[5]
                print("{}:{}".format(time, weather))
                weather_info[msg_place][time] = weather
        print(msg_place)
        print(msg_weather)
        print(weather_info)
        print("output file")
        filename = "testout.html"
        with open(filename, mode='w') as f:
            wi = weather_info['東部']
            f.write("<html><head></head><body>")
            f.write("<table>")
            for key in wi.keys():
                f.write("<tr><td>'{}'</td><td>'{}'</td></tr>".format(key, wi[key]))
            f.write("</table>")
            f.write("</body></html>")

    except requests.exceptions.RequestException as err:
        print(err)
