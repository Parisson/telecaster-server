#!/bin/sh

# Start TeleCaster video channel

#WIDTH=640
#HEIGHT=360
WIDTH=1280
HEIGHT=720

gst-launch v4l2src device=/dev/video1 ! video/x-raw-rgb, width=$WIDTH, height=$HEIGHT  \
	! queue ! ffmpegcolorspace ! ximagesink 

