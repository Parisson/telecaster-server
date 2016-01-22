#!/bin/sh

# Start TeleCaster video channel

WIDTH=1280
HEIGHT=720

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=1 quality=9.0 ! queue ! muxout. \
	alsasrc \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none

	

