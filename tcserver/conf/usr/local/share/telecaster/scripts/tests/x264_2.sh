#!/bin/sh

gst-launch v4l2src ! video/x-raw-yuv,width=640,height=480 \
 ! queue ! x264enc byte-stream=true bitrate=500 bframes=4 ref=4 me=hex subme=4 weightb=true threads=4 \
 ! tcpserversink host=127.0.0.1 port=9000 protocol=none
