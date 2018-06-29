
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
from threading import Thread
import sys
import liblo

class OSCController(Thread):

    def __init__(self, port):
        Thread.__init__(self)
        import liblo
        self.port = port
        try:
            self.server = liblo.Server(self.port)
        except liblo.ServerError, err:
            print str(err)

    def run(self):
        while True:
            self.server.recv(100)

            
class AudioPlayer(Thread):
    
    def __init__(self, uri):
        Thread.__init__(self)
        self.uri = uri
        self.controller = OSCController(12345)
        self.controller.server.add_method('/play', 'i', self.play_stop_cb)
        self.controller.start()
        
        self.mainloop = gobject.MainLoop()
        self.player = gst.element_factory_make("playbin", "player")
        self.player.set_property('uri', self.uri)
        
    def play_stop_cb(self, path, value):
        value = value[0]
        if value:
            print 'play'
            self.player.set_state(gst.STATE_NULL)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            print 'stop'
            self.player.set_state(gst.STATE_NULL)
            
    def run(self):
        self.mainloop.run()
    
if __name__ == '__main__':
    path = sys.argv[-1]
    player = AudioPlayer(path)
    player.start()
    
