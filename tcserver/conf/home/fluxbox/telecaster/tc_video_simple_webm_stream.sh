#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=360
#WIDTH=1280
#HEIGHT=720

v4l2-ctl -d 1 -c power_line_frequency=1

gst-launch v4l2src device=/dev/video1 ! video/x-raw-rgb, width=$WIDTH, height=$HEIGHT, framerate={24/1}  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=4 quality=10.0 max-latency=25 max-keyframe-distance=96 auto-alt-ref-frames=true  ! queue ! muxout. \
	jackaudiosrc connect=2 client-name=webmenc ! audio/x-raw-float, channels=2 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none blocksize=65536 sync-method=1 \
	> /dev/null

