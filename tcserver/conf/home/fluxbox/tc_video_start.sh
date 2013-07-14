#!/bin/sh

# Start TeleCaster video channel

/usr/local/share/telecaster/scripts/telecaster/tc_video_simple_webm_stream.sh &

sleep 3

jack_disconnect system:capture_1 webmenc:in_jackaudiosrc0_1
jack_connect    jack_rack:out_1  webmenc:in_jackaudiosrc0_1

deefuzzer /etc/telecaster/telecaster_webm_monitor.yaml > /dev/null &
