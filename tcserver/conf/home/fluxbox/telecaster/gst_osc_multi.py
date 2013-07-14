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

    def __init__(self, pipe=None, mime_type='video/x-raw-yuv', framerate='24/1',
                 width=160, height=90, xpos=0, ypos=0):
        self.mime_type = mime_type
        self.framerate = framerate
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        if not pipe:
            pipe = 'videotestsrc pattern="snow"'
        self.pipe = pipe + ' ! %s, framerate=%s, width=%s, height=%s' \
                        % (self.mime_type, self.framerate, str(self.width), str(self.height))


class GSTSrcAudio(object):

    def __init__(self, pipe=None, mime_type='audio/x-raw-float', channels=2):
        self.mime_type = mime_type
        self.channels = channels
        if not pipe:
            pipe = 'jackaudiosrc connect=2'
        self.pipe = pipe + ' ! %s, channels=%s' % (self.mime_type, str(self.channels))


class V4lControl(object):

    def __init__(self, device=0):
        self.program = 'v4l2-ctl'
        self.device = device

    def execute(self, args):
        command = ' '.join([self.program, '-d', self.device, '-c', args])
        os.system(command)

    def power_line_frequency(self, value):
          arg = 'power_line_frequency=' + value
          self.execute(arg)


class GSTWebmStreamer(object):

    def __init__(self, host='127.0.0.1', port=9000, blocksize=65536):
        self.host = host
        self.port = port
        self.blocksize = blocksize
        self.muxer = """webmmux streamable=true name=muxer \
                    ! queue ! tcpserversink host=%s port=%s protocol=none blocksize=%s sync-method=1
                    """ % (self.host, str(self.port), str(self.blocksize))

    def video_setup(self, threads=4, quality=10):
        self.video = """! queue ! ffmpegcolorspace ! queue ! vp8enc speed=2 threads=%s quality=%s \
                        max-latency=25 max-keyframe-distance=96 auto-alt-ref-frames=true  \
                        ! queue ! muxer.""" % (str(threads), str(quality))

    def audio_setup(self, quality=0.3):
        self.audio = "! queue ! audioconvert ! queue ! vorbisenc quality=%s ! queue ! muxer." % str(self.quality)

    @property
    def pipe(self):
        return ' '.join([self.video, self.audio, self.muxer])


class GSTMixer(object):

    def __init__(self, osc_port=8338):
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

    def osc_alpha_callback(self, path, value):
        paths = path.split('/')
        layer = paths[1]
        param = paths[2]
        id = int(param[-1])-1
        for src in self.srcs:
            if src['id'] == id:
                break
        src['control'].set('alpha', 5 * gst.SECOND, value[0])

    def osc_xy_callback(self, path, value):
        for src in self.srcs:
            if src['id'] == 2:
                break
        src['control'].set("xpos", 5 * gst.SECOND, int(value[0]*480))
        src['control'].set("ypos", 5 * gst.SECOND, int(value[1]*270))

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

            src['control'].set_interpolation_mode("ypos", gst.INTERPOLATE_LINEAR)
            src['control'].set("ypos", 5 * gst.SECOND, src['src'].ypos)

            src['control'].set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
            src['control'].set("alpha", 5 * gst.SECOND, 1.0)

            self.osc.add_method('/1/fader'+str(src['id']+1), 'f', self.osc_alpha_callback)

        self.osc.add_method('/3/xy', 'ff', self.osc_xy_callback)

    def run(self):
        self.osc.start()
        self.process.set_state(gst.STATE_PLAYING)
        gobject.MainLoop().run()


if __name__ == '__main__':
    src1 = GSTSrcVideo(width=640, height=360, framerate='24/1', pipe='videotestsrc pattern="black" ')
    src2 = GSTSrcVideo(width=640, height=360, framerate='24/1', pipe='videotestsrc ')
    src3 = GSTSrcVideo(width=160, height=90, framerate='24/1', xpos=200, ypos=150)
    src4 = GSTSrcVideo(width=160, height=90, framerate='24/1', xpos=300, ypos=250)
    mixer = GSTMixer()
    mixer.add_src(src1)
    mixer.add_src(src2)
    mixer.add_src(src3)
    mixer.add_src(src4)
    mixer.setup()
    mixer.run()
