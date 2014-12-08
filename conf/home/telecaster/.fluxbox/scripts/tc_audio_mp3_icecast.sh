#!/bin/sh

gst-launch jackaudiosrc connect=1 ! audio/x-raw-float, channels=1 \
	! queue ! audioconvert ! queue ! lamemp3enc quality=4.0 \
	! queue ! shout2send ip=127.0.0.1 port=8000 password=source2parisson mount=telecaster_live.mp3
	> /dev/null
