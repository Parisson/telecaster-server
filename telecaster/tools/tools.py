#!/usr/bin/python
# -*- coding: utf-8 -*-
# *-* coding: utf-8 *-*
"""
   teleoddcast

   Copyright (c) 2006-2007 Guillaume Pellerin <yomguy@altern.org>

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
"""

import os
import cgi
import shutil
import datetime
import string
import time
from xmltodict import *
import socket
import fcntl
import struct
import acpi
import subprocess
import pwd

class SubProcessPipe:
    def __init__(self, command, stdin=None):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        self.buffer_size = 0xFFFF

        if not stdin:
            stdin =  subprocess.PIPE

        self.proc = subprocess.Popen(command.encode('utf-8'),
                    shell = True,
                    bufsize = self.buffer_size,
                    stdin = stdin,
                    stdout = subprocess.PIPE,
                    close_fds = True)

        self.input = self.proc.stdin
        self.output = self.proc.stdout

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_hostname():
    return socket.gethostname()

def get_lines(file):
    """Get lines from a file"""
    fic = open(file,'r')
    lines = fic.readlines()
    fic.close()
    return lines

def clean_string(string):
    """removes blank spaces and accents"""
    string = string.replace(' ','_')
    #string = string.replace('é','e')
    #string = string.replace('è','e')
    return string

def xml2dict(conf_file):
    confile = open(conf_file,'r')
    conf_xml = confile.read()
    confile.close()
    dict = xmltodict(conf_xml,'utf-8')
    return dict

def get_pid(proc,uid):
    """Get a process pid filtered by arguments and uid"""
    command = 'pgrep -fl -U '+str(uid)+' '+'"'+proc+'"'
    proc = SubProcessPipe(command)
    list = proc.output
    procs = list.readlines()
    pids = []
    if procs != '':
        for proc in procs:
            pid = proc.split(' ')[0]
            command = ' '.join(proc.split(' ')[1:])[:-1]
            pids.append(pid)
    if len(pids) <= 1:
        return []
    else:
        return [pids[0]]

def get_params_from_lock(lock_file):
    lockfile = open(lock_file,'r')
    params = lockfile.readline()
    params_ok = params.split('_*_')
    lockfile.close()
    return params_ok

def dict2tuple(dict):
    len_dict = len(dict['conference'])
    if len_dict == 1:
        return dict['conference']['name']
    else:
        tup = []
        for value in dict['conference']:
            tup.append(value['name'])
        return tup

def dict2tuple_iso(dict):
    len_dict = len(dict['conference'])
    if len_dict == 1:
        return unicode(dict['conference']['name'],'utf8').encode('iso-8859-1')
    else:
        tup = []
        for value in dict['conference']:
            tup.append(unicode(value['name'],'utf8').encode('iso-8859-1'))
        return tup

def get_conference_from_lock(lock_file):
    lockfile = open(lock_file,'r')
    conference = lockfile.readline()
    conference_l = conference.split('_*_')
    conference_dict = {'title': conference_l[0],
                   'department': conference_l[1],
                   'conference': conference_l[2],
                   'session': conference_l[3],
                   'professor': conference_l[4],
                   'comment': conference_l[5]}
    lockfile.close()
    return conference_dict

def str_to_bool(string):
    return string == 'true'

def norm_string(string):
    pass


class Status(object):

    interfaces = ['eth0', 'eth1', 'eth2', 'eth0-eth2', 'eth3', 'wlan0', 'wlan1']
    acpi_states = {0: 'battery', 1: 'battery', 2: 'AC'}

    def __init__(self):
        self.acpi = acpi.Acpi()
        self.uid = os.getuid()
        self.user = pwd.getpwuid(os.getuid())[0]
        self.user_dir = '/home' + os.sep + self.user + os.sep + '.telecaster'

    def update(self):
        self.acpi.update()
        try:
            self.temperature = self.acpi.temperature(0)
        except:
            self.temperature = 'N/A'
        self.get_ids()
        self.get_hosts()

    def to_dict(self):
        status = [
          {'id': 'acpi_state','class': 'default', 'value': self.acpi_states[self.acpi.charging_state()], 'label': 'Power'},
          {'id': 'acpi_percent', 'class': 'default', 'value': str(self.acpi.percent()), 'label': 'Battery Charge'},
          {'id': 'temperature', 'class': 'default', 'value': self.temperature, 'label': 'Temperature'},
          {'id': 'jack_state', 'class': 'default', 'value': self.jacking, 'label': 'Jack server'},
          {'id': 'name', 'class': 'default', 'value': self.name, 'label': 'Name'},
          {'id': 'ip', 'class': 'default', 'value': self.ip, 'label': 'IP address'},
          {'id': 'encoder_state','class': 'default', 'value': self.writing, 'label': 'Encoder'},
          {'id': 'casting', 'class': 'default', 'value': self.casting, 'label': 'Broadcasting'},
          {'id': 'writing', 'class': 'default', 'value': self.writing, 'label': 'Recording'},
          ]

        for stat in status:
            if stat['value'] == False or stat['value'] == 'localhost' or stat['value'] == 'battery':
                stat['class'] = 'warning'

        return status

    def get_hosts(self):
        ip = ''
        for interface in self.interfaces:
            try:
                ip = get_ip_address(interface)
                if ip:
                    self.ip = ip
                break
            except:
                self.ip = '127.0.0.1'
        self.url = 'http://' + self.ip
        self.name = get_hostname()

    def get_ids(self):
        edcast_pid = get_pid('edcast_jack', self.uid)
        deefuzzer_pid = get_pid('/usr/bin/deefuzzer '+self.user_dir+os.sep+'deefuzzer.xml', self.uid)
        jackd_pid = get_pid('jackd', self.uid)
        if jackd_pid == []:
            jackd_pid = get_pid('jackdbus', self.uid)
        self.writing = edcast_pid != []
        self.casting = deefuzzer_pid != []
        self.jacking = jackd_pid != []
