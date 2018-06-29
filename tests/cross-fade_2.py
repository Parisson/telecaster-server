#!/usr/bin/python
import gobject; gobject.threads_init()
import pygst; pygst.require("0.10")
import gst

p = gst.parse_launch ("""videomixer name=mix ! ffmpegcolorspace ! xvimagesink
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=10/1, width=200, height=150 ! mix.sink_0
      videotestsrc ! video/x-raw-yuv, framerate=10/1, width=640, height=360 ! mix.sink_1
""")

m = p.get_by_name ("mix")
s0 = m.get_pad ("sink_0")
s0.set_property ("xpos", 100)

control = gst.Controller(s0, "ypos", "alpha")
control.set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
control.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
control.set("ypos", 0, 0); control.set("ypos", 5 * gst.SECOND, 200)
control.set("alpha", 0, 0); control.set("alpha", 5 * gst.SECOND, 1.0)

p.set_state (gst.STATE_PLAYING)

gobject.MainLoop().run()