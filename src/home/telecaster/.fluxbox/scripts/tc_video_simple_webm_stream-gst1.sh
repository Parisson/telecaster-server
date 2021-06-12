#!/bin/sh

# Start TeleCaster video channel

#WIDTH=640
#HEIGHT=360
WIDTH=864
HEIGHT=480
#WIDTH=1280
#HEIGHT=720
FRAMERATE=24

v4l2-ctl -d 0 -c power_line_frequency=1
v4l2-ctl -d 0 -c zoom_absolute=100
v4l2-ctl -d 0 -c focus_auto=0
v4l2-ctl -d 0 -c focus_absolute=1

# ! queue ! videoflip method=rotate-180 \

gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-raw, format=YUY2, width=$WIDTH, height=$HEIGHT, framerate=$FRAMERATE/1  \
	! queue ! videoconvert \
	! queue ! vp8enc threads=4 deadline=2 ! queue ! muxout. \
	jackaudiosrc connect=1 ! audio/x-raw, format=F32LE, channels=1 \
	! queue ! audioconvert \
	! queue ! audiocheblimit mode=high-pass cutoff=120 poles=4 \
	! queue ! audiodynamic characteristics=soft-knee mode=compressor threshold=0.16 ratio=0.15 \
        ! queue ! rgvolume pre-amp=6.0 headroom=1.0 \
	! queue ! rglimiter \
	! queue ! vorbisenc quality=0.4 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 blocksize=65536 sync-method=1 \
	> /dev/null
