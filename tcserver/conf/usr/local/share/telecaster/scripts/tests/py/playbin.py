import pygst 
pygst.require("0.10") 
import gst 

#pipeline = gst.Pipeline() 
playbin = gst.element_factory_make("playbin2", 'player') 
#sink = gst.element_factory_make("autoaudiosink", None) 

playbin.set_property("uri", "/home/momo/music_local/test/sweep.wav")
#playbin.set_property("uri", "/home/momo/video_local/webm/ocean-clip.webm")
#playbin.set_property("audio-sink", sink)

#pipeline.add(playbin) 

import time 
playbin.set_state(gst.STATE_PLAYING) 
time.sleep(200) 
