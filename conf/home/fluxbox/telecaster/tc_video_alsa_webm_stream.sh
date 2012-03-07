#!/bin/sh

# Start TeleCaster video channel

WIDTH=320
HEIGHT=240
#WIDTH=1024
#HEIGHT=576

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=2 quality=9.0 ! queue ! muxout. \
	alsasrc device=hw:0 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none \
	> /dev/null 

