#!/bin/bash

sudo modprobe v4l2loopback devices=1 video_nr=12 card_label="virtual webcam" exclusive_caps=1 max_buffers=2
