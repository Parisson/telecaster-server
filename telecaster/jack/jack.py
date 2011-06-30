#!/usr/bin/python
# Capture 3 seconds of stereo audio from alsa_pcm:capture_1/2; then play it back.
#
# Copyright 2003, Andrew W. Schmeder
# This source code is released under the terms of the GNU Public License.
# See LICENSE for the full text of these terms.

import Numeric
import jack
import time

class JackInput:
    "A JACK connexion input in TeleOddCast"

    def __init__(self, dict):
        self.host = dict['host']
        self.name = dict['name']
        self.jack = jack()
        self.buffer_size = self.jack.get_buffer_size()
        self.sample_rate = float(self.jack.get_sample_rate())
        print "Buffer Size:", N, "Sample Rate:", Sr
        self.power = True
        self.capture = Numeric.zeros((2, self.buffer_size), 'f')
        
        
    def attach(self):
        jack.attach(self.name)

    def get_ports(self):
        return self.jack.get_ports()

    def register_ports(self):
        self.jack.register_port("in_1", self.jack.IsInput)
        self.jack.register_port("in_2", self.jack.IsInput)

    def activate(self):
        self.jack.activate()

    def stop(self):
        self.power = False

    def connect(self):
        self.jack.connect("alsa_pcm:capture_1", self.name+":in_1")
        self.jack.connect("alsa_pcm:capture_2", self.name+":in_2")
        #jack.connect(self.name+":out_1", "alsa_pcm:playback_1")
        #jack.connect(self.name+":out_2", "alsa_pcm:playback_2")

    def process(self):
        while True:
            try:
                if not self.power:
                    break
                self.jack.process(__chunk, capture[:,self.buffer_size])
                yield __chunk
            except self.jack.InputSyncError:
                print "Input Sync"
                pass
            except self.jack.OutputSyncError:
                print "Output Sync"
                pass

    def desactivate(self):           
        self.jack.deactivate()

    def detach(self):
        self.jack.detach()
