#!/usr/bin/python
# *-* coding: utf-8 *-*
"""
   telecaster

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

version = '0.3.2'

import os
import cgi
import shutil
import datetime
import time
import codecs
import string
import signal
from tools import *
from mutagen.oggvorbis import OggVorbis


class Conference:
    """A conference object including metadata"""
    
    def __init__(self, dict):
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
        self.conf = xml2dict(conf_file)
        self.conf = self.conf['telecaster']
        self.root_dir = self.conf['server']['root_dir']
        self.media_dir = self.conf['media']['dir']
        self.host = self.conf['server']['host']
        self.port = self.conf['server']['port']
        self.password = self.conf['server']['sourcepassword']
        self.url = 'http://'+self.host+':'+self.port
        self.odd_conf_file = self.conf['server']['odd_conf_file']
        self.description = [self.title, self.department, self.conference, self.session, self.professor, self.comment]
        self.server_name = [self.title, self.department, self.conference]
        self.ServerDescription = clean_string('_-_'.join(self.description))
        self.ServerName = clean_string('_-_'.join(self.server_name))
        self.mount_point = '/' + clean_string(self.title) + '_-_' + \
                                 clean_string(self.department) + '_-_' + \
                                 clean_string(self.conference)+'.ogg'
        self.lock_file = self.root_dir + os.sep + self.conf['server']['lock_file']
        self.filename = self.ServerDescription + '.ogg'
        self.output_dir = self.media_dir + os.sep + self.department + os.sep + self.date
        self.file_dir = self.output_dir + os.sep + self.ServerName
        self.uid = os.getuid()
        self.odd_pid = get_pid('^oddcastv3 -n [^LIVE]', self.uid)
        self.rip_pid = get_pid('streamripper ' + self.url + self.mount_point, self.uid)
        self.bitrate = '64'
        self.new_title = clean_string('_-_'.join(self.server_name)+'_-_'+self.professor+'_-_'+self.comment)
        self.genre = 'Vocal'
        self.encoder = 'TeleCaster by Parisson'

    def set_oddcast_conf(self):
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
                
            else:
                newlines.append(line)
                
        oddconf = open(self.odd_conf_file,'w')
        oddconf.writelines(newlines)
        oddconf.close()

    def start_oddcast(self):
        command = 'oddcastv3 -n "'+clean_string(self.conference)[0:16]+'" -c '+self.odd_conf_file+ \
                  ' alsa_pcm:capture_1 alsa_pcm:capture_2 > /dev/null &'
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
        command = 'streamripper ' + self.url + self.mount_point + \
                  ' -d '+self.output_dir+' -D "%S" -s -t --quiet > /dev/null &'
        os.system(command)

    def stop_oddcast(self):
        if len(self.odd_pid) != 0:
            os.system('kill -9 '+self.odd_pid[0])
        
    def stop_rip(self):
        if len(self.rip_pid) != 0:
            os.system('kill -9 ' + self.rip_pid[0])
        time.sleep(1)
        date = datetime.datetime.now().strftime("%Y")
        if os.path.exists(self.file_dir) and os.path.exists(self.file_dir + os.sep + 'incomplete'):
            shutil.move(self.file_dir+os.sep+'incomplete'+os.sep+' - .ogg', self.file_dir+os.sep)
            shutil.rmtree(self.file_dir+os.sep+'incomplete'+os.sep)
            os.rename(self.file_dir+os.sep+' - .ogg', self.file_dir+os.sep+self.filename)

    def mp3_convert(self):
        os.system('oggdec -o - '+ self.file_dir+os.sep+self.filename+' | lame -S -m m -h -b '+ self.bitrate + \
	        ' --add-id3v2 --tt "'+ self.new_title + '" --ta "'+self.professor+'" --tl "'+self.title+'" --ty "'+self.date+ \
		'" --tg "'+self.genre+'" - ' + self.file_dir+os.sep+self.ServerDescription + '.mp3 &')
    
    def write_tags(self):
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

    def start(self):
        self.set_lock()
        self.set_oddcast_conf()
        self.start_oddcast()
        self.start_rip()

    def stop(self):
        self.stop_rip()
        self.write_tags()
        self.stop_oddcast()
        self.del_lock()
        self.encode_mp3()

    def encode_mp3(self):
        self.mp3_convert()

    def start_mp3cast(self):        
        item_id = item_id
        source = source
        metadata = metadata
        args = get_args(options)
        ext = get_file_extension()
        args = ' '.join(args)
        command = 'sox "%s" -q -w -r 44100 -t wav -c2 - | lame %s -' \
                       % (source, args)
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


class WebView:
    """Gives the web CGI frontend"""
    
    def __init__(self, school_file):
        self.conf = xml2dict(school_file)
        self.conf = self.conf['telecaster']
        self.url = self.conf['url']
        self.port = self.conf['port']
        self.title = self.conf['title']
        self.departments = self.conf['department']
        #print self.departments
        #self.conferences = self.conf['department']['conferences']
        self.len_departments = len(self.departments)
        self.conference_nb_max = 40

    def header(self):
        # Required header that tells the browser how to render the HTML.
        print "Content-Type: text/html\n"
        print "<HTML>"
        print "<HEAD>"
        print "<TITLE>TeleCaster - "+self.title+"</TITLE>"
        print "<link href=\"css/telecaster.css\" rel=\"stylesheet\" type=\"text/css\">"
        print '<script language="Javascript" type="text/javascript" >'
        print 'function choix(formulaire)'
        print '{var j; var i = formulaire.department.selectedIndex;'
        print 'if (i == 0)'
        print   'for(j = 1; j < '+ str(self.len_departments) + '; j++)'
        print      'formulaire.conference.options[j].text="";'
        print 'else{'
        print '   switch (i){'
        for k in range(0, self.len_departments):
            department = self.departments[k]
            conferences = department['conferences']
            #print conferences
            conferences_t = dict2tuple(conferences)
            #print conferences
            conferences = '"'+'","'.join(conferences_t)+'"'
            print '       case '+str(k+1)+' : var text = new Array('+conferences+'); '
            print '       break;'
        print '       }'
        print '      for(j = 0; j<'+str(self.conference_nb_max)+'; j++)'
        print '       formulaire.conference.options[j+1].text=text[j];'
        #print '       formulaire.conference.options[j+1].value=text[j];'
        print '}'
        print '      formulaire.conference.selectedIndex=0;}'
        print '</script>'
        print "</HEAD>"
        
        print "<BODY BGCOLOR =\"#FFFFFF\">"
        print "<div id=\"bg\">"
        print "<div id=\"header\">"
        print "<H3>&nbsp;TeleCaster - L'enregistrement et la diffusion audio en direct par internet</H3>"
        print "</div>"

    def colophon(self):
        date = datetime.datetime.now().strftime("%Y")
        print "<div id=\"colophon\">"
        print "TeleCaster "+version+" &copy; <span>"+date+"</span>&nbsp;<a href=\"http://parisson.com\">Parisson</a>. Tous droits r&eacute;serv&eacute;s."
        print "</div>"
            
    def footer(self):
        print "</div>"
        print "</BODY>"
        print "</HTML>"

    def start_form(self, message=''):
        self.header()
        print "<div id=\"main\">"
        print "<h5><span style=\"color: red\">"+message+"</span></h5>"
        print "<h5><span style=\"color: red\">Attention, il est important de remplir tous les champs, y compris le commentaire !</span></h5>"
        print "<TABLE BORDER = 0>"
        print "<form method=post action=\"telecaster.py\" name=\"formulaire\">"
        print "<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement :</TH>"
        print "<TD><select name=\"department\" onChange=\"choix(this.form)\">"
        print "<option selected>...........Choisissez un d&eacute;partement...........</option>"
        for department in self.departments:
            print "<option value=\""+department['name']+"\">"+department['name']+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Conf&eacute;rence :</TH>"
        print "<TD><select name=\"conference\">"
        print "<option selected>...........Choisissez une conf&eacute;rence...........</option>"
        for i in range(1,self.conference_nb_max):
            print "<option></option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Session :</TH><TD><select name=\"session\">"
        for i in range(1,21):
            print "<option value=\""+str(i)+"\">"+str(i)+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Professeur :</TH><TD><INPUT type = text name = \"professor\"></TD><TR>"
        print "<TR><TH align=\"left\">Commentaire :</TH><TD><INPUT type = text name = \"comment\"></TD></TR>"
        print "</TABLE>"
        print "<h5><a href=\""+self.url+":"+self.port+"/augustins.pre-barreau.com_live.ogg.m3u\">Cliquez ici pour &eacute;couter le flux continu 24/24 en direct</a></h5>"
        print "</div>"
        print "<div id=\"tools\">"
        print "<INPUT TYPE = hidden NAME = \"action\" VALUE = \"start\">"
        print "<INPUT TYPE = submit VALUE = \"Enregistrer\">"
        print "</FORM>"
        print "</div>"
        self.colophon()
        self.footer()

    def encode_form(self, message=''):
        self.header()
        print "<div id=\"main\">"
        print "<h5><span style=\"color: red\">"+message+"</span></h5>"
        print "<h5><span style=\"color: red\">ENCODAGE EN COURS !</span></h5>"
        print "</div>"
        self.colophon()
        self.footer()

    def stop_form(self, conference_dict):
        """Stop page"""
        department = conference_dict['department']
        conference = conference_dict['conference']
        session = conference_dict['session']
        professor = conference_dict['professor']
        comment = conference_dict['comment']

        self.header()
        print "<div id=\"main\">"
        print "<h4><span style=\"color: red\">Cette formation est en cours de diffusion :</span></h4>"
        print "<hr>"
        print "<TABLE BORDER = 0>"
        print "<FORM METHOD = post ACTION = \"telecaster.py\">"
        print "<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement :</TH><TD>"+department+"</TD><TR>"
        print "<TR><TH align=\"left\">Conference :</TH><TD>"+conference+"</TD><TR>"
        print "<TR><TH align=\"left\">Session :</TH><TD>"+session+"</TD><TR>"
        print "<TR><TH align=\"left\">Professeur :</TH><TD>"+professor+"</TD><TR>"
        print "<TR><TH align=\"left\">Commentaire :</TH><TD>"+comment+"</TD><TR>"
        print "</TABLE>"
        print "<hr>"
        print "<h5><a href=\""+self.url+":"+self.port+"/"+clean_string(self.title) + \
              "_-_"+clean_string(department)+"_-_"+clean_string(conference) + \
              ".ogg.m3u\">Cliquez ici pour &eacute;couter cette formation en direct</a></h5>"
        print "</div>"
        print "<div id=\"tools\">"
        print "<INPUT TYPE = hidden NAME = \"action\" VALUE = \"stop\">"
        print "<INPUT TYPE = submit VALUE = \"STOP\">"
        print "</FORM>"
        print "</div>"
        self.colophon()
        self.footer()


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
        self.odd_conf_file = self.conf['server']['lock_file']
        self.title = self.conf['infos']['name']
        self.uid = os.getuid()
        self.odd_pid = get_pid('^oddcastv3 -n [^LIVE]', self.uid)

    def main(self):
        w = WebView(self.school_file)
        form = cgi.FieldStorage()
        
        if self.odd_pid == [] and form.has_key("action") and \
            form.has_key("department") and form.has_key("conference") and \
            form.has_key("professor") and form.has_key("comment") and \
            form["action"].value == "start":
            
            self.conference_dict = {'title': self.title,
                        'department': form["department"].value,
                        'conference': form["conference"].value,
                        'session': form["session"].value,
                        'professor': form["professor"].value,
                        'comment': form["comment"].value}

            s = Station(self.conf_file, self.conference_dict, self.lock_file)
            s.start()
            w.stop_form(self.conference_dict)
            
        elif self.odd_pid != [] and os.path.exists(self.lock_file) and not form.has_key("action"):
            self.conference_dict = get_conference_from_lock(self.lock_file)
            w.stop_form(self.conference_dict)

        elif self.odd_pid != [] and form.has_key("action") and form["action"].value == "stop":
            if os.path.exists(self.lock_file):
                self.conference_dict = get_conference_from_lock(self.lock_file)
            s = Station(self.conf_file, self.conference_dict, self.lock_file)
            s.stop()
            #w.encode_form()
            #s.encode_mp3()
            #w.start_form('Please wait : encoding file to MP3...')
            w.start_form()

        elif self.odd_pid == []:
            w.start_form()


# Call main function.
conf_file = 'etc/telecaster.xml'
school_file = 'etc/pre-barreau_conferences.xml'

if __name__ == '__main__':
    t = TeleCaster(conf_file, school_file)
    t.main()

