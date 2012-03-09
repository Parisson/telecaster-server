#!/bin/sh

gst-launch tcpclientsrc host=192.168.0.18 port=9000 \
    ! matroskademux \
    ! queue ! vp8dec \
    ! queue ! ffmpegcolorspace \
    ! queue ! x264enc bitrate=200 bframes=4 ref=4 me=hex subme=4 weightb=true threads=0 ! muxout. \
	mp4mux name=muxout \
	! queue ! filesink location=/tmp/video.mp4

# tcpclientsrc host=192.168.0.18 port=9000 protocol=none \
