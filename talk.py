import subprocess

def speak_message(msg):
    #open_jtalk = ['/usr/bin/open_jtalk']
    open_jtalk = ['/home/pi/open_jtalk/open_jtalk-1.11/bin/open_jtalk']
    htsvoice   = ['-m',  '/usr/share/hts-voice/mei/mei_normal.htsvoice']
    #mech       = ['-x',  '/var/lib/mecab/dic/open-jtalk/naist-jdic']
    mech       = ['-x',  '/home/pi/open_jtalk/open_jtalk-1.11/mecab-naist-jdic']
    volume     = ['-g',  '-40']
    volume     = ['-g',  '0']
    speed      = ['-r',  '1.2']
    outfile    = ['-ow', '/dev/stdout']
    outtrace   = ['-ot', 'ttt']
    cmd_jtalk  = open_jtalk + htsvoice + mech + volume + speed + outfile + outtrace
    aplay      = ['aplay']
    device     = ['-D',  'plughw:1,0']
    cmd_aplay  = aplay + device
    print("speak_message: " + msg)
    p1 = subprocess.Popen(cmd_jtalk, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_aplay, stdin=p1.stdout)
    p1.stdin.write(msg.encode('utf-8'))
    p1.stdin.close()
    p2.wait()

