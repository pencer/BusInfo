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

if [ $# -ne 2 ]; then
  echo "Usage: script <userid> <passwd>"
  exit
fi
USERID=$1
PASSWORD=$2

wget --save-cookies cookies.txt https://opac.lib.city.yokohama.lg.jp/opac/OPP0200 -O $PHASE1

reCheckID=`grep reCheck $PHASE1 | head -n 1 | cut -d '"' -f 4`
#echo "reCheckID=$reCheckID"

POSTDATA="\
&USERID=${USERID}\
&PASSWORD=${PASSWORD}\
&LOGIN=\
&MENUNO=0\
&URI=%2Fopac%2FOPP0100\
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

wget --save-cookies cookies.txt --post-data "$POSTDATA" https://opac.lib.city.yokohama.lg.jp/opac/OPP0200 -O $PHASE2

wget --save-cookies cookies.txt --post-data "$POSTDATA" https://opac.lib.city.yokohama.lg.jp/opac/OPP1000 -O $PHASE3

nkf $PHASE3 

exit
