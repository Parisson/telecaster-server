#!/bin/sh

# Start TeleCaster video channel

WIDTH=432
HEIGHT=240

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! theoraenc bitrate=400 speed-level=0 ! queue ! muxout. \
	jackaudiosrc connect=1 \
	! queue ! audioconvert ! queue ! vorbisenc ! queue ! muxout.  \
	oggmux name=muxout ! filesink location=/home/telecaster/archives/test.ogg \
	> /dev/null &

sleep 2

jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect 	jack_rack:out_1  gst-launch-0.10:in_jackaudiosrc0_1

