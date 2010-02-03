#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import os
import shutil
import datetime
import time
import codecs
import string
import signal
import jack
import unicodedata
from tools import *
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, TIT2, TP1, TAL, TDA, TCO, COM

class Conference:
    """A conference object including metadata"""

    def __init__(self, dict):
        self.dict = dict
        self.title = dict['title']
        self.department = dict['department']
        self.conference = dict['conference']
        self.session = dict['session']
        self.professor = dict['professor']
        self.comment = dict['comment']

    def get_info(self):
        return self.title, self.department, self.conference, self.session, self.professor, self.comment


class Station(Conference):
    """Control the Oddcastv3-jack thread which send audio data to the icecast server
    and the Streamripper thread which write audio on the hard disk"""

    def __init__(self, conf_file, conference_dict, lock_file):
        Conference.__init__(self, conference_dict)
        self.date = datetime.datetime.now().strftime("%Y")
        self.time = datetime.datetime.now().strftime("%x-%X")
        self.time_txt = self.time.replace('/','_').replace(':','_').replace(' ','_')
        self.conf = xml2dict(conf_file)
        self.conf = self.conf['telecaster']
        self.root_dir = self.conf['server']['root_dir']
        self.url_ext = self.conf['infos']['url']
        self.media_dir = self.conf['media']['dir']
        self.host = self.conf['server']['host']
        self.port = self.conf['server']['port']
        self.rss_dir = self.conf['server']['rss']['dir']
        self.rss_file = 'telecaster.xml'
        self.password = self.conf['server']['sourcepassword']
        self.url_int = 'http://'+self.host+':'+self.port
        self.odd_conf_file = self.conf['server']['odd_conf_file']
        self.bitrate = self.conf['media']['bitrate']
        self.dict['Bitrate'] = str(self.bitrate) + ' kbps'
        self.ogg_quality = self.conf['media']['ogg_quality']
        self.format = self.conf['media']['format']
        self.channels = int(self.conf['media']['channels'])
        self.description = [self.title, self.department, self.conference, self.session, self.professor, self.comment]
        self.server_name = [self.title, self.department, self.conference]
        self.ServerDescription = clean_string('_-_'.join(self.description))
        self.ServerName = clean_string('_-_'.join(self.server_name))
        self.mount_point = '/' + clean_string(self.title) + '_-_' + \
                                 clean_string(self.department) + '_-_' + \
                                 clean_string(self.conference)+'.'+self.format
        self.lock_file = self.root_dir + os.sep + self.conf['server']['lock_file']
        self.filename = clean_string('_-_'.join(self.description[1:])) + '_-_' + self.time_txt + '.' + self.format
        self.output_dir = self.media_dir + os.sep + self.department + os.sep + self.date
        self.file_dir = self.output_dir + os.sep + self.ServerName
        self.uid = os.getuid()
        self.odd_pid = get_pid('^oddcastv3\ -n', self.uid)
        self.rip_pid = get_pid('streamripper ' + self.url_int + self.mount_point, self.uid)
        self.new_title = clean_string('_-_'.join(self.server_name)+'_-_'+self.session+'_-_'+self.professor+'_-_'+self.comment)
        self.short_title = clean_string('_-_'.join(self.conference)+'_-_'+self.session+'_-_'+self.professor+'_-_'+self.comment)
        self.genre = 'Vocal'
        self.encoder = 'TeleCaster by Parisson'
        self.rsync_host = self.conf['server']['rsync_host']
        self.record = str_to_bool(self.conf['media']['record'])
        self.raw_dir = self.conf['media']['raw_dir']
        if not os.path.exists(self.media_dir):
            os.makedirs(self.media_dir)
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)

        self.jack_inputs = []
        if 'jack' in self.conf:
            for jack_input in self.conf['jack']['input']:
                self.jack_inputs.append(jack_input['name'])

    def set_oddcast_conf(self):
        #oddconf_temp = NamedTemporaryFile(suffix='.cfg')
        oddconf = open(self.odd_conf_file,'r')
        lines = oddconf.readlines()
        oddconf.close()
        newlines = []
        for line in lines:
            if 'ServerDescription' in line.split('='):
                newlines.append('ServerDescription=' + \
                                self.ServerDescription.replace(' ','_') + '\n')

            elif 'ServerName' in line.split('='):
                newlines.append('ServerName=' + self.ServerName + '\n')

            elif 'ServerMountpoint' in line.split('='):
                newlines.append('ServerMountpoint=' + self.mount_point + '\n')

            elif 'ServerPassword' in line.split('='):
                newlines.append('ServerPassword=' + self.password + '\n')

            elif 'SaveDirectory' in line.split('='):
                newlines.append('SaveDirectory=' + self.raw_dir + '\n')
            elif 'NumberChannels' in line.split('='):
                newlines.append('NumberChannels=' + str(len(self.jack_inputs)) + '\n')
            elif 'BitrateNominal' in line.split('='):
                newlines.append('BitrateNominal=' + str(self.bitrate) + '\n')
            elif 'OggQuality' in line.split('='):
                newlines.append('OggQuality=' + str(self.ogg_quality) + '\n')
            else:
                newlines.append(line)

        odd_conf_file = 'etc/'+self.title+'.cfg'
        oddconf = open(odd_conf_file,'w')
        oddconf.writelines(newlines)
        oddconf.close()
        self.odd_conf = odd_conf_file

    def start_oddcast(self):
        if not self.jack_inputs:
            jack.attach('telecaster')
            for jack_input in jack.get_ports():
                if 'system' in jack_input and 'capture' in jack_input.split(':')[1] :
                    self.jack_inputs.append(jack_input)
        jack_ports = ' '.join(self.jack_inputs)
        command = 'oddcastv3 -n "'+clean_string(self.conference)[0:16]+'" -c "'+self.odd_conf+ \
                  '" '+ jack_ports + ' > /dev/null &'
        os.system(command)
        self.set_lock()
        time.sleep(1)

    def set_lock(self):
        lock = open(self.lock_file,'w')
        lock_text = clean_string('_*_'.join(self.description))
        lock_text = lock_text.replace('\n','')
        lock.write(lock_text)
        lock.close()

    def del_lock(self):
        os.remove(self.lock_file)

    def start_rip(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        command = 'streamripper ' + self.url_int + self.mount_point + \
                  ' -d '+self.output_dir+' -D \"%S\" -s -t --quiet > /dev/null &'
        os.system(command)
        time.sleep(1)

    def stop_oddcast(self):
        if len(self.odd_pid) != 0:
            os.system('kill -9 '+self.odd_pid[0])

    def stop_rip(self):
        if len(self.rip_pid) != 0:
            os.system('kill -9 ' + self.rip_pid[0])
        time.sleep(1)
        date = datetime.datetime.now().strftime("%Y")
        if os.path.exists(self.file_dir) and os.path.exists(self.file_dir + os.sep + 'incomplete'):
            try:
                shutil.move(self.file_dir+os.sep+'incomplete'+os.sep+' - .'+self.format, self.file_dir+os.sep)
                os.rename(self.file_dir+os.sep+' - .'+self.format, self.file_dir+os.sep+self.filename)
                shutil.rmtree(self.file_dir+os.sep+'incomplete'+os.sep)
            except:
                pass

    def mp3_convert(self):
        os.system('oggdec -o - '+ self.file_dir+os.sep+self.filename+' | lame -S -m m -h -b '+ self.bitrate + \
            ' --add-id3v2 --tt "'+ self.new_title + '" --ta "'+self.professor+'" --tl "'+self.title+'" --ty "'+self.date+ \
        '" --tg "'+self.genre+'" - ' + self.file_dir+os.sep+self.ServerDescription + '.mp3 &')

    def write_tags_ogg(self):
       file = self.file_dir + os.sep + self.filename
       if os.path.exists(file):
            audio = OggVorbis(file)
            audio['TITLE'] = self.new_title
            audio['ARTIST'] = self.professor
            audio['ALBUM'] = self.title
            audio['DATE'] = self.date
            audio['GENRE'] = self.genre
            audio['SOURCE'] = self.title
            audio['ENCODER'] = self.encoder
            audio['COMMENT'] = self.comment
            audio.save()

    def write_tags_mp3(self):
        file = self.file_dir + os.sep + self.filename
        if os.path.exists(file):
            os.system('mp3info -t "a" -a "a" '+file)
            audio = ID3(file)
            #tag = tags.__dict__['TITLE']
            audio.add(TIT2(encoding=3, text=self.new_title))
            #tag = tags.__dict__['ARTIST']
            audio.add(TP1(encoding=3, text=self.professor))
            #tag = tags.__dict__['ALBUM']
            audio.add(TAL(encoding=3, text=self.title))
            #tag = tags.__dict__['DATE']
            audio.add(TDA(encoding=3, text=self.date))
            #tag = tags.__dict__['GENRE']
            audio.add(TCO(encoding=3, text=self.genre))
            #tag = tags.__dict__['COMMENT']
            #audio.add(COM(encoding=3, text=self.comment))
            audio.save()
        time.sleep(1)

    def start(self):
        self.set_lock()
        self.set_oddcast_conf()
        self.start_oddcast()
        self.start_rip()
        self.update_rss()

    def stop(self):
        self.stop_rip()
        self.stop_oddcast()
        if self.format == 'ogg':
            self.write_tags_ogg()
        elif self.format == 'mp3':
            self.write_tags_mp3()
        self.del_lock()
        #self.mp3_convert()
        #self.rsync_out()

    def start_mp3cast(self):
        item_id = item_id
        source = source
        metadata = metadata
        args = get_args(options)
        ext = get_file_extension()
        args = ' '.join(args)
        command = 'sox "%s" -q -w -r 44100 -t wav -c2 - | lame %s -' % (source, args)
        # Processing (streaming + cache writing)
        stream = self.core_process(self.command,self.buffer_size,self.dest)
        for chunk in stream:
            yield chunk

    def core_process(self, command, buffer_size, dest):
        """Encode and stream audio data through a generator"""
        __chunk = 0
        file_out = open(dest,'w')
        try:
            proc = subprocess.Popen(command,
                    shell = True,
                    bufsize = buffer_size,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    close_fds = True)
        except:
            raise ExportProcessError('Command failure:', command, proc)
        # Core processing
        while True:
            __chunk = proc.stdout.read(buffer_size)
            status = proc.poll()
            if status != None and status != 0:
                raise ExportProcessError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk
            file_out.write(__chunk)
        file_out.close()

    def rsync_out(self):
        local_uname = os.uname()
        hostname = local_uname[1]
        os.system('rsync -a '+self.media_dir+os.sep+' '+self.rsync_host+':'+os.sep+hostname+os.sep)

    def update_rss(self):
        rss_item_list = []
        if not os.path.exists(self.rss_dir):
            os.makedirs(self.rss_dir)

        time_now = datetime.datetime.now().strftime("%x-%X")

        media_description = '<table>'
        media_description_item = '<tr><td>%s:   </td><td><b>%s</b></td></tr>'
        for key in self.dict.keys():
            if self.dict[key] != '':
                media_description += media_description_item % (key.capitalize(), self.dict[key])
        media_description += '</table>'

        media_link = self.url_ext + '/rss/' + self.rss_file
        media_link = media_link.decode('utf-8')

        rss_item_list.append(RSSItem(
            title = self.ServerName,
            link = media_link,
            description = media_description,
            guid = Guid(media_link),
            pubDate = self.time_txt,)
            )

        rss = RSS2(title = self.title + ' - ' + self.department,
                            link = self.url_ext,
                            description = self.ServerDescription.decode('utf-8'),
                            lastBuildDate = str(time_now),
                            items = rss_item_list,)

        f = open(self.rss_dir + os.sep + self.rss_file, 'w')
        rss.write_xml(f, 'utf-8')
        f.close()
