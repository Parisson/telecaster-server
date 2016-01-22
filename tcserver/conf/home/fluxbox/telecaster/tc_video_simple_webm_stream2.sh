#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=360
#WIDTH=1280
#HEIGHT=720

gst-launch v4l2src device=/dev/video2 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=4 quality=8.0 ! queue ! muxout. \
	jackaudiosrc connect=1 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9001 protocol=none \
	> /dev/null 

