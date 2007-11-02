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

version = '0.2'

import os
import cgi
import shutil
import datetime
import time
from mutagen.oggvorbis import OggVorbis

def get_pid(proc,uid):
	"""Get a process pid filtered by arguments and uid"""
	(list1, list2) = os.popen4('pgrep -f -U '+str(uid)+' '+'"'+proc+'"')
	pids = list2.readlines()
	if pids != '':
		for pid in pids:
			index = pids.index(pid)
			pids[index] = pid[:-1]
	return pids
		

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

def start_stream(odd_conf_file, lock_file, media_dir, title, department, course, session, professor, comment):
	oddconf = open(odd_conf_file,'r')
	params = oddconf.readlines()
	oddconf.close()
	newlines = []
	for line in params:
		if 'ServerDescription' in line.split('='):
			ServerDescription = title+'_-_'+department+'_-_'+course+'_-_'+session+'_-_'+professor+'_-_'+comment
			ServerDescription = ServerDescription.replace(' ','_')
			newlines.append('ServerDescription='+ServerDescription+'\n')
		elif 'ServerName' in line.split('='):	
			ServerName=title+'_-_'+department+'_-_'+course+'_-_'+session
			ServerName=clean_string(ServerName)
			newlines.append('ServerName='+ServerName+'\n')
		elif 'ServerMountpoint' in line.split('='):
			mount_point = '/'+clean_string(title)+'_-_'+clean_string(department)+'_-_'+clean_string(course)+'.ogg'
			newlines.append('ServerMountpoint='+mount_point+'\n')
		else:
			newlines.append(line)
	oddconf = open(odd_conf_file,'w')
	oddconf.writelines(newlines)
	oddconf.close()
	os.system('oddcastv3 -n "'+clean_string(course)+'" -c '+odd_conf_file+ \
		  ' alsa_pcm:capture_1 alsa_pcm:capture_2 > /dev/null &')
	lock = open(lock_file,'w')
	lock_text = clean_string(title+'_*_'+department+'_*_'+course+'_*_'+session+'_*_'+professor+'_*_'+comment)
	lock_text = lock_text.replace('\n','')
	lock.write(lock_text)
	lock.close()
	time.sleep(1)
	return mount_point

def start_rip(url, mount_point, media_dir, department):
	output_dir = media_dir+os.sep+department+os.sep
	#print mount_point
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
	os.system('streamripper '+url+mount_point+' -d '+output_dir+' -D "%S" -s -t --quiet > /dev/null &')

def stop_oddcast(pid):
	os.system('kill -9 '+pid)
	
def rm_lockfile(lock_file):
	os.system('rm '+lock_file)

def stop_rip(pid,media_dir,title,department,course,session,professor,comment):
	os.system('kill -9 '+pid)
	time.sleep(1)
	date = datetime.datetime.now().strftime("%Y")
	filename = clean_string(title+'_-_'+department+'_-_'+course+'_-_'+session+'_-_'+date+'_-_'+professor+'_-_'+comment+'.ogg')
	dirname = media_dir + os.sep + department + os.sep + clean_string(title+'_-_'+department+'_-_'+course+'_-_'+session)
	if os.path.exists(dirname) and os.path.exists(dirname+os.sep+'incomplete'):
		shutil.move(dirname+os.sep+'incomplete'+os.sep+' - .ogg',dirname+os.sep)
		shutil.rmtree(dirname+os.sep+'incomplete'+os.sep)
		os.rename(dirname+os.sep+' - .ogg',dirname+os.sep+filename)

def get_params_from_lock(lock_file):
	lockfile = open(lock_file,'r')
	params = lockfile.readline()
	params_ok = params.split('_*_')
	lockfile.close()
	return params_ok

def write_tags(media_dir,title,department,course,session,professor,comment):
	date = datetime.datetime.now().strftime("%Y")
	filename = clean_string(title+'_-_'+department+'_-_'+course+'_-_'+session+'_-_'+date+'_-_'+professor+'_-_'+comment+'.ogg')
	new_title = clean_string(title+'_-_'+department+'_-_'+course+'_-_'+session)
	dirname = media_dir + os.sep + department + os.sep + new_title
	if os.path.exists(dirname+os.sep+filename):
		audio = OggVorbis(dirname+os.sep+filename)
		audio['TITLE'] = new_title
		audio['ARTIST'] = professor
		audio['ALBUM'] = title
		audio['DATE'] = date
		audio['GENRE'] = 'Vocal'
		audio['SOURCE'] = title
		audio['ENCODER'] = 'TeleOddCast by Parisson'
		audio['COMMENT'] = comment
		audio.save()
		
# Required header that tells the browser how to render the HTML.
print "Content-Type: text/html\n\n"

def header(title):
	print "<HTML>"
	print "<HEAD>"
	print "\t<TITLE>"+title+"</TITLE>"
	print "<link href=\"teleoddcast.css\" rel=\"stylesheet\" type=\"text/css\">"
	print "</HEAD>"
	print "<BODY BGCOLOR =\"#FFFFFF\">"
	print "<div id=\"bg\">" 
	print "<div id=\"header\">"
	print "\t<H3>&nbsp;TeleOddCast - L'enregistrement et la diffusion audio en direct par internet</H3>"
	print "</div>"

def colophon():
	print "<div id=\"colophon\">"
	print "TeleOddCast "+version+" &copy; <span>2007</span>&nbsp;<a href=\"http://parisson.com\">Parisson</a>. Tous droits réservés."
	print "</div>"
        
def footer():
	print "</div>"
	print "</BODY>"
	print "</HTML>"



def start_form(title, departments, courses):
	header(title)
	print "<div id=\"main\">"
	print "<h5><a href=\"http://augustins.pre-barreau.com:8000/crfpa.pre-barreau.com_live.ogg.m3u\">Cliquez ici pour &eacute;couter le flux continu 24/24 en direct</a></h5>"
	print "\t<TABLE BORDER = 0>"
	print "\t\t<FORM METHOD = post ACTION = \"teleoddcast.py\">"
	print "\t\t<TR><TH align=\"left\">Titre :</TH><TD>"+title+"</TD></TR>"
	print "\t\t<TR><TH align=\"left\">D&eacute;partement :</TH><TD><select name=\"department\">"
	for department in departments:
		print "<option value=\""+department+"\">"+department+"</option>"
	print "</select></TD></TR>"
	print "\t\t<TR><TH align=\"left\">Intitul&eacute; du cours :</TH><TD><select name=\"course\">"
	for course in courses:
		print "<option value=\""+course+"\">"+course+"</option>"
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
	colophon()
	footer()


def stop_form(url,title, department, course, session, professor, comment):
	"""Stop page"""
	header(title)
	print "<div id=\"main\">"
	print "\t<h4><span style=\"color: red\">Cette formation est en cours de diffusion :</span></h4>"
	print "<hr>"
	print "\t<TABLE BORDER = 0>"
	print "\t\t<FORM METHOD = post ACTION = \"teleoddcast.py\">"
	print "\t\t<TR><TH align=\"left\">Titre :</TH><TD>"+title+"</TD></TR>"
	print "\t\t<TR><TH align=\"left\">D&eacute;partement :</TH><TD>"+department+"</TD><TR>"
	print "\t\t<TR><TH align=\"left\">Intitul&eacute; du cours :</TH><TD>"+course+"</TD><TR>"
	print "\t\t<TR><TH align=\"left\">Session :</TH><TD>"+session+"</TD><TR>"
	print "\t\t<TR><TH align=\"left\">Professeur :</TH><TD>"+professor+"</TD><TR>"
	print "\t\t<TR><TH align=\"left\">Commentaire :</TH><TD>"+comment+"</TD><TR>"
	print "\t</TABLE>"
	print "<hr>"
	print "<h5><a href=\""+url+"/"+clean_string(title)+"_-_"+clean_string(department)+"_-_"+clean_string(course)+".ogg.m3u\">Cliquez ici pour &eacute;couter cette formation en direct</a></h5>"
	print "</div>"
	print "<div id=\"tools\">"
	print "\t<INPUT TYPE = hidden NAME = \"action\" VALUE = \"stop\">"
	print "\t<INPUT TYPE = submit VALUE = \"Stop\">"
	print "\t</FORM>"
	print "</div>"
	colophon()
	footer()

def main():
	"""Main function"""
	title = 'Pre-barreau - Augustins'
	root_dir = '/var/www/cgi-bin/'
	media_dir = root_dir + 'media/'
	server = 'localhost'
	port = '8000'
	url = 'http://'+server+':'+port
	uid = os.getuid()
	
	departments = get_lines(root_dir+'pre-barreau_departments.txt') 
	courses = get_lines(root_dir+'pre-barreau_courses.txt')
	odd_conf_file = root_dir+'teleoddcast.cfg'
	
	oddcast_pid = get_pid('^oddcastv3 -n [^LIVE]',uid)
	lock_file = root_dir+'teleoddcast.lock'
	
	form = cgi.FieldStorage()
		
	if oddcast_pid == [] and form.has_key("action") and \
	form.has_key("department") and form.has_key("course") and form.has_key("professor") \
	and form.has_key("comment") and form["action"].value == "start":
		
		mount_point = start_stream(odd_conf_file, lock_file, media_dir, title, 
			form["department"].value, form["course"].value, 
			form["session"].value, form["professor"].value, 
			form["comment"].value)
		
		department = form["department"].value		
		start_rip(url,mount_point,media_dir,department)

		stop_form(url,title,
			form["department"].value, form["course"].value,
			form["session"].value, form["professor"].value, 
			form["comment"].value)

	elif oddcast_pid != [] and os.path.exists(lock_file) and not form.has_key("action"):
		
		title,department,course,session,professor,comment = get_params_from_lock(lock_file)
		stop_form(url,title,department,course,session,professor,comment)

	elif oddcast_pid != [] and form.has_key("action") and form["action"].value == "stop":
		
		if os.path.exists(lock_file):
			title,department,course,session,professor,comment = get_params_from_lock(lock_file)
	
		stop_oddcast(oddcast_pid[0])
		mount_point = '/'+clean_string(title)+'_-_'+clean_string(department)+'_-_'+clean_string(course)+'.ogg'
	 	#print mount_point
		streamripper_pid = get_pid('streamripper '+url+mount_point,uid)

		if streamripper_pid != []:
			stop_rip(streamripper_pid[0],media_dir,title,department,course,session,professor,comment)
			write_tags(media_dir,title,department,course,session,professor,comment)
		
		rm_lockfile(lock_file)
		
		start_form(title, departments, courses)

	elif oddcast_pid == []:
		start_form(title, departments, courses)

# Call main function.
main()

