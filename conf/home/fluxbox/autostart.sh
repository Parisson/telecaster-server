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

edcast_jack -c /etc/telecaster/edcast_jack_local.cfg -n LIVE -p jack_rack &
sleep 3

# MONO setup
jack_disconnect jack_rack:out_2 LIVE:in_2
jack_connect jack_rack:out_1  LIVE:in_1
jack_connect jack_rack:out_1  LIVE:in_2

# STEREO setup
#jack_connect jack_rack:out_1  LIVE:in_1
#jack_connect jack_rack:out_2  LIVE:in_2



