#!/bin/sh

# Start TeleCaster video channel

gst-launch ximagesrc ! video/x-raw-rgb,framerate=30/1 \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=2 quality=9.0 ! queue ! muxout. \
	jackaudiosrc connect=1 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! filesink location=/home/momo/tmp/desktop.webm
	

