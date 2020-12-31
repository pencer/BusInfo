#!/bin/bash
PHASE1=$(mktemp)
PHASE2=$(mktemp)
PHASE3=$(mktemp)

function rm_tempfile {
  [[ -f "$PHASE1" ]] && rm -f "$PHASE1"
  [[ -f "$PHASE2" ]] && rm -f "$PHASE2"
  [[ -f "$PHASE3" ]] && rm -f "$PHASE3"
}
trap rm_tempfile EXIT
trap 'trap - EXIT; rm_tempfile; exit -1' INT PIPE TERM
#PHASE1="phase1.html"
#PHASE2="phase2.html"
#PHASE3="phase3.html"

if [ $# -ne 2 ]; then
  echo "Usage: script <userid> <passwd>"
  exit
fi
USERID=$1
PASSWORD=$2

USER_AGENT="Wget/1.17.1 (linux-gnu)"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
#USER_AGENT="Mozilla/5.0 (Linux; Android 7.0; 507SH Build/S1005) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36"


wget --user-agent="$USER_AGENT" --keep-session-cookies --save-cookies cookies.txt https://opac.lib.city.yokohama.lg.jp/opac/OPP0200 -O $PHASE1

reCheckID=`grep reCheck $PHASE1 | head -n 1 | cut -d '"' -f 4`
#echo "reCheckID=$reCheckID"

POSTDATA="\
&USERID=${USERID}\
&PASSWORD=${PASSWORD}\
&LOGIN=\
&MENUNO=0\
&URI=%2Fopac%2FOPP0200\
&SELDATA=\
&SEARCHID=\
&START=\
&LISTCNT=\
&MAXCNT=\
&ORDER=\
&ORDER_ITEM=\
&ID=\
&SEARCHMETHOD=\
&HLDBID=\
&N_URI=\
&N_PAGE=\
&N_VIEW=\
&N_DATA=\
&N_RANGE=\
&N_ORDER=\
&N_ITEM=\
&reCheck=${reCheckID}\
&HEADBGCOLOR=\
&RMFLAG=\
&SKBN=\
&RMSNO=\
"

#echo "POSTDATA=$POSTDATA"

wget --user-agent="$USER_AGENT" --keep-session-cookies --load-cookies cookies.txt --save-cookies cookies2.txt --post-data "$POSTDATA" https://opac.lib.city.yokohama.lg.jp/opac/OPP0200 -O $PHASE2

wget --user-agent="$USER_AGENT" --load-cookies cookies2.txt https://opac.lib.city.yokohama.lg.jp/opac/OPP1000 -O $PHASE3

nkf $PHASE3 

exit
