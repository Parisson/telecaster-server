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
import shutil

def remove_svn(path):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if '.svn' in dir:
                shutil.rmtree(root + os.sep + dir)

app_dir = os.getcwd()

user = 'telecaster' 
home = '/home/' + user
if not os.path.exists(home):
    print 'Please give some informations for the new "telecaster" user :'
    os.system('adduser ' + user)

# compiling edcast-jack
os.chdir(app_dir + '/tools/edcast-jack')
os.system('make; sudo make install')

# installing deefuzzer
os.chdir(app_dir + '/tools/deefuzzer')
os.system('sudo python install.py')

os.chdir(app_dir)
install_dir = '/var/www/telecaster'
if os.path.exists(install_dir):
    shutil.rmtree(install_dir)
shutil.copytree(app_dir, install_dir,ignore=shutil.ignore_patterns('edcast-jack*', 'deefuzzer*', '*.svn*'))
os.system('chown -R ' + user + ':' + user + ' ' + install_dir)

conf_dir = '/etc/telecaster'
if not os.path.exists(conf_dir):
    shutil.copytree('conf'+conf_dir, conf_dir, ignore=shutil.ignore_patterns('*.svn*'))

daemons = ['jackd', 'vncserver']
init_dir = '/etc/init.d/'
conf_dir = '/etc/default/'
for daemon in daemons:
    shutil.copy('conf'+init_dir+daemon, init_dir)
    shutil.copy('conf'+conf_dir+daemon, conf_dir)
    
init_link = '/etc/rc2.d/S97jackd'
if not os.path.islink(init_link):
    os.symlink('/etc/init.d/jackd ', init_link)

init_link = '/etc/rc2.d/S99vncserver'
if not os.path.islink(init_link):
    os.symlink('/etc/init.d/vncserver ', init_link)

home_dirs = ['fluxbox', 'vnc']
for dir in home_dirs:
    home_dir = home + '/.' + dir
    if not os.path.exists(home_dir):
        shutil.copytree('conf/home/'+dir, home_dir, ignore=shutil.ignore_patterns('*.svn*'))
        os.system('chown -R ' + user + ':' + user + ' ' + home_dir) 

apache_conf = '/etc/apache2/sites-available/telecaster.conf'
if not os.path.exists(apache_conf):
    shutil.copy('conf'+apache_conf, apache_conf)
os.system('/etc/init.d/apache2 reload')

log_dir = '/var/log/telecaster'
os.mkdir(log_dir)
os.system('chown -R ' + user + ':' + user + ' ' + log_dir) 

print """
   Installation successfull !
   
   Now, please :
   - configure your telecaster editing /etc/telecaster/telecaster.xml
   - configure your apache VirtualHost editing /etc/apache2/sites-available/telecaster.conf 

   And use the TeleCaster system browsing http://localhost/telecaster/telecaster.py
   
   See README for more infos.
   """

