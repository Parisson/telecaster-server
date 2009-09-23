#!/usr/bin/python
# *-* coding: utf-8 *-*
"""
   telecaster

   Copyright (c) 2006-2008 Guillaume Pellerin <yomguy@parisson.org>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

version = '0.3.5'
# Only for Unix and Linux systems

import os
import cgi
import cgitb
import shutil
import datetime
import time
import codecs
import string
import signal
import unicodedata
from tools import *
from webview import *
from station import *
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, TIT2, TP1, TAL, TDA, TCO, COM
cgitb.enable()


class TeleCaster:
    """Manage the calls of Station and Webview to get the network and
    disk streams"""

    def __init__(self, conf_file, school_file):
        """Main function"""
        self.conf_file = conf_file
        self.school_file = school_file
        conf_t = xml2dict(self.conf_file)
        self.conf = conf_t['telecaster']
        self.title = self.conf['infos']['name']
        self.root_dir = self.conf['server']['root_dir']
        self.lock_file = self.root_dir + os.sep + self.conf['server']['lock_file']
        self.title = self.conf['infos']['name']
        self.uid = os.getuid()
        self.url = self.conf['infos']['url']

    def main(self):
        odd_pid = get_pid('^oddcastv3\ -n', self.uid)
        rip_pid = get_pid('streamripper ', self.uid)
        writing = False
        casting = False
        writing = rip_pid != []
        casting = odd_pid != []        
        form = WebView(self.school_file, self.url, version)
        
        if odd_pid == [] and form.has_key("action") and \
            form.has_key("department") and form.has_key("conference") and \
            form.has_key("professor") and form.has_key("comment") and \
            form["action"].value == "start":
            
            self.conference_dict = {'title': self.title,
                        'department': form.getfirst("department"),
                        'conference': form.getfirst("conference"),
                        'session': form.getfirst("session"),
                        'professor': form.getfirst("professor"),
                        'comment': form.getfirst("comment")}
            
            s = Station(self.conf_file, self.conference_dict, self.lock_file)
            s.start()
            time.sleep(1)
            #w.stop_form(self.conference_dict, writing, casting)
            self.main()
            
        elif odd_pid != [] and os.path.exists(self.lock_file) and not form.has_key("action"):
            self.conference_dict = get_conference_from_lock(self.lock_file)
            form.stop_form(self.conference_dict, writing, casting)

        elif odd_pid != [] and form.has_key("action") and form["action"].value == "stop":
            if os.path.exists(self.lock_file):
                self.conference_dict = get_conference_from_lock(self.lock_file)
            s = Station(self.conf_file, self.conference_dict, self.lock_file)
            s.stop()
            time.sleep(1)
            self.main()

        elif odd_pid == []:
            form.start_form()


# Call main function.
conf_file = 'etc/telecaster_mp3.xml'
school_file = 'etc/pre-barreau_conferences.xml'

if __name__ == '__main__':
    t = TeleCaster(conf_file, school_file)
    t.main()

