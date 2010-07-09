#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Guillaume Pellerin (2006-2010)

# <yomguy@parisson.com>

# This software is a computer program whose purpose is to stream audio
# and video data through icecast2 servers.

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

# ONLY FOR GNU/LINUX Debian

import os, sys
import platform

install_dir = '/var/www/telecaster'
if not os.path.exists(install_dir):
    os.mkdir(install_dir)

os.system('cp -ra ./* ' + install_dir + os.sep)

conf_dir = '/etc'
if not os.path.exists(conf_dir):
    os.mkdir(conf_dir)
os.system('chown -R  root:root ./conf/etc/')
os.system('cp -ra ./conf/etc/* ' + conf_dir + os.sep)


init_dir = '/etc/rc2.d'
init_link = init_dir + os.sep + 'S97jackd'
if not os.path.exists(init_link):
    os.system('ln -s /etc/init.d/jackd ' + init_link)

init_link = init_dir + os.sep + 'S99vncserver'
if not os.path.exists(init_link):
    os.system('ln -s /etc/init.d/vncserver ' + init_link)
    
user = raw_input('Give a user to use the TeleCaster system : ')
os.system('chown -R ' + user + ':' + user + ' ' + install_dir) 
home = os.sep + 'home' + os.sep + user + os.sep
home_dirs = ['fluxbox', 'vnc']

for dir in home_dirs:
    home_dir = home + '.' + dir
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    os.system('cp ' + conf_dir + os.sep + 'telecaster/home/' + dir + '/* ' + home_dir)
    os.system('chown -R ' + user + ':' + user + ' ' + home_dir) 

#var_dir = '/var/www/telecaster'
#if not os.path.exists(var_dir):
#    os.system('ln -s ' + install_dir + ' ' + var_dir)

print """
   Installation successfull !
   Now configure your apache VirtualHost to get TeleCaster in your browser.
   Please see conf/etc/apache2/default and README for more infos.
   """

