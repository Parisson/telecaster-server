#!/usr/bin/env python

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class GTK_Main:

	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title("Vorbis-Player")
		window.set_default_size(500, 200)
		window.connect("destroy", gtk.main_quit, "WM destroy")
		vbox = gtk.VBox()
		window.add(vbox)
		self.entry = gtk.Entry()
		vbox.pack_start(self.entry, False)
		self.button = gtk.Button("Start")
		vbox.add(self.button)
		self.button.connect("clicked", self.start_stop)
		window.show_all()

		self.player = gst.Pipeline("player")
		source = gst.element_factory_make("filesrc", "file-source")
		demuxer = gst.element_factory_make("oggdemux", "demuxer")
		demuxer.connect("pad-added", self.demuxer_callback)
		self.audio_decoder = gst.element_factory_make("vorbisdec", "vorbis-decoder")
		audioconv = gst.element_factory_make("audioconvert", "converter")
		audiosink = gst.element_factory_make("autoaudiosink", "audio-output")

		self.player.add(source, demuxer, self.audio_decoder, audioconv, audiosink)
		gst.element_link_many(source, demuxer)
		gst.element_link_many(self.audio_decoder, audioconv, audiosink)

		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)

	def start_stop(self, w):
		if self.button.get_label() == "Start":
			filepath = self.entry.get_text()
			if os.path.isfile(filepath):
				self.button.set_label("Stop")
				self.player.get_by_name("file-source").set_property("location", filepath)
				self.player.set_state(gst.STATE_PLAYING)
		else:
			self.player.set_state(gst.STATE_NULL)
			self.button.set_label("Start")

	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			self.button.set_label("Start")
		elif t == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.player.set_state(gst.STATE_NULL)
			self.button.set_label("Start")

	def demuxer_callback(self, demuxer, pad):
		adec_pad = self.audio_decoder.get_pad("sink")
		pad.link(adec_pad)

GTK_Main()
gtk.gdk.threads_init()
gtk.main()