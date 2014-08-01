#!/bin/sh

# Start TeleCaster video channel

WIDTH=640
HEIGHT=360

gst-launch v4l2src device=/dev/video0 ! video/x-raw-rgb, width=$WIDTH, height=$HEIGHT  \
    ! queue ! ffmpegcolorspace \
    ! queue ! vp8enc speed=2 threads=2 quality=9.0 \
    ! webmmux streamable=true \
    ! shout2send mount=/telecaster_live_video.webm port=8000 password=source2parisson ip=127.0.0.1