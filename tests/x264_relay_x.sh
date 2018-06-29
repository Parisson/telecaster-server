#!/bin/sh

gst-launch tcpclientsrc host=192.168.0.18 port=9000 \
    ! matroskademux \
    ! vp8dec ! ffmpegcolorspace \
    ! queue ! x264enc \
    ! queue ! vdpauh264dec ! ffmpegcolorspace ! ximagesink

# tcpclientsrc host=192.168.0.18 port=9000 protocol=none \