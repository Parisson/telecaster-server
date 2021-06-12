#!/bin/sh

gst-launch-1.0 jackaudiosrc connect=1 ! audio/x-raw, format=F32LE, channels=1 \
	! queue ! audioconvert \
	! queue ! audiocheblimit mode=high-pass cutoff=120 poles=4 \
	! queue ! audiodynamic characteristics=soft-knee mode=compressor threshold=0.25 ratio=4.0 \
	! queue ! audioconvert ! queue ! lamemp3enc quality=4.0 \
	! queue ! shout2send ip=127.0.0.1 port=8000 password=source2parisson mount=telecaster_live.mp3
	> /dev/null

