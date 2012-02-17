#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=360
#WIDTH=1024
#HEIGHT=576

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! videoflip method=rotate-180 \
	! queue ! ffmpegcolorspace \
	! queue ! vp8enc speed=2 threads=2 quality=5 ! queue ! muxout. \
	jackaudiosrc connect=1 \
	! queue ! audioconvert ! queue ! vorbisenc quality=3 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! tee name=t ! queue ! multifdsink name=sink sync=false recover-policy=3 \
	t. ! queue ! filesink location=/home/telecaster/trash/test.webm \
	> /dev/null &

sleep 2

jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect 	jack_rack:out_1  gst-launch-0.10:in_jackaudiosrc0_1

