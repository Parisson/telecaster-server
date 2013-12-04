#!/bin/sh

gst-launch -v gstrtpbin name=rtpbin latency=200 \
 udpsrc caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" port=5000 \
 ! rtpbin.recv_rtp_sink_0 \
 rtpbin. ! rtph264depay ! tee name=t ! ffdec_h264 ! xvimagesink \
 udpsrc port=5001 ! rtpbin.recv_rtcp_sink_0 \
 rtpbin.send_rtcp_src_0 ! udpsink port=5002 host=127.0.0.1 sync=false async=false \
 t. ! filesink location=/tmp/video.mp4 
