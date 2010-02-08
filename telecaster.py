#!/usr/bin/python
# -*- coding: utf-8 -*-
# *-* coding: utf-8 *-*
"""
   telecaster

   Copyright (c) 2006-2008 Guillaume Pellerin <yomguy@parisson.org>

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

# Author: Guillaume Pellerin <yomguy@parisson.com>

version = '0.3.7'
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
        odd_pid = get_pid('^edcast_jack\ -n', self.uid)
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

