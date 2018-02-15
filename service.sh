#!/bin/bash

if [ $# -lt 1 ];then
    echo "service.sh start|stop"
    exit
fi

if [ $USER = "gandan" ] && [ $1 = "start" ];then
    
    /usr/bin/python3.4 /home/gandan/gmw_main.py &

elif [ $USER == "gandan" ] && [ $1 == "stop" ] ; then

    ps aux|grep -v grep|egrep gandan.*gmw_main.py|awk '{print $2}'|xargs -Iz kill z

else

    echo "error"

fi
