#!/bin/sh

# Start TeleCaster video channel

#WIDTH=640
#HEIGHT=360
WIDTH=864
HEIGHT=480
#WIDTH=1280
#HEIGHT=720

# gst-launch-1.0 tcpclientsrc host=$1 port=$2  \
#     	! gdpdepay ! rtph264depay ! avdec_h264 \
#     	! videoconvert \
#         ! queue ! vp8enc threads=4 ! queue ! muxout. \
#         jackaudiosrc connect=2 ! audio/x-raw, format=F32LE, channels=2 \
#         ! audioconvert ! audioresample ! audio/x-raw, rate=48000 ! vorbisenc quality=0.3 ! queue ! muxout.  \
#         webmmux streamable=true name=muxout \
#         ! tcpserversink host=127.0.0.1 port=10001


# gst-launch-1.0 tcpclientsrc host=$1 port=$2  \
#     	! queue ! gdpdepay ! rtph264depay ! avdec_h264 \
#         ! vp8enc threads=4 target-bitrate=1000000 auto-alt-ref=true \
#         ! webmmux streamable=true name=muxout \
#         ! tcpserversink host=127.0.0.1 port=10001


gst-launch-0.10 tcpclientsrc host=$1 port=$2  \
    	! queue ! gdpdepay ! rtph264depay ! ffdec_h264 \
        ! queue ! vp8enc speed=2 threads=4 quality=5.0 \
        ! queue ! webmmux streamable=true name=muxout \
        ! tcpserversink host=127.0.0.1 port=10001 sync-method=1


