#!/bin/sh

# ---------------------
# Audio channel
# ---------------------

qjackctl &

/home/telecaster/.fluxbox/scripts/tc_audio_mp3_icecast-gst1.sh &

/home/telecaster/.fluxbox/scripts/tc_video_simple_webm_stream-gst1.sh &

sleep 8

#Audio monitor
deefuzzer /etc/telecaster/deefuzzer/telecaster_mp3_monitor.yaml &

#Video monitor
deefuzzer /etc/telecaster/deefuzzer/telecaster_webm_monitor.yaml &

#sleep 3

#Wathdog for trash
#/home/telecaster/.fluxbox/scripts/monitor_check.py 10 /home/telecaster/trash/webm/ smtp.icp.fr informatique@icp.fr alerts@parisson.com &

