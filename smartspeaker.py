#!/usr/bin/python
# -*- coding: utf-8 -*-

# https://www.pc-koubou.jp/magazine/20637
import socket
import time

import talk
import subprocess

host = 'localhost'
port = 10500

if __name__ == '__main__':
    # ALSADEV="plughw:2,0" ~/julius/julius/julius/julius -C /home/pi/julius/mydict/am-gmm.jconf -C ~/julius/mydict/am-gmm.jconf -nostrip -gram /home/pi/julius/mydict/mydict -module
    #p = subprocess.Popen(["~/julius/julius/julius/julius", "-C", "/home/pi/julius/mydict/am-gmm.jconf", "-C", "~/julius/mydict/am-gmm.jconf", "-nostrip", "-gram", "/home/pi/julius/mydict/mydict", "-module"], stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen(["/home/pi/julius/smaspe/julius-start.sh"], stdout=subprocess.PIPE, shell=True)
    pid = str(p.stdout.read())
    #pid = str(p.stdout.read().decode('uft-8'))
    time.sleep(3)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    flag_wakeword = 0

    try:
        res = ''
        killword = ''
        while True:
            print("Waiting... killword={}".format(killword))
            while (res.find('\n.') == -1):
                res += sock.recv(1024)
    
            #print("Let's find line with 'WORD=' ...")
            word = ''
            for line in res.split('\n'):
                index = line.find('WORD=')
                #print('OK')
                print(line)
    
                if index != -1:
                    # recognized string found
                    line = line[index + 6:line.find('"', index+6)]
                    if line != '[s]':
                        word = word + line
    
                if word == 'ちゅーりーちゃん':
                    if killword != 'ちゅーりーちゃん':
                        print("なんでしょうか？")
                        talk.speak_message(u"なんでしょうーか？")
                        flag_wakeword = 1
                        killword = 'ちゅーりーちゃん'
                    break
                if word == 'バス':
                    if killword != 'バス':
                        print(u"バスですね。少々お待ちください")
                        talk.speak_message(u"バスですね。少々お待ちください")
                        subprocess.call(["/home/pi/kanachu/BusInfo/kanachu.py", "12117", "12101"])
                        killword = 'バス'
                    break
    
                print(word)
                res = ''
    except KeyboardInterrupt:
        p.kill()
        subprocess.call(["kill " + pid], shell=True)
        sock.close()
