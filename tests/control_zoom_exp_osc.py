#!/usr/bin/python
import gobject; gobject.threads_init()
import pygst; pygst.require("0.10")
import os, gst
from threading import Thread


class OSCController(Thread):

    def __init__(self, port):
        Thread.__init__(self)
        import liblo
        self.port = port
        try:
            self.server = liblo.Server(self.port)
        except liblo.ServerError, err:
            print str(err)
        # self.server.add_method(None, None, self.fallback)

    def fallback(self, path, args, types, src):
        print "got unknown message '%s' from '%s'" % (path, src.get_url())
        for a, t in zip(args, types):
            print "argument of type '%s': %s" % (t, a)

    def add_method(self, path, type, method):
        self.server.add_method(path, type, method)

    def run(self):
        while True:
            self.server.recv(100)


class V4L2Controller(object):

    def __init__(self, video_id=0, osc_port=12345):
        self.osc_port = osc_port
        self.osc = OSCController(self.osc_port)
        self.video_id = video_id

        self.zoom_param = 'zoom_absolute'
        self.zoom_range = [100, 250]
        self.zoom_path = '/1/fader1'
        self.zoom_toggle = '/1/toggle1'
        self.osc.add_method(self.zoom_toggle, 'f', self.zoom_toggle_callback)
        self.osc.add_method(self.zoom_path, 'f', self.zoom_callback)
        self.zoom = False

        self.exposure_param = 'exposure_absolute'
        self.exposure_range = [0, 250]
        self.exposure_path = '/1/fader2'
        self.exposure_toggle = '/1/toggle2'
        self.osc.add_method(self.exposure_toggle, 'f', self.exposure_toggle_callback)
        self.osc.add_method(self.exposure_path, 'f', self.exposure_callback)
        self.exposure = False

    def set_param(self, param, value):
        command = 'v4l2-ctl -d ' + str(self.video_id) + ' -c ' + param + '=' + value
        print command
        os.system(command)

    def zoom_toggle_callback(self, path, args, types, src):
        for a, t in zip(args, types):
            value = a
        if not value:
            self.zoom = False
        else:
            self.zoom = True

    def zoom_callback(self, path, args, types, src):
        for a, t in zip(args, types):
            value = a
        if self.zoom:
            zoom_value = self.zoom_range[0] + (self.zoom_range[1] - self.zoom_range[0]) * value
            self.set_param(self.zoom_param, str(int(zoom_value)))

    def exposure_toggle_callback(self, path, args, types, src):
        for a, t in zip(args, types):
            value = a
        if not value:
            self.set_param('exposure_auto', str(3))
            self.exposure = False
        else:
            self.set_param('exposure_auto', str(1))
            self.exposure = True

    def exposure_callback(self, path, args, types, src):
        for a, t in zip(args, types):
            value = a
        if self.exposure:
            exposure_value = self.exposure_range[0] + (self.exposure_range[1] - self.exposure_range[0]) * value
            self.set_param(self.exposure_param, str(int(exposure_value)))

    def run(self):
        self.osc.start()


if __name__ == '__main__':
    controller = V4L2Controller(video_id=1)
    controller.run()

