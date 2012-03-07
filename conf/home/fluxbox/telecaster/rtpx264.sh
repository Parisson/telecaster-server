#!/bin/sh

gst-launch -v  gstrtpbin name=rtpbin \
 v4l2src ! video/x-raw-yuv,width=640,height=480 \
 ! queue ! x264enc byte-stream=true bitrate=500 bframes=4 ref=4 me=hex subme=4 weightb=true threads=4 ! rtph264pay \
 ! rtpbin.send_rtp_sink_0 \
 rtpbin.send_rtp_src_0 ! udpsink port=5000 host=127.0.0.1 \
 rtpbin.send_rtcp_src_0 ! udpsink port=5001 host=127.0.0.1 sync=false async=false  \
 udpsrc port=5002 ! rtpbin.recv_rtcp_sink_0 
 