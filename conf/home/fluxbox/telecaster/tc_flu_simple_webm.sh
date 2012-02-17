#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=360
#WIDTH=1024
#HEIGHT=576


pipe="v4l2src device=/dev/video0  \
	! vp8-encoder ! muxout. \
	jackaudiosrc ! vorbis-encoder ! muxout.  \
	webmmux streamable=true name=muxout"

flumotion-launch pipeline-producer pipeline=$pipe ! http-streamer port=8800 

sleep 2

jack_disconnect system:capture_1 flumotion-launch:in_jackaudiosrc0_1
jack_connect 	jack_rack:out_1  flumotion-launch:in_jackaudiosrc0_1

