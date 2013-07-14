#!/bin/sh

# Start TeleCaster video channel

telecaster/tc_video_simple_webm_stream.sh > /dev/null &

sleep 3

jack_disconnect system:capture_1 webmenc:in_jackaudiosrc0_1
jack_connect    jack_rack:out_1  webmenc:in_jackaudiosrc0_1

deefuzzer /etc/telecaster/deefuzzer_video_safe.xml > /dev/null &
