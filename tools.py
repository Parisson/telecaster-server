#!/usr/bin/python
# *-* coding: utf-8 *-*
"""
   teleoddcast

   Copyright (c) 2006-2007 Guillaume Pellerin <yomguy@altern.org>

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

import os
import cgi
import shutil
import datetime
import string
import time
from xmltodict import *
from mutagen.oggvorbis import OggVorbis

def get_lines(file):
	"""Get lines from a file"""
	fic = open(file,'r')
	lines = fic.readlines()
	fic.close()
	return lines

def clean_string(string):
	"""removes blank spaces and accents"""
	string = string.replace(' ','_')
	string = string.replace('é','e')
	string = string.replace('è','e')
	return string

def xml2dict(conf_file):
    confile = open(conf_file,'r')
    conf_xml = confile.read()
    confile.close()
    dict = xmltodict(conf_xml,'utf-8')
    return dict

def get_pid(proc,uid):
    """Get a process pid filtered by arguments and uid"""
    (list1, list2) = os.popen4('pgrep -f -U '+str(uid)+' '+'"'+proc+'"')
    pids = list2.readlines()
    if pids != '':
        for pid in pids:
            index = pids.index(pid)
            pids[index] = pid[:-1]
    return pids

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

