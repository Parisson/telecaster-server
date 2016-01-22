#!/bin/sh

# Start TeleCaster video channel

WIDTH_1=1280
HEIGHT_1=720

WIDTH_2=640
HEIGHT_2=360


gst-launch v4l2src device=/dev/video1 ! video/x-raw-yuv, width=$WIDTH_2, height=$HEIGHT_2  \
        ! queue ! videomixer name=mix sink_1::xpos=$WIDTH_2 sink_1::ypos=$HEIGHT_2 sink_1::alpha=0.9 \
        ! queue ! ffmpegcolorspace \
        ! queue ! vp8enc speed=2 threads=4 quality=9.0 ! queue ! muxout. \
        jackaudiosrc connect=1 \
        ! queue ! audioconvert ! queue ! vorbisenc quality=0.3 ! queue ! muxout.  \
        webmmux streamable=true name=muxout \
        ! queue ! tcpserversink host=127.0.0.1 port=9000 protocol=none \
        v4l2src device=/dev/video0 ! video/x-raw-yuv, width=$WIDTH_1, height=$HEIGHT_1 \
        ! queue ! mix. \
        > /dev/null 
        