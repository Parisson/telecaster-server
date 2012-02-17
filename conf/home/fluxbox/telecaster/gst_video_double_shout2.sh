#!/bin/sh

# Start TeleCaster video channel

WIDTH=480
HEIGHT=270

gst-launch v4l2src device=/dev/video0 ! queue ! videoscale ! video/x-raw-yuv, width=160, height=120 \
	! queue ! videorate ! video/x-raw-yuv,framerate=25/1 \
	! queue ! videomixer name=mix sink_1::xpos=0 sink_1::ypos=0 sink_1::alpha=0.9 \
	! queue ! ffmpegcolorspace ! queue ! theoraenc quality=25 ! muxout. \
	jackaudiosrc connect=1 ! audioconvert ! audio/x-raw-int,rate=44100,channels=1,width=16 \
	! queue ! audioconvert ! vorbisenc ! queue ! muxout.  \
	oggmux name=muxout ! queue ! shout2send mount=/telecaster_live_video.ogg port=8000 password=source2parisson ip=127.0.0.1 \
	v4l2src device=/dev/video1 ! queue ! videoscale ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT \
	! queue ! videorate ! video/x-raw-yuv,framerate=25/1 ! mix. \
	> /dev/null &
		
sleep 2

jack_disconnect system:capture_1 gst-launch-0.10:in_jackaudiosrc0_1
jack_connect 	jack_rack:out_1  gst-launch-0.10:in_jackaudiosrc0_1

