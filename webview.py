#!/usr/bin/python
# -*- coding: utf-8 -*-
# *-* coding: utf-8 *-*
"""
   telecaster

   Copyright (c) 2006-2010 Guillaume Pellerin <yomguy@parisson.org>

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
#import cgitb
import datetime
import time
import string
from tools import *
from cgi import FieldStorage
#cgitb.enable()

class WebView(FieldStorage):
    """Gives the web CGI frontend"""

    def __init__(self, conf,  version):
        FieldStorage.__init__(self)
        self.conf = conf
        self.version = version
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
        if 'url' in self.conf['infos']:
            self.url = 'http://' + self.conf['infos']['url']
        else:
            self.url = 'http://' + self.ip
        self.rss_url = self.url+'/rss/telecaster.xml'
        self.port = '8000'
        self.acpi = acpi.Acpi()
        self.format = self.conf['media']['format']
        self.short_name = self.conf['infos']['short_name']
        self.title = self.conf['infos']['name'] + ' - ' +  self.conf['infos']['description']
        self.departments = self.conf['department']
        self.professors = self.conf['professor']
        self.professors.sort()
        self.comments = self.conf['comment']
        self.len_departments = len(self.departments)
        self.len_professors = len(self.professors)
        self.conference_nb_max = 40
        self.professor_nb_max = 40
        self.refresh = False
        self.refresh_value = 20
        self.uid = os.getuid()
        self.casting = False
        self.writing = False

    def header(self):
        # Required header that tells the browser how to render the HTML.
        print "Content-Type: text/html\n\n"
        print "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">"
        print "<HTML>"
        print "<HEAD>"
        print "<TITLE>TeleCaster - "+self.title+"</TITLE>"
        print "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">"

        print "<link href=\"/telecaster/css/telecaster.css\" rel=\"stylesheet\" type=\"text/css\">"

    def javascript(self):
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

        # rss ajax
        #print "<script type=\"text/javascript\" src=\"js/rssajax.js\"></script>"
        #print "<script type=\"text/javascript\">"
        #print " function rss_reload(url) {"
        #print "  getRSS(url)"
        #print "  setTimeout(\"rss_reload(\'\" + url + \"\')\", 10000);}"
        #print "</script>"
    
    def sub_header(self):
        if self.refresh:
            print "<meta http-equiv=\"refresh\" content=\"" + str(self.refresh_value) + "; URL=telecaster.py\">"
        print "</HEAD>\n"
        #print "<BODY bgcolor =\"#ffffff\" onload=\"rss_reload(\'" + self.rss_url + "\');\">"
        print "<BODY>"
        print "<div class=\"bg\">"
        print "<div class=\"header\">"
        print "<img src=\"img/logo_telecaster_wh.png\" alt=\"logo_telecaster\">"
        print "<div class=\"title_main\">&nbsp;TeleCaster - Audio Web Live Recording</div>"
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
        jackd_pid = get_pid('jackd', self.uid)
        if jackd_pid == []:
            jackd_pid = get_pid('jackdbus', self.uid)
        self.acpi.update()
        self.power_state = self.acpi.charging_state()
        if self.power_state == 0:
            power_info = "<span style=\"color: red\">batterie</span>"
        elif self.power_state == 1 or self.power_state == 2:
            power_info = "<span style=\"color: green\">secteur</span>"
        else:
            power_info = ""
            
        if self.acpi.percent() == 127:
            batt_charge = '<span style=\"color: green\">100 &#37;</span>'
        else:
            percent = self.acpi.percent()
            if percent < 10:
                batt_charge = '<span style=\"color: red\"><b>'+str(percent)+' &#37;</b></span>'
            else:
                batt_charge = '<span style=\"color: green\">'+str(percent)+' &#37;</span>'

        if self.ip == 'localhost':
            ip_info = '<span style=\"color: red\"><b>'+self.ip+'</b></span>'
        else:
            ip_info = '<span style=\"color: green\">'+self.ip+'</span>'

        if jackd_pid == []:
            jackd_info = '<span style=\"color: red\"><b>OFF</b></span>'
        else:
            jackd_info = '<span style=\"color: green\">On</span>'

        print "<div class=\"hardware\">"
        print "<div class=\"title\">Status</div>"
        print "<table class=\"hardware\">"
        print "<tr><td>Name</td><TD> : </TD>"
        print "<td>%s</td></tr>" % self.conf['infos']['url']
        print "<tr><td>IP address</td><TD> : </TD>"
        print "<td>%s</td></tr>" % ip_info
        print "<tr><td>Power</td><TD> : </TD>"
        print "<td>%s</td></tr>" % power_info
        print "<tr><td>Battery charge</td><TD> : </TD>"
        print "<td>%s</td></tr>" % batt_charge
        try:
            print "<tr><td>Temp core 1</td><TD> : </TD><td>%s</td></tr>" % self.acpi.temperature(0)
        except:
            pass
        try:
            print "<tr><td>Temp core 2</td><TD> : </TD><td>%s</td></tr>" % self.acpi.temperature(1)
        except:
            pass
        print "<tr><td>JACK audio server</td><TD> : </TD>"
        print "<td>%s</td></tr>" % jackd_info
        print "<tr><td><div class=\"buttons\">"
        if self.writing:
            print "<button class=\"positive\"><img src=\"img/drive_add.png\" alt=\"\">Recording...</button>"
        else:
            print "<button class=\"negative\"><img src=\"img/drive_error.png\" alt=\"\">NOT Recording !</button>"
        print "</div></td>"
        print "<td></td>"
        print "<td><div class=\"buttons\">"
        if self.casting:
            print "<button class=\"positive\"><img src=\"img/transmit_add.png\" alt=\"\">Diffusing...</button>"
        else:
            print "<button class=\"negative\"><img src=\"img/transmit_error.png\" alt=\"\">NOT Diffusing !</button>"
        print "</div>"
        print "</td></tr>"
        print "</table>"
        print "</div>"


    def start_form(self, writing, casting, message=''):
        self.casting = writing
        self.writing = casting
        self.refresh = False
        
        self.header()
        self.javascript()
        self.sub_header()
        self.hardware_data()
        
        print "<form method=\"POST\" action=\"telecaster.py\" name=\"formulaire\">"
        print "<div class=\"main\">"
        print "<table class=\"form\">"
        print "<TR><TH align=\"left\">Titre</TH><TD> : </TD><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement</TH><TD> : </TD>"
        print "<TD><select name=\"department\" onChange=\"choix(this.form)\">"
        print "<option selected=\"\">...........Choisissez un d&eacute;partement...........</option>"
        for department in self.departments:
            print "<option value=\""+department['name']+"\">"+department['name']+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Conf&eacute;rence</TH><TD> : </TD>"
        print "<TD><select name=\"conference\">"
        print "<option selected=\"\">...........Choisissez une conf&eacute;rence...........</option>"
        for i in range(1,self.conference_nb_max):
            print "<option></option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Session</TH><TD> : </TD><TD><select name=\"session\">"
        for i in range(1,21):
            print "<option value=\""+str(i)+"\">"+str(i)+"</option>"
        print "</select></TD></TR>"
        print "<TR><TH align=\"left\">Professeur</TH><TD> : </TD>"
        print "<TD><INPUT type = text name = \"professor\"></TD></TR>"
        print "<TR><TH align=\"left\">Commentaire</TH><TD> : </TD>"
        print "<TD><INPUT type = text name = \"comment\"></TD></TR>"
        print "</table>"
        print "</div>"
        print "<div class=\"tools\">"
        print "<div class=\"buttons\">"
        print "<button type=\"submit\" class=\"positive\"><img src=\"img/arrow_refresh.png\" alt=\"\">Refresh</button>"
        print "<button type=\"submit\" name=\"action\" value=\"start\" class=\"negative\"><img src=\"img/stop.png\" alt=\"\">Record</button>"
        print "<a href=\"http://"+self.url+"/archives/\"><img src=\"img/folder_go.png\" alt=\"\">Archives</a>"
        print "<a href=\"http://"+self.url+"/trash/\"><img src=\"img/bin.png\" alt=\"\">Trash</a>"
        print "</div>"
        print "</div>"
        print "</form>"
        self.colophon()
        self.footer()

    def stop_form(self, conference_dict, writing, casting):
        department = conference_dict['department']
        conference = conference_dict['conference']
        session = conference_dict['session']
        professor = conference_dict['professor']
        comment = conference_dict['comment']
        self.mount_point ='-'.join([clean_string(self.short_name),clean_string(department), clean_string(conference)])+'.'+self.format+'.m3u'
        self.writing = writing
        self.casting = casting
        self.refresh = True
        
        self.header()
        self.sub_header()
        
        print "<form method=\"POST\" action=\"telecaster.py\" name=\"formulaire\">"
        
        self.hardware_data()
        
        print "<div class=\"main\">"
        print "<table class=\"form\">"
        print "<TR><TH align=\"left\">Titre</TH><TD> : </TD><TD>"+self.title+"</TD></TR>"
        print "<TR><TH align=\"left\">D&eacute;partement</TH><TD> : </TD><TD>"+department+"</TD></TR>"
        print "<TR><TH align=\"left\">Conference</TH><TD> : </TD><TD>"+conference+"</TD></TR>"
        print "<TR><TH align=\"left\">Session</TH><TD> : </TD><TD>"+session+"</TD></TR>"
        print "<TR><TH align=\"left\">Professeur</TH><TD> : </TD><TD>"+professor+"</TD></TR>"
        print "<TR><TH align=\"left\">Commentaire</TH><TD> : </TD><TD>"+comment+"</TD></TR>"
        print "</table>"
        print "</div>"
        print "<div class=\"tools\">"
        print "<div class=\"buttons\">"
        print "<button><img src=\"img/arrow_refresh.png\" alt=\"\">Refresh</button>"
        print "<a href=\"http://"+self.url+":"+self.port+"/"+self.mount_point+"\"><img src=\"img/control_play_blue.png\" alt=\"\">Play</a>"
        print "<button type=\"submit\" name=\"action\" value=\"stop\" class=\"negative\"><img src=\"img/cancel.png\" alt=\"\">Stop</button>"
        print "<a href=\"http://"+self.url+"/archives/\"><img src=\"img/folder_go.png\" alt=\"\">Archives</a>"
        print "<a href=\"http://"+self.url+"/trash/\"><img src=\"img/bin.png\" alt=\"\">Trash</a>"
        print "</div>"
        print "</div>"
        print "</form>"
        self.colophon()
        self.footer()

