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
from optparse import OptionParser


def cleanup(path):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if '.svn' in dir or '.git' in dir:
                shutil.rmtree(root + os.sep + dir)

class Install(object):

    def __init__(self, options):
        self.options = options
        self.app_dir = os.getcwd()
        self.user = 'telecaster'
        self.home = '/home/' + self.user
        self.app_dir = os.path.dirname(__file__)

        self.rss_dir = '/var/www/rss'
        self.m3u_dir = '/var/www/m3u'
        self.log_dir = '/var/log/telecaster'
        self.deefuzzer_log_dir = '/var/log/deefuzzer'
        self.conf_dir = '/etc/telecaster'
        self.stream_m_conf_dir = '/etc/stream-m'
        self.init_dirs = ['/etc/init.d/', '/etc/default/']
        self.daemons = ['jackd', 'telecaster', 'stream-m']
        self.apache_conf = '/etc/apache2/sites-available/telecaster.conf'

    def create_user(self):
        if not os.path.exists(self.home):
            print 'Please give some informations for the new "telecaster" user :'
            os.system('adduser ' + self.user)
            os.system('adduser ' + self.user + ' audio')

    def chown(self, dir):
        os.system('chown -R ' + self.user + ':' + self.user + ' ' + dir)

    def install_deps(self):
        # compiling edcast-jack
        os.chdir(self.app_dir + '/lib/edcast-jack')
        os.system('./configure; make; make install')

        # Install Stream-m
        os.chdir(self.app_dir)
        os.system('cp -ra lib/stream-m /usr/local/lib/')
        init_link = '/usr/local/bin/stream-m'
        if not os.path.islink(init_link):
            os.system('ln -s /usr/local/lib/stream-m/bin/stream-m '+init_link)

    def install_conf(self):
        os.chdir(self.app_dir)

        for conf_dir in [self.conf_dir, self.stream_m_conf_dir]:
            in_files = os.listdir('conf'+conf_dir)
            if not os.path.exists(conf_dir):
                os.makedirs(conf_dir)
            for file in in_files:
                shutil.copy('conf'+conf_dir+os.sep+file, conf_dir+os.sep+file)
            self.chown(conf_dir)

        for dir in os.listdir('conf/home'):
            home_dir = self.home + '/.' + dir
            if not os.path.exists(home_dir):
                os.makedirs(home_dir)
            os.system('cp -r conf/home/'+dir + '/* ' + home_dir)
            self.chown(home_dir)

        shutil.copy('conf'+self.apache_conf, self.apache_conf)
        os.system('a2ensite telecaster.conf')
        os.system('/etc/init.d/apache2 reload')

        dir = '/etc/pm/'
        os.system('cp -r conf' + dir + '* ' + dir)

    def install_init(self):
        os.chdir(self.app_dir)

        dirs = [self.rss_dir, self.m3u_dir, self.log_dir, self.deefuzzer_log_dir, self.conf_dir,  self.stream_m_conf_dir]
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
            self.chown(dir)

        for init_dir in self.init_dirs:
            for daemon in self.daemons:
                path = init_dir + daemon
                shutil.copy('conf'+path, path)
                os.system('sudo chmod 755 '+path)

        init_link = '/etc/rc2.d/S97jackd'
        if not os.path.islink(init_link):
            os.system('ln -s /etc/init.d/jackd '+init_link)

        init_link = '/etc/rc2.d/S99telecaster'
        if not os.path.islink(init_link):
            os.system('ln -s /etc/init.d/telecaster '+init_link)

        init_link = '/etc/rc2.d/S98stream-m'
        if not os.path.islink(init_link):
            os.system('ln -s /etc/init.d/stream-m '+init_link)

        os.system('cp -r conf/usr/* /usr/')

    def run(self):
        if self.options['keepinit'] == False:
            print 'Installing init files...'
            self.install_init()
        if self.options['keepmods'] == False:
            print 'Installing dependencies...'
            self.install_deps()
        if self.options['keepconf'] == False:
            print 'Installing config files...'
            self.install_conf()

        print 'Please now user telecaster-client to control your streams...'



def run():
    parser = OptionParser()
    parser.add_option("-c", "--keepconf", dest="keepconf", default=False, action="store_true",
                      help="do NOT overwrite config files")
    parser.add_option("-i", "--keepinit", dest="keepinit", default=False, action="store_true",
                      help="do NOT overwrite init files")
    parser.add_option("-m", "--keepmods", dest="keepmods", default=False, action="store_true",
                      help="do NOT overwrite or install modules")

    (options, args) = parser.parse_args()
    install = Install(vars(options))
    install.run()

    print """
       Installation successfull !

       Now, please :
        - configure your telecaster editing:
            /etc/telecaster/telecaster.xml
            /etc/telecaster/deefuzzer.xml

        - configure your apache VirtualHost editing /etc/apache2/sites-available/telecaster.conf

        - tune your audio and video servers and REBOOT!

        See README for more infos.
       """
