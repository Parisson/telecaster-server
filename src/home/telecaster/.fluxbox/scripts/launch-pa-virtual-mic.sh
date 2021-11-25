#!/bin/bash

# https://unix.stackexchange.com/questions/576785/redirecting-pulseaudio-sink-to-a-virtual-source

pactl load-module module-null-sink sink_name=mix-for-virtual-mic \
sink_properties=device.description=Mix-for-Virtual-Microphone

pactl load-module module-null-sink sink_name=silence \
sink_properties=device.description=silent-sink-for-echo-cancel

pactl load-module module-echo-cancel \
sink_name=virtual-microphone source_name=virtual-microphone \
source_master=mix-for-virtual-mic.monitor sink_master=silence aec_method=null \
source_properties=device.description=Virtual-Microphone \
sink_properties=device.description=Virtual-Microphone

