#!/bin/sh

gst-launch tcpclientsrc host=127.0.0.1 port=9000 \
  ! ffdec_h264 ! xvimagesink 
 
