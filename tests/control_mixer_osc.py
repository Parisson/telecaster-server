#!/usr/bin/python
import gobject; gobject.threads_init()
import pygst; pygst.require("0.10")
import gst
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

    def add_method(self, path, type, method):
        self.server.add_method(path, type, method)

    def run(self):
        while True:
            self.server.recv(100)


class GSTSrcVideo(object):

    def __init__(self, pipe=None, framerate='24/1', width=160, height=90, xpos=0, ypos=0):
        self.framerate = framerate
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        if not pipe:
            pipe = 'videotestsrc pattern="snow"'
        self.pipe = pipe + ' ! video/x-raw-yuv, framerate=%s, width=%s, height=%s' \
                        % (self.framerate, str(self.width), str(self.height))

class GSTMixer(object):

    def __init__(self, osc_port=13000):
        self.name = 'mixer'
        self.pipe = ['videomixer name=mixer ! ffmpegcolorspace ! xvimagesink']
        self.srcs = []
        self.i= 0

        self.osc_port = osc_port
        self.osc = OSCController(self.osc_port)

    def osc_callback(self, path, value):
        paths = path.split('/')
        sink = paths[1]
        param = paths[2]
        for src in self.srcs:
            if src['sink'] == sink:
                break
        src['control'].set(param, 5 * gst.SECOND, value[0])

    def add_src(self, src):
        self.srcs.append({'id': self.i, 'src': src, 'sink': 'sink_' + str(self.i)})
        self.i += 1

    def setup(self):
        self.srcs.reverse()

        for src in self.srcs:
            self.pipe.append(' '.join([src['src'].pipe, '! ' + self.name + '.' + src['sink']]))

        print ' '.join(self.pipe)
        self.process = gst.parse_launch(' '.join(self.pipe))
        mixer = self.process.get_by_name("mixer")

        for src in self.srcs:
            src['pad'] = mixer.get_pad(src['sink'])
            src['control'] = gst.Controller(src['pad'], "xpos", "ypos", "alpha")

            src['control'].set_interpolation_mode("xpos", gst.INTERPOLATE_LINEAR)
            src['control'].set("xpos", 5 * gst.SECOND, src['src'].xpos)
            self.osc.add_method('/'+src['sink']+'/xpos', 'i', self.osc_callback)

            src['control'].set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
            src['control'].set("ypos", 5 * gst.SECOND, src['src'].ypos)
            self.osc.add_method('/'+src['sink']+'/ypos', 'i', self.osc_callback)

            src['control'].set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
            src['control'].set("alpha", 5 * gst.SECOND, 1.0)
            self.osc.add_method('/'+src['sink']+'/alpha', 'f', self.osc_callback)


    def run(self):
        self.osc.start()
        self.process.set_state(gst.STATE_PLAYING)
        gobject.MainLoop().run()


if __name__ == '__main__':
    src1 = GSTSrcVideo(width=640, height=360, framerate='24/1', pipe='videotestsrc')
    src2 = GSTSrcVideo(width=160, height=90, framerate='24/1', xpos=100, ypos=50)
    src3 = GSTSrcVideo(width=160, height=90, framerate='24/1', xpos=200, ypos=150)
    src4 = GSTSrcVideo(width=160, height=90, framerate='24/1', xpos=300, ypos=250)
    mixer = GSTMixer()
    mixer.add_src(src1)
    mixer.add_src(src2)
    mixer.add_src(src3)
    mixer.add_src(src4)
    mixer.setup()
    mixer.run()
