#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=480
#WIDTH=1024
#HEIGHT=576

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=4 quality=5.0 ! queue ! muxout. \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none 

