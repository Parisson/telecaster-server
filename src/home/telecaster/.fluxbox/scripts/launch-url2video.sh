#!/bin/bash

URL=https://e-learning.crfpa.pre-barreau.com/media/Pre-Barreau/CRFPA/2021/Libertes_-_Cours/3cf774cb990d9987/crfpa-libertes-cours-09_16_21-09:45:47.mp4

VIDEO_SINK_NAME="/dev/video12"
AUDIO_SINK_NAME="Mix-for-Virtual-Microphone"

gst-launch-1.0 uridecodebin uri="$URL" name=uridec do-timestamp=true live=true \
      ! videoconvert \
      ! v4l2sink device=$VIDEO_SINK_NAME sync=true \
      uridec. \
      ! audioconvert \
      ! pulsesink device=$AUDIO_SINK_NAME sync=true
