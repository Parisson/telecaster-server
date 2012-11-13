#!/bin/sh

pid=`pgrep jack-rack`

# Audio channel

if [ ! $pid = "" ]; then
 sleep 1
else
 jack-rack -n /etc/telecaster/eq_comp_limit_02.rack > /dev/null &
 sleep 3
 jack_connect system:capture_1 jack_rack:in_1
 jack_connect system:capture_2 jack_rack:in_2
fi

qjackctl &

edcast_jack -c /etc/telecaster/edcast_jack_local.cfg -n LIVE -p jack_rack > /dev/null &

sleep 3

# MONO setup
#jack_disconnect jack_rack:out_2 LIVE:in_2
jack_connect jack_rack:out_1  LIVE:in_1
jack_connect jack_rack:out_2  LIVE:in_2
#jack_connect jack_rack:out_1  system:playback_1
#jack_connect jack_rack:out_1  system:playback_2

# STEREO setup
#jack_connect jack_rack:out_1  LIVE:in_1
#jack_connect jack_rack:out_2  LIVE:in_2
#jack_connect jack_rack:out_1  system:playback_1
#jack_connect jack_rack:out_2  system:playback_2

#VuMeter
meterbridge -t dpm jack_rack:out_1 jack_rack:out_2 &

sleep 3

# Start safe DeeFuzzer
deefuzzer /etc/telecaster/deefuzzer_audio_safe.xml > /dev/null &
