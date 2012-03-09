#!/bin/sh

# Start TeleCaster video channel

/home/telecaster/.fluxbox/telecaster/tc_video_simple_webm_stream.sh > /dev/null &

sleep 3

jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect    jack_rack:out_1  gst-launch-0.10:in_jackaudiosrc0_1

deefuzzer /etc/telecaster/deefuzzer_video_safe.xml > /dev/null & 
