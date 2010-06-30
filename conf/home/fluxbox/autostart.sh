#!/bin/sh
# Ensure the XPATH variable is set appropriately to the Linux distribution's Xvfb installation path.

pid=`pgrep jack-rack`

if [ ! $pid = "" ]; then 
 sleep 1
else
 jack-rack -n /home/prebarreau/rack/comp_limit_2_02.rack &
 sleep 10
 jack_connect system:capture_1 jack_rack:in_1
 jack_connect system:capture_2 jack_rack:in_2
fi

qjackctl &

