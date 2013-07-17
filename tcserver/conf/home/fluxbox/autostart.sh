#!/bin/sh

# ---------------------
# Audio channel
# ---------------------

pid=`pgrep jack-rack`

if [ ! $pid = "" ]; then
 sleep 1
else
 jack-rack -n /etc/telecaster/jack-rack/eq_comp_limit_02.rack > /dev/null &
 sleep 3
fi

jack_connect system:capture_1 jack_rack:in_1
jack_connect system:capture_2 jack_rack:in_2

qjackctl &

/usr/local/share/telecaster/scripts/tc_audio_mp3_icecast.sh &
#edcast_jack -c /etc/telecaster/edcast_jack_local.cfg -n lamemp3enc -p jack_rack > /dev/null &

sleep 2

# MONO setup
jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect jack_rack:out_1 gst-launch-0.10:in_jackaudiosrc0_1

#jack_disconnect system:capture_1 lamemp3enc:in_jackaudiosrc0_1
#jack_connect    jack_rack:out_1 lamemp3enc:in_jackaudiosrc0_1

#jack_connect jack_rack:out_1  system:playback_1
#jack_connect jack_rack:out_1  system:playback_2

# STEREO setup
#jack_connect jack_rack:out_1  lamemp3enc:in_1
#jack_connect jack_rack:out_2  lamemp3enc:in_2
#jack_connect jack_rack:out_1  system:playback_1
#jack_connect jack_rack:out_2  system:playback_2

 # 4 channels setup
 #jack_connect system:capture_1 jack_rack:in_1
 #jack_connect system:capture_1 jack_rack:in_2
 #jack_connect system:capture_2 jack_rack:in_1
 #jack_connect system:capture_2 jack_rack:in_2
 #jack_connect system:capture_3 jack_rack:in_1
 #jack_connect system:capture_4 jack_rack:in_2

# ---------------------
# Video channel
# ---------------------

/usr/local/share/telecaster/scripts/tc_video_simple_webm_stream.sh &

sleep 2

jack_disconnect system:capture_1 gst-launch-0.10-01:in_jackaudiosrc0_1
jack_disconnect system:capture_2 gst-launch-0.10-01:in_jackaudiosrc0_2

jack_connect jack_rack:out_1 gst-launch-0.10-01:in_jackaudiosrc0_1
jack_connect jack_rack:out_2 gst-launch-0.10-01:in_jackaudiosrc0_2
