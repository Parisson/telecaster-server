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
from tempfile import NamedTemporaryFile
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, TIT2, TP1, TAL, TDA, TCO, COM
cgitb.enable()

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
        self.time = datetime.datetime.now().strftime("%x-%X")
        self.time1 = self.time.replace('/','_')
        self.time2 = self.time1.replace(':','_')
       	self.time = self.time2.replace(' ','_')
        self.conf = xml2dict(conf_file)
        self.conf = self.conf['telecaster']
        self.root_dir = self.conf['server']['root_dir']
        self.media_dir = self.conf['media']['dir']
        self.host = self.conf['server']['host']
        self.port = self.conf['server']['port']
        self.password = self.conf['server']['sourcepassword']
        self.url = 'http://'+self.host+':'+self.port
        self.odd_conf_file = self.conf['server']['odd_conf_file']
        self.bitrate = '64'
        self.format = self.conf['media']['format']
        self.description = [self.title, self.department, self.conference, self.session, self.professor, self.comment]
        self.server_name = [self.title, self.department, self.conference]
        self.ServerDescription = clean_string('_-_'.join(self.description))
        self.ServerName = clean_string('_-_'.join(self.server_name))
        self.mount_point = '/' + clean_string(self.title) + '_-_' + \
                                 clean_string(self.department) + '_-_' + \
                                 clean_string(self.conference)+'.'+self.format
        self.lock_file = self.root_dir + os.sep + self.conf['server']['lock_file']
        self.filename = self.ServerDescription + '_-_' + self.time + '.' + self.format
        self.output_dir = self.media_dir + os.sep + self.department + os.sep + self.date
        self.file_dir = self.output_dir + os.sep + self.ServerName
        self.uid = os.getuid()
        self.odd_pid = get_pid('^oddcastv3 -n [^LIVE]', self.uid)
        self.rip_pid = get_pid('streamripper ' + self.url + self.mount_point, self.uid)
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

    def set_oddcast_conf(self):
        oddconf_temp = NamedTemporaryFile(suffix='.cfg')
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

            else:
                newlines.append(line)

        oddconf_temp_file = open(oddconf_temp.name,'w')
        oddconf_temp_file.writelines(newlines)
        self.odd_conf = oddconf_temp.name

    def start_oddcast(self):
        command = 'oddcastv3 -n "'+clean_string(self.conference)[0:16]+'" -c '+self.odd_conf+ \
                  ' alsa_pcm:capture_1 > /dev/null &'
        os.system(command)
        self.set_lock()
        time.sleep(0.1)

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
            shutil.copy(self.file_dir+os.sep+'incomplete'+os.sep+' - .'+self.format, self.file_dir+os.sep)
            os.rename(self.file_dir+os.sep+' - .'+self.format, self.file_dir+os.sep+self.filename)
            shutil.rmtree(self.file_dir+os.sep+'incomplete'+os.sep)

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
	    time.sleep(2)

    def start(self):
        self.set_lock()
        self.set_oddcast_conf()
        self.start_oddcast()
        self.start_rip()

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


class WebView:
    """Gives the web CGI frontend"""
    
    def __init__(self, school_file):
        self.conf = xml2dict(school_file)
        self.conf = self.conf['telecaster']
        self.interfaces = ['eth0', 'eth1', 'eth2']
        ip = ''
        for interface in self.interfaces:
            try:
                ip = get_ip_address(interface)
                if ip:
                    self.ip = ip
                break
            except:
                self.ip = 'localhost'
        self.url = 'http://' + self.ip
        self.port = self.conf['port']
        self.acpi = acpi.Acpi()
        self.format = self.conf['format']
        self.title = self.conf['title']
        self.departments = self.conf['department']
        self.professors = self.conf['professor']
        self.comments = self.conf['comment']
        #print self.departments
        #self.conferences = self.conf['department']['conferences']
        self.len_departments = len(self.departments)
        self.len_professors = len(self.professors)
        self.conference_nb_max = 40
        self.professor_nb_max = 40
        self.refresh = False

    def header(self):
        # Required header that tells the browser how to render the HTML.
        print "Content-Type: text/html\n\n"
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
        if self.refresh:
            print "<meta http-equiv=\"refresh\" content=\"10; URL=telecaster.py\">"
        print "</HEAD>\n"
        
        print "<BODY BGCOLOR =\"#FFFFFF\">"
        print "<div class=\"bg\">"
        print "<div class=\"header\">"
        print "<H3>&nbsp;TeleCaster - L'enregistrement et la diffusion audio en direct par internet</H3>"
        print "</div>"

    def colophon(self):
        date = datetime.datetime.now().strftime("%Y")
        print "<div class=\"colophon\">"
        print "TeleCaster "+version+" &copy; <span>"+date+"</span>&nbsp;<a href=\"http://parisson.com\">Parisson SARL</a>. Tous droits r&eacute;serv&eacute;s."
        print "</div>"
            
    def footer(self):
        print "</div>"
        print "</BODY>"
        print "</HTML>"

    def hardware_data(self):
        self.acpi.update()
        self.power_state = self.acpi.charging_state()
        if self.power_state == 0:
            power_info = "<span style=\"color: red\">batterie</span>"
        elif self.power_state == 1 or self.power_state == 2:
            power_info = "<span style=\"color: green\">secteur</span>"
        else:
            power_info = ""
            
        #if self.power_state == 0:
            #batt_info = "en d&eacute;charge"
        #elif self.power_state == 1:
            #batt_info = "charg&eacute;e"
        #elif self.power_state == 2:
            #batt_info = "en charge"
        #else:
            #batt_info = ""

        if self.acpi.percent() == 127:
            batt_charge = '<span style=\"color: green\">100 &#37;</span>'
        else:
            percent = self.acpi.percent()
            if percent < 10:
                batt_charge = '<span style=\"color: red\">'+str(percent)+' &#37;</span>'
            else:
                batt_charge = '<span style=\"color: green\">'+str(percent)+' &#37;</span>'

        if self.ip == 'localhost':
            ip_info = '<span style=\"color: red\">'+self.ip+'</span>'
        else:
            ip_info = '<span style=\"color: green\">'+self.ip+'</span>'
        
        print "<div class=\"hardware\">"
        print "<div class=\"title\">Informations mat&eacute;rielles</div>"
        print "<table>"
        print "<tr><td>Alimentation :</td>"
        print "<td>%s</td></tr>" % power_info
        #print "<tr><td>Etat batterie :</td>"
        #print "<td>%s</td></tr>" % batt_info
        print "<tr><td>Capacit&eacute; batterie :</td>"
        print "<td>%s</td></tr>" % batt_charge
        #print "<tr><td>Estimation dur&eacute;e batterie :</td>"
        #print "<td>%s</td></tr>" % self.acpi.estimated_lifetime()
        try:
            print "<tr><td>Temp core 1 :</td><td>%s</td></tr>" % self.acpi.temperature(0)
        except:
            pass
        try:
            print "<tr><td>Temp core 2 :</td><td>%s</td></tr>" % self.acpi.temperature(1)
        except:
            pass
        print "<tr><td>Address IP :</td>"
        print "<td>%s</td></tr>" % ip_info
        print "</table>"
        print "</div>"
        

    def start_form(self, message=''):
        self.refresh = False
        self.header()
        self.hardware_data()
        print "<div class=\"main\">"
        #print "<h5><span style=\"color: red\">"+message+"</span></h5>"
        #print "<h5><span style=\"color: red\">Attention, il est important de remplir tous les champs, y compris le commentaire !</span></h5>"
        print "<div \class=\"form\">"
        print "<TABLE BORDER = 0>"
        print "<FORM method=POST ACTION=\""+self.url+"/telecaster/telecaster.py\" name=\"formulaire\">"
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

        print "<TR><TH align=\"left\">Professeur :</TH>"
        print "<TD><select name=\"professor\">"
        print "<option selected>...........Choisissez un professeur...........</option>"
        for professor in self.professors:
            print "<option value=\""+professor['name']+"\">"+professor['name']+"</option>"
        print "</select></TD></TR>"

        print "<TR><TH align=\"left\">Commentaire :</TH>"
        print "<TD><select name=\"comment\">"
        print "<option selected>...........Choisissez un commentaire...........</option>"
        for comment in self.comments:
            print "<option value=\""+comment['text']+"\">"+comment['text']+"</option>"
        print "</select></TD></TR>"
       
        print "</TABLE>"
        print "</div>"
        
        #print "<h5><a href=\""+self.url+":"+self.port+"/augustins.pre-barreau.com_live."+self.format+".m3u\">Cliquez ici pour &eacute;couter le flux continu 24/24 en direct</a></h5>"
        print '<hr>'
        print "<h5><a href=\""+self.url+"/media/\">Cliquez ici pour acc&eacute;der aux archives</a></h5>"
        print "<h5><a href=\""+self.url+"/backup/\">Cliquez ici pour acc&eacute;der aux archives de secours</a></h5>"
        print "</div>"
        print "<div class=\"tools\">"
        print "<INPUT TYPE = hidden NAME = \"action\" VALUE = \"start\">"
        print "<INPUT TYPE = submit VALUE = \"Enregistrer\">"
        print "</FORM>"
        print "</div>"
        self.colophon()
        self.footer()

    def encode_form(self, message=''):
        self.header()
        print "<div class=\"main\">"
        print "<h5><span style=\"color: red\">"+message+"</span></h5>"
        print "<h5><span style=\"color: red\">ENCODAGE EN COURS !</span></h5>"
        print "</div>"
        self.colophon()
        self.footer()

    def stop_form(self, conference_dict, writing, casting):
        """Stop page"""
        department = conference_dict['department']
        conference = conference_dict['conference']
        session = conference_dict['session']
        professor = conference_dict['professor']
        comment = conference_dict['comment']
        self.refresh = True
        self.header()
        self.hardware_data()
        print "<div class=\"main\">"
        
        print "<hr>"
        if writing:
            print "<h4><span style=\"color: green\">Enregistrement en cours...</span></h4>"
        else:
            print "<h4><span style=\"color: red\">PAS d'enregistrement en cours !</span></h4>"
        print '<hr>'
        if casting:
            print "<h4><span style=\"color: green\">Diffusion en cours...</span></h4>"
        else:
            print "<h4><span style=\"color: red\">PAS de diffusion en cours !</span></h4>"
        print "<hr>"
        print "<TABLE BORDER = 0>"
        print "<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement :</TH><TD>"+department+"</TD><TR>"
        print "<TR><TH align=\"left\">Conference :</TH><TD>"+conference+"</TD><TR>"
        print "<TR><TH align=\"left\">Session :</TH><TD>"+session+"</TD><TR>"
        print "<TR><TH align=\"left\">Professeur :</TH><TD>"+professor+"</TD><TR>"
        print "<TR><TH align=\"left\">Commentaire :</TH><TD>"+comment+"</TD><TR>"
        print "</TABLE>"
        print "<hr>"
        print "<h5><a href=\""+self.url+":"+self.port+"/"+clean_string(self.title)+"_-_"+clean_string(department)+"_-_"+clean_string(conference)+"."+self.format+".m3u\">Cliquez ici pour &eacute;couter cette formation en direct</a></h5>"
        print "</div>"
        print "<div class=\"tools\">"
        print "<FORM METHOD = post ACTION = \""+self.url+"/telecaster/telecaster.py\">"
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
        self.title = self.conf['infos']['name']
        self.uid = os.getuid()

    def main(self):
        odd_pid = get_pid('^oddcastv3 -n [^LIVE]', self.uid)
        rip_pid = get_pid('streamripper ', self.uid)
        writing = False
        casting = True
        if rip_pid != []:
            writing = True
        if odd_pid == []:
            casting = False
        
        w = WebView(self.school_file)
        form = cgi.FieldStorage()
        
        if odd_pid == [] and form.has_key("action") and \
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
            if get_pid('^oddcastv3 -n [^LIVE]', self.uid) != []:
                casting = True
            if get_pid('streamripper ', self.uid) == []:
                writing = False
            w.stop_form(self.conference_dict, writing, casting)
            
        elif odd_pid != [] and os.path.exists(self.lock_file) and not form.has_key("action"):
            self.conference_dict = get_conference_from_lock(self.lock_file)
            if get_pid('^oddcastv3 -n [^LIVE]', self.uid) != []:
               casting = True
            if get_pid('streamripper ', self.uid) == []:
                writing = False
            w.stop_form(self.conference_dict, writing, casting)

        elif odd_pid != [] and form.has_key("action") and form["action"].value == "stop":
            if os.path.exists(self.lock_file):
                self.conference_dict = get_conference_from_lock(self.lock_file)
            s = Station(self.conf_file, self.conference_dict, self.lock_file)
            s.stop()
            w.start_form()

        elif odd_pid == []:
            w.start_form()


# Call main function.
conf_file = 'etc/telecaster_mp3.xml'
school_file = 'etc/pre-barreau_conferences.xml'

if __name__ == '__main__':
    t = TeleCaster(conf_file, school_file)
    t.main()

