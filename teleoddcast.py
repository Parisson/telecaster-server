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

version = '0.3'


import os
import cgi
import shutil
import datetime
import time
from tools import *
from mutagen.oggvorbis import OggVorbis


class Course:
    """A course in a class room"""
    
    def __init__(self, dict):
        self.title = dict['title']
        self.department = dict['department']
        self.course = dict['course']
        self.session = dict['session']
        self.professor = dict['professor']
        self.comment = dict['comment']

    def get_info(self):
        return self.title, self.department, self.course, self.session, self.professor, self.comment


class Station(Course):
    """Control the Oddcastv3-jack thread which send audio data to the icecast server
    and the Streamripper thread which write audio on the hard disk"""
    
    def __init__(self, conf_file, course_dict, lock_file):
        Course.__init__(self, course_dict)
        self.conf = xml2dict(conf_file)
        self.conf = self.conf['teleoddcast']
        self.root_dir = self.conf['server']['root_dir']
        self.media_dir = self.conf['media']['dir']
        self.host = self.conf['server']['host']
        self.port = self.conf['server']['port']
        self.password = self.conf['server']['sourcepassword']
        self.url = 'http://'+self.host+':'+self.port
        self.odd_conf_file = self.conf['server']['odd_conf_file']
        self.description = [self.title, self.department, self.course, self.session, self.professor, self.comment]
        self.server_name = [self.title, self.department, self.course, self.session]
        self.ServerDescription = clean_string('_-_'.join(self.description))
        self.ServerName = clean_string('_-_'.join(self.server_name))
        self.mount_point = '/' + clean_string(self.title) + '_-_' + \
                                 clean_string(self.department) + '_-_' + \
                                 clean_string(self.course)+'.ogg'
        self.lock_file = self.root_dir + os.sep + self.conf['server']['lock_file']
        self.filename = self.ServerDescription + '.ogg'
        self.uid = os.getuid()
        self.odd_pid = get_pid('^oddcastv3 -n [^LIVE]', self.uid)
        self.rip_pid = get_pid('streamripper ' + self.url + self.mount_point, self.uid)


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
        command = 'oddcastv3 -n "'+clean_string(self.course)+'" -c '+self.odd_conf_file+ \
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
        output_dir = self.media_dir + os.sep + self.department + os.sep
        #print mount_point
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        command = 'streamripper ' + self.url + self.mount_point + \
                  ' -d '+output_dir+' -D "%S" -s -t --quiet > /dev/null &'
        os.system(command)

    def stop_oddcast(self):
        os.system('kill -9 ' + self.odd_pid[0])
        
    def stop_rip(self):
        print self.rip_pid[0]
        os.system('kill -9 ' + self.rip_pid[0])
        time.sleep(1)
        date = datetime.datetime.now().strftime("%Y")
        dirname = self.media_dir + os.sep + self.department + os.sep + self.ServerName
        if os.path.exists(dirname) and os.path.exists(dirname+os.sep+'incomplete'):
            shutil.move(dirname+os.sep+'incomplete'+os.sep+' - .ogg',dirname+os.sep)
            shutil.rmtree(dirname+os.sep+'incomplete'+os.sep)
            os.rename(dirname+os.sep+' - .ogg',dirname+os.sep+self.filename)

    def write_tags(self):
        date = datetime.datetime.now().strftime("%Y")
        new_title = clean_string('_-_'.join(self.server_name))
        dirname = self.media_dir + os.sep + self.department + os.sep + new_title
        if os.path.exists(dirname+os.sep+self.filename):
            audio = OggVorbis(dirname+os.sep+self.filename)
            audio['TITLE'] = new_title
            audio['ARTIST'] = self.professor
            audio['ALBUM'] = self.title
            audio['DATE'] = date
            audio['GENRE'] = 'Vocal'
            audio['SOURCE'] = self.title
            audio['ENCODER'] = 'TeleOddCast by Parisson'
            audio['COMMENT'] = self.comment
            audio.save()

    def start(self):
        self.set_lock()
        self.set_oddcast_conf()
        self.start_oddcast()
        self.start_rip()

    def stop(self):
        self.stop_rip
        self.write_tags()
        self.stop_oddcast()
        self.del_lock()
        

class WebView:

    def __init__(self, school_file):
        self.conf = xml2dict(school_file)
        self.conf = self.conf['teleoddcast']
        self.url = self.conf['url']
        self.title = self.conf['title']
        self.departments = self.conf['department']
        #print self.departments
        #self.courses = self.conf['department']['courses']
        self.len_departments = len(self.departments)

    def header(self):
        # Required header that tells the browser how to render the HTML.
        print "Content-Type: text/html\n\n"
        print "<HTML>"
        print "<HEAD>"
        print "\t<TITLE>"+self.title+"</TITLE>"
        print "<link href=\"teleoddcast.css\" rel=\"stylesheet\" type=\"text/css\">"
        print '<script language="Javascript" type="text/javascript" >'
        print 'function choix(formulaire)'
        print '{var j; var i = formulaire.department.selectedIndex;'
        print 'if (i == 0)'
        print   'for(j = 1; j < '+ str(self.len_departments) + '; j++)'
        print      'formulaire.course.options[j].text="";'
        #print      'formulaire.course.options[j].value="";'
        print 'else{'
        print '   switch (i){'
        for k in range(0,self.len_departments):
            department = self.departments[k]
            courses = department['courses']
            #print courses
            courses_t = dict2tuple(courses)
            #print courses
            courses = '"'+'","'.join(courses_t)+'"'
            print '       case '+str(k+1)+' : var text = new Array('+courses+'); '
            print '       break;'
        print '       }'
        print '      for(j = 0; j<50; j++)'
        print '       formulaire.course.options[j+1].text=text[j];'
        #print '       formulaire.course.options[j+1].value=text[j];'
        print '}'
        print '      formulaire.course.selectedIndex=0;}'
        print '</script>'
        print "</HEAD>"
        
        print "<BODY BGCOLOR =\"#FFFFFF\">"
        print "<div id=\"bg\">"
        print "<div id=\"header\">"
        print "\t<H3>&nbsp;TeleOddCast - L'enregistrement et la diffusion audio en direct par internet</H3>"
        print "</div>"

    def colophon(self):
        print "<div id=\"colophon\">"
        print "TeleOddCast "+version+" &copy; <span>2007</span>&nbsp;<a href=\"http://parisson.com\">Parisson</a>. Tous droits r&eacute;serv&eacute;s."
        print "</div>"
            
    def footer(self):
        print "</div>"
        print "</BODY>"
        print "</HTML>"

    def start_form(self):
        self.header()
        print "<div id=\"main\">"
        print "<h5><a href=\"http://augustins.pre-barreau.com:8000/crfpa.pre-barreau.com_live.ogg.m3u\">Cliquez ici pour &eacute;couter le flux continu 24/24 en direct</a></h5>"
        print "\t<TABLE BORDER = 0>"
        print "\t\t<form method=post action=\"teleoddcast.py\" name=\"formulaire\">"
        print "\t\t<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        
        print "\t\t<TR><TH align=\"left\">D&eacute;partement :</TH>"
        print "<TD><select name=\"department\" onChange=\"choix(this.form)\">"
        print "<option selected>...........Choisissez un d&eacute;partement...........</option>"
        for department in self.departments:
            print "<option value=\""+department['name']+"\">"+department['name']+"</option>"
        print "</select></TD></TR>"
        
        print "\t\t<TR><TH align=\"left\">Intitul&eacute; du cours :</TH>"
        print "<TD><select name=\"course\">"
        print "<option selected>...........Choisissez un intitul&eacute;...........</option>"
        for i in range(1,50):
            print "<option></option>"
        print "</select></TD></TR>"

        print "\t\t<TR><TH align=\"left\">Session :</TH><TD><select name=\"session\">"
        for i in range(1,21):
            print "<option value=\""+str(i)+"\">"+str(i)+"</option>"
        print "</select></TD></TR>"

        print "\t\t<TR><TH align=\"left\">Professeur :</TH><TD><INPUT type = text name = \"professor\"></TD><TR>"

        print "\t\t<TR><TH align=\"left\">Commentaire :</TH><TD><INPUT type = text name = \"comment\"></TD></TR>"

        print "\t</TABLE>"
        print "\t<h5><span style=\"color: red\">Attention, il est important de remplir tous les champs, y compris le commentaire !</span></h5>"
        print "</div>"
        print "<div id=\"tools\">"
        print "\t<INPUT TYPE = hidden NAME = \"action\" VALUE = \"start\">"
        print "\t<INPUT TYPE = submit VALUE = \"Start\">"
        print "\t</FORM>"
        print "</div>"
        self.colophon()
        self.footer()


    def stop_form(self, course_dict):
        """Stop page"""
        department = course_dict['department']
        course = course_dict['course']
        session = course_dict['session']
        professor = course_dict['professor']
        comment = course_dict['comment']

        self.header()
        print "<div id=\"main\">"
        print "\t<h4><span style=\"color: red\">Cette formation est en cours de diffusion :</span></h4>"
        print "<hr>"
        print "\t<TABLE BORDER = 0>"
        print "\t\t<FORM METHOD = post ACTION = \"teleoddcast.py\">"
        print "\t\t<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        print "\t\t<TR><TH align=\"left\">D&eacute;partement :</TH><TD>"+department+"</TD><TR>"
        print "\t\t<TR><TH align=\"left\">Intitul&eacute; du cours :</TH><TD>"+course+"</TD><TR>"
        print "\t\t<TR><TH align=\"left\">Session :</TH><TD>"+session+"</TD><TR>"
        print "\t\t<TR><TH align=\"left\">Professeur :</TH><TD>"+professor+"</TD><TR>"
        print "\t\t<TR><TH align=\"left\">Commentaire :</TH><TD>"+comment+"</TD><TR>"
        print "\t</TABLE>"
        print "<hr>"
        print "<h5><a href=\""+self.url+"/"+clean_string(self.title)+"_-_"+clean_string(department)+"_-_"+clean_string(course)+".ogg.m3u\">Cliquez ici pour &eacute;couter cette formation en direct</a></h5>"
        print "</div>"
        print "<div id=\"tools\">"
        print "\t<INPUT TYPE = hidden NAME = \"action\" VALUE = \"stop\">"
        print "\t<INPUT TYPE = submit VALUE = \"Stop\">"
        print "\t</FORM>"
        print "</div>"
        self.colophon()
        self.footer()



class TeleOddCast:

    def __init__(self, conf_file, school_file):
        """Main function"""
        self.conf_file = conf_file
        self.school_file = school_file
        conf_t = xml2dict(self.conf_file)
        self.conf = conf_t['teleoddcast']
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
            form.has_key("department") and form.has_key("course") and \
            form.has_key("professor") and form.has_key("comment") and \
            form["action"].value == "start":
            
            self.course_dict = {'title': self.title,
                        'department': form["department"].value,
                        'course': form["course"].value,
                        'session': form["session"].value,
                        'professor': form["professor"].value,
                        'comment': form["comment"].value}

            s = Station(self.conf_file, self.course_dict, self.lock_file)
            s.start()
            w.stop_form(self.course_dict)
            
        elif self.odd_pid != [] and os.path.exists(self.lock_file) and not form.has_key("action"):
            self.course_dict = get_course_from_lock(self.lock_file)
            w.stop_form(self.course_dict)

        elif self.odd_pid != [] and form.has_key("action") and form["action"].value == "stop":
            if os.path.exists(self.lock_file):
                self.course_dict = get_course_from_lock(self.lock_file)
            s = Station(self.conf_file, self.course_dict, self.lock_file)
            s.stop()
            w.start_form()

        elif self.odd_pid == []:
            w.start_form()


# Call main function.
conf_file = 'teleoddcast.xml'
school_file = 'pre-barreau.xml'

if __name__ == '__main__':
    t = TeleOddCast(conf_file, school_file)
    t.main()

