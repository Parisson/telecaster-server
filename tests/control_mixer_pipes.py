#!/usr/bin/python
import gobject; gobject.threads_init()
import pygst; pygst.require("0.10")
import gst

p = gst.parse_launch ("""videomixer name=mix0 ! ffmpegcolorspace ! xvimagesink
      videotestsrc ! video/x-raw-yuv, framerate=24/1, width=640, height=360 ! mix0.sink_0
      videomixer name=mix1 ! mix0.sink_1
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix1.sink_0
      videomixer name=mix2 ! mix1.sink_1
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix2.sink_0
      videotestsrc pattern="snow" ! video/x-raw-yuv, framerate=24/1, width=200, height=150 ! mix2.sink_1
""")

m1 = p.get_by_name ("mix1")
s1_0 = m1.get_pad ("sink_0")
s1_0.set_property ("xpos", 100)
s1_1 = m1.get_pad ("sink_1")
s1_1.set_property ("xpos", 250)

m2 = p.get_by_name ("mix2")
s2_0 = m2.get_pad ("sink_0")
s2_0.set_property ("xpos", 200)
s2_1 = m2.get_pad ("sink_1")
s2_1.set_property ("xpos", 250)

c1_0 = gst.Controller(s1_0, "ypos", "alpha")
c1_0.set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
c1_0.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
c1_0.set("ypos", 0, 0)
c1_0.set("ypos", 5 * gst.SECOND, 200)
c1_0.set("alpha", 0, 0)
c1_0.set("alpha", 5 * gst.SECOND, 1.0)

c1_1 = gst.Controller(s1_1, "ypos", "alpha")
c1_1.set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
c1_1.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
c1_1.set("ypos", 0, 0)
c1_1.set("ypos", 5 * gst.SECOND, 200)
c1_1.set("alpha", 0, 0)
c1_1.set("alpha", 5 * gst.SECOND, 1.0)

c2_0 = gst.Controller(s2_0, "ypos", "alpha")
c2_0.set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
c2_0.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
c2_0.set("ypos", 0, 0)
c2_0.set("ypos", 5 * gst.SECOND, 200)
c2_0.set("alpha", 0, 0)
c2_0.set("alpha", 5 * gst.SECOND, 1.0)

c2_1 = gst.Controller(s2_1, "ypos", "alpha")
c2_1.set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
c2_1.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
c2_1.set("ypos", 0, 0)
c2_1.set("ypos", 5 * gst.SECOND, 200)
c2_1.set("alpha", 0, 0)
c2_1.set("alpha", 5 * gst.SECOND, 1.0)

p.set_state (gst.STATE_PLAYING)

gobject.MainLoop().run()
