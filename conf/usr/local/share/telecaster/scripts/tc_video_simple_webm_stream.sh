#!/bin/sh

# Start TeleCaster video channel

#WIDTH=640
#HEIGHT=360
WIDTH=864
HEIGHT=480
#WIDTH=1280
#HEIGHT=720

v4l2-ctl -d 0 -c power_line_frequency=1 -c zoom_absolute=140

gst-launch v4l2src device=/dev/video0 ! video/x-raw-rgb, width=$WIDTH, height=$HEIGHT, framerate={30/1}  \
        ! queue ! videoflip method=rotate-180 \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=4 quality=10.0 max-latency=25 max-keyframe-distance=30 auto-alt-ref-frames=true  ! queue ! muxout. \
	jackaudiosrc connect=2 ! audio/x-raw-float, channels=2 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.4 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! tcpserversink host=127.0.0.1 port=9000 protocol=none blocksize=65536 sync-method=1 \
	> /dev/null
