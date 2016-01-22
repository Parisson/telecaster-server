#!/usr/bin/python
import gobject; gobject.threads_init()
import pygst; pygst.require("0.10")
import gst

p = gst.parse_launch ("""videomixer name=mix0 ! ffmpegcolorspace ! xvimagesink
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix0.sink_3
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix0.sink_2
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix0.sink_1
      videotestsrc ! video/x-raw-yuv, framerate=24/1, width=640, height=360 ! mix0.sink_0
""")

m1 = p.get_by_name("mix0")

s1_1 = m1.get_pad("sink_1")
c1_1 = gst.Controller(s1_1, "xpos", "ypos", "alpha")
c1_1.set("xpos", 0, 0)
c1_1.set("ypos", 0, 0)
c1_1.set("alpha", 0, 1.0)

s1_2 = m1.get_pad("sink_2")
c1_2 = gst.Controller(s1_2, "xpos", "ypos", "alpha")
c1_2.set("xpos", 0, 200)
c1_2.set("ypos", 0, 200)
c1_2.set("alpha", 0, 1.0)

s1_3 = m1.get_pad("sink_3")
c1_3 = gst.Controller(s1_3, "xpos", "ypos", "alpha")
c1_3.set("xpos", 0, 400)
c1_3.set("ypos", 0, 0)
c1_3.set("alpha", 0, 1.0)

p.set_state(gst.STATE_PLAYING)

gobject.MainLoop().run()
