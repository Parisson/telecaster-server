from PyQt4 import QtCore, QtGui
import pygst
import sys, os, time, math
pygst.require("0.10")
import gst
import gobject

#This class runs the code it contains in another thread using QThread
class Player(QtCore.QThread):
     def __init__(self):
          QtCore.QThread.__init__(self)

     def run(self):
          #create the pipeline
          player = gst.Pipeline("player")
          #filesrc element
          source = gst.element_factory_make("filesrc", "file-source")
          #volume element to adjust volume of audio
          volume = gst.element_factory_make("volume", "volume")
          #level element to get the rms/peak property
          level = gst.element_factory_make("level", "volume-level")
          #decoder to play mp3 files
          decoder = gst.element_factory_make("mad", "mp3-decoder")
          #convert the audio to play to speakers
          conv = gst.element_factory_make("audioconvert", "converter")
          #autosink if not alsa
          sink = gst.element_factory_make("autoaudiosink", "audio-output")

          #add the elements to the pipeline
          player.add(source, volume, level, decoder, conv, sink)

          #link the elements in order
          gst.element_link_many(source, decoder, conv, volume, level, sink)
          #set properties of elements
          player.get_by_name("volume").set_property('volume', 1)
          player.get_by_name("volume-level").set_property('peak-ttl' , 0)
          player.get_by_name("volume-level").set_property('peak-falloff', 20)
          #add bus to listen signal from
          bus = gst.Pipeline.get_bus(player)
          gst.Bus.add_signal_watch(bus)

          #the source of the player
          filepath = "/home/momo/music_local/test/aboul.wav.mp3"
          #set the property of the element filesrc
          player.get_by_name("file-source").set_property('location', filepath)
          #play the file
          player.set_state(gst.STATE_PLAYING)
          #get the current thread in Qt
          play_thread_id = self.currentThread

          #set the minimum decibels
          MIN_DB = -45
          #set the maximum decibels
          MAX_DB = 0
          #if current thread is running
          while play_thread_id == self.currentThread:
               #listen to messages that emit during playing
               messagePoll = bus.poll(gst.MESSAGE_ANY,-1)
               #if the message is level
               if messagePoll.src == level:
                    #get the structure of the message
                    struc = messagePoll.structure
               #if the structure message is rms
               if struc.has_key('rms'):
                    rms = struc["rms"]
                    #get the values of rms in a list
                    rms0 = abs(float(rms[0]))
                    #compute for rms to decibels
                    rmsdb = 10 * math.log(rms0 / 32768 )
                    #compute for progress bar
                    vlrms = (rmsdb-MIN_DB) * 100 / (MAX_DB-MIN_DB)
                    #emit the signal to the qt progress bar
                    self.emit(QtCore.SIGNAL("setLabel"), abs(vlrms))
               #set timer
               time.sleep(0.05)

#this code produced using pyuic from qt designer
class Ui_Dialog(object):
     def setupUi(self, Dialog):
          Dialog.setObjectName("Dialog")
          Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,94,300).size()).expandedTo(Dialog.minimumSizeHint()))

          self.progressBar = QtGui.QProgressBar(Dialog)
          self.progressBar.setGeometry(QtCore.QRect(10,10,31,281))
          self.progressBar.setProperty("value",QtCore.QVariant(24))
          self.progressBar.setOrientation(QtCore.Qt.Vertical)
          self.progressBar.setObjectName("progressBar")
          self.progressBar.setValue(0)
          self.progressBar.setMinimum(0)
          self.progressBar.setMaximum(100)

          self.retranslateUi(Dialog)
          QtCore.QMetaObject.connectSlotsByName(Dialog)
          #sets the value of the progress bar emited
     def setLabel(self,value):
          self.progressBar.setValue(value)

     def retranslateUi(self, Dialog):
          Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
     app = QtGui.QApplication(sys.argv)
     window = QtGui.QDialog()
     ui = Ui_Dialog()
     ui.setupUi(window)
     window.show()
     #creates instance of the Player class
     player=Player()
     #connect to signal emitted in Player class
     QtCore.QObject.connect(player, QtCore.SIGNAL("setLabel"), ui.setLabel, QtCore.Qt.QueuedConnection)
     #run the Player class thread
     player.start()
     app.exec_()
