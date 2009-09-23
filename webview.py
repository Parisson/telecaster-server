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
from cgi import FieldStorage
cgitb.enable()

class WebView(FieldStorage):
    """Gives the web CGI frontend"""
    
    def __init__(self, school_file, version):
        FieldStorage.__init__(self)
        self.version = version
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
        self.professors.sort()
        self.comments = self.conf['comment']
        #print self.departments
        #self.conferences = self.conf['department']['conferences']
        self.len_departments = len(self.departments)
        self.len_professors = len(self.professors)
        self.conference_nb_max = 40
        self.professor_nb_max = 40
        self.refresh = False
        self.uid = os.getuid()

    def header(self):
        # Required header that tells the browser how to render the HTML.
        print "Content-Type: text/html\n\n"
        print "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">"
        print "<HTML>"
        print "<HEAD>"
        print "<TITLE>TeleCaster - "+self.title+"</TITLE>"
        print "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">"
        print "<link href=\""+self.url+"/telecaster/css/telecaster.css\" rel=\"stylesheet\" type=\"text/css\">"
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
        print "TeleCaster "+self.version+" &copy; <span>"+date+"</span>&nbsp;<a href=\"http://parisson.com\">Parisson SARL</a>. Tous droits r&eacute;serv&eacute;s."
        print "</div>"
            
    def footer(self):
        print "</div>"
        print "</BODY>"
        print "</HTML>"

    def hardware_data(self):
        jackd_pid = get_pid('jackd ', self.uid)
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

        if jackd_pid == []:
            jackd_info = '<span style=\"color: red\">&eacute;teint</span>'
        else:
            jackd_info = '<span style=\"color: green\">d&eacute;marr&eacute;</span>'
        
        print "<div class=\"hardware\">"
        print "<div class=\"title\">Informations mat&eacute;rielles</div>"
        print "<table class=\"hardware\">"
        print "<tr><td>Alimentation :</td>"
        print "<td>%s</td></tr>" % power_info
        #print "<tr><td>Etat batterie :</td>"
        #print "<td>%s</td></tr>" % batt_info
        print "<tr><td>Capacit&eacute; batterie :</td>"
        print "<td>%s</td></tr>" % batt_charge
        #print "<tr><td>Estimation dur&eacute;e batterie :</td>"
        #print "<td>%s</td></tr>" % self.acpi.estimated_lifetime()
        try:
            print "<tr><td>Temp Core 1 :</td><td>%s</td></tr>" % self.acpi.temperature(0)
        except:
            pass
        try:
            print "<tr><td>Temp Core 2 :</td><td>%s</td></tr>" % self.acpi.temperature(1)
        except:
            pass
        print "<tr><td>Address IP :</td>"
        print "<td>%s</td></tr>" % ip_info
        print "<tr><td>Serveur JACK :</td>"
        print "<td>%s</td></tr>" % jackd_info
        print "</table>"
        print "</div>"
        

    def start_form(self, message=''):
        self.refresh = False
        self.header()
        self.hardware_data()
        print "<form method=\"post\" action=\""+self.url+"/telecaster/telecaster.py\" name=\"formulaire\">"
        print "<div class=\"main\">"
        print "<table class=\"form\">"
        print "<TR><TH align=\"left\">Titre:</TH><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement:</TH>"
        print "<TD><select name=\"department\" onChange=\"choix(this.form)\">"
        print "<option selected>...........Choisissez un d&eacute;partement...........</option>"
        for department in self.departments:
            print "<option value=\""+department['name']+"\">"+department['name']+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Conf&eacute;rence:</TH>"
        print "<TD><select name=\"conference\">"
        print "<option selected>...........Choisissez une conf&eacute;rence...........</option>"
        for i in range(1,self.conference_nb_max):
            print "<option></option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Session:</TH><TD><select name=\"session\">"
        for i in range(1,21):
            print "<option value=\""+str(i)+"\">"+str(i)+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Professeur:</TH>"
        print "<TD><select name=\"professor\">"
        print "<option selected>...........Choisissez un professeur...........</option>"
        for professor in self.professors:
            print "<option value=\""+professor['name']+"\">"+professor['name']+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Commentaire:</TH>"
        print "<TD><INPUT type = text name = \"comment\"></TD></TR>"

        #print "<TD><select name=\"comment\">"
        #print "<option selected>...........Choisissez un commentaire...........</option>"
        #for comment in self.comments:
        #    print "<option value=\""+comment['text']+"\">"+comment['text']+"</option>"
        #print "</select></TD></TR>"

        print "</table>"
        print "</div>"
        #print "<h5><a href=\""+self.url+":"+self.port+"/augustins.pre-barreau.com_live."+self.format+".m3u\">Cliquez ici pour &eacute;couter le flux continu 24/24 en direct</a></h5>"
        print "<div class=\"tools\">"
        print "<div class=\"buttons\">"
        #print "<INPUT TYPE = hidden NAME = \"action\" VALUE = \"start\">"
        print "<button type=\"submit\" name=\"action\" value=\"start\" class=\"negative\"><img src=\"img/stop.png\" alt=\"\">Record</button>"
        print "<button type=\"submit\" class=\"positive\"><img src=\"img/arrow_refresh.png\" alt=\"\">Refresh</button>"
        print "<a href=\""+self.url+"/media/\"><img src=\"img/folder_go.png\" alt=\"\">Archives</a>"
        print "<a href=\""+self.url+"/backup/\"><img src=\"img/bin.png\" alt=\"\">Trash</a>"
        #print "<INPUT TYPE = submit VALUE = \"Enregistrer\">"
        print "</div>"
        print "</div>"
        print "</form>"
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
        print "<table class=\"form\">"
        print "<TR><TH align=\"left\">Titre :</TH><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement :</TH><TD>"+department+"</TD></TR>"
        print "<TR><TH align=\"left\">Conference :</TH><TD>"+conference+"</TD></TR>"
        print "<TR><TH align=\"left\">Session :</TH><TD>"+session+"</TD></TR>"
        print "<TR><TH align=\"left\">Professeur :</TH><TD>"+professor+"</TD></TR>"
        print "<TR><TH align=\"left\">Commentaire :</TH><TD>"+comment+"</TD></TR>"
        print "</table>"
        #print "<h5><a href=\""+self.url+":"+self.port+"/"+clean_string(self.title)+"_-_"+clean_string(department)+"_-_"+clean_string(conference)+"."+self.format+".m3u\">Cliquez ici pour &eacute;couter cette formation en direct</a></h5>"
        print "</div>"
        print "<div class=\"tools\">"
        print "<form method=\"post\" action=\""+self.url+"/telecaster/telecaster.py\">"
        print "<div class=\"buttons\">"
        if writing:
            print "<button type=\"submit\" class=\"positive\"><img src=\"img/drive_add.png\" alt=\"\">Recording...</button>"
        else:
            print "<button type=\"submit\" class=\"negative\"><img src=\"img/drive_error.png\" alt=\"\">NOT Recording !</button>"
        if casting:
            print "<button type=\"submit\" class=\"positive\"><img src=\"img/transmit_add.png\" alt=\"\">Diffusing...</button>"
        else:
            print "<button type=\"submit\" class=\"negative\"><img src=\"img/transmit_error.png\" alt=\"\">NOT Diffusing !</button>"
        print "<button type=\"submit\"><img src=\"img/arrow_refresh.png\" alt=\"\">Refresh</button>"
        print "<a href=\""+self.url+":"+self.port+"/"+clean_string(self.title)+"_-_"+clean_string(department)+"_-_"+clean_string(conference)+"."+self.format+".m3u\"><img src=\"img/control_play_blue.png\" alt=\"\">Play</a>"
        print "<button type=\"submit\" name=\"action\" value=\"stop\" class=\"negative\"><img src=\"img/cancel.png\" alt=\"\">Stop</button>"
        print "</div>"
        print "</form>"
        print "</div>"
        self.colophon()
        self.footer()

