#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=480

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT, framerate={30/1}  \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=4 quality=7.0 max-latency=2 max-keyframe-distance=3 auto-alt-ref-frames=true  ! queue ! muxout. \
	jackaudiosrc connect=2 client-name=webmenc ! audio/x-raw-float, channels=2 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none blocksize=65536 sync-method=1

