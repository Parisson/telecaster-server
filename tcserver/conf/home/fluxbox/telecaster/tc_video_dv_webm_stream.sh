#!/bin/sh

# Start TeleCaster video channel

#WIDTH=640
#HEIGHT=360
#WIDTH=1024
#HEIGHT=576
WIDTH=480
HEIGHT=320

gst-launch dv1394src ! dvdemux ! queue ! dvdec ! queue ! deinterlace \
	! queue ! videoscale ! video/x-raw-yuv, width=$WIDTH, height=$HEIGHT \
	! queue ! ffmpegcolorspace \
        ! queue ! vp8enc speed=2 threads=2 quality=10.0 max-latency=25 max-keyframe-distance=96 \
        ! queue ! muxout. \
	jackaudiosrc connect=1 ! audio/x-raw-float, channels=2 \
	! queue ! audioconvert ! queue ! vorbisenc quality=0.6 ! queue ! muxout.  \
	webmmux streamable=true name=muxout \
	! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none blocksize=65536 sync-method=1 


