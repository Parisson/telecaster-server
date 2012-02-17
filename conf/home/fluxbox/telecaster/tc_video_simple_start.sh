#!/bin/sh

# Start TeleCaster video channel

WIDTH=432
HEIGHT=240

gst-launch v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace \
	! queue ! theoraenc quality=10 ! queue ! muxout. \
	jackaudiosrc connect=1 \
	! queue ! audioconvert ! queue ! vorbisenc quality=3 ! queue ! muxout.  \
	oggmux name=muxout ! shout2send mount=/telecaster_live_video.ogg port=8000 password=source2parisson ip=127.0.0.1 \
	> /dev/null &

sleep 2

jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect 	jack_rack:out_1  gst-launch-0.10:in_jackaudiosrc0_1

