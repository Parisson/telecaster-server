# Create your views here.

import os
import cgi
import datetime
import time
import string

from tools import *
from models import *
from forms import*

from jsonrpc import jsonrpc_method

from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.template import RequestContext, loader
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.views.generic import list_detail
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.context_processors import csrf
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ObjectDoesNotExist


def render(request, template, data = None, mimetype = None):
    return render_to_response(template, data, context_instance=RequestContext(request),
                              mimetype=mimetype)
                              
class WebView(object):
    
    hidden_fields = ['started', 'datetime_start', 'datetime_stop']
    
    def __init__(self, conf_file):
        self.uid = os.getuid()
        self.user = pwd.getpwuid(os.getuid())[0]
        self.user_dir = '/home' + os.sep + self.user + os.sep + '.telecaster'
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        self.conf_file = conf_file
        conf_dict = xml2dict(self.conf_file)
        self.conf = conf_dict['telecaster']
        self.title = self.conf['infos']['name']
        self.log_file = self.conf['log']
        self.logger = Logger(self.log_file)
        self.url = self.conf['infos']['url']
        self.status = Status(self.conf)
    
    def index(self, request):
        status = self.get_status()
        stations = Station.objects.filter(started=True)
        status = self.get_status()
        
        if stations or (status['writing'] or status['casting']):
            template = 'telecaster/stop.html'
            # FIXME: manage multiple stations
            station = stations[0]
            station.set_conf(self.conf)
            station.setup()
            if request.method == 'POST':
                station.stop()
                time.sleep(2)
                self.logger.write_info('stop')
                return HttpResponseRedirect('/')
            
        else:
            template = 'telecaster/start.html'
            if request.method == 'POST':
                station = StationForm(data=request.POST)
                if station.is_valid():
                    station.set_conf(self.conf)
                    station.setup()
                    station.start()
                    station.started = True
                    station.save()
                    self.logger.write_info('start')
                    time.sleep(2)
                    return HttpResponseRedirect('/')
            else:
                station = StationForm()
                
        
        return render(request, template, {'station': station, 'status': status, 
                                'hidden_fields': self.hidden_fields})
            

    @jsonrpc_method('telecaster.get_status')
    def get_status_json(request):
        status = Status(self.conf)
        status.update()
        return status.to_dict()
        
    def get_status(self):
        status = Status(self.conf)
        status.update()
        return status.to_dict()


class Status(object):
        
    interfaces = ['eth0', 'eth1', 'eth2', 'eth0-eth2','eth3']
    acpi_states = {0: 'battery', 1: 'battery', 2: 'AC'}
    
    def __init__(self, conf):
        self.acpi = acpi.Acpi()
        self.conf = conf
        self.uid = os.getuid()
        self.user = pwd.getpwuid(os.getuid())[0]
        self.user_dir = '/home' + os.sep + self.user + os.sep + '.telecaster'
        
    def update(self):
        self.acpi.update()
        try:
            self.temperature = self.acpi.temperature(0)
        except:
            self.temperature = 'N/A'
        self.get_ids()
        self.get_hosts()
    
    def to_dict(self):
        status = {'acpi_state': self.acpi_states[self.acpi.charging_state()], 
                  'acpi_percent': str(self.acpi.percent()), 
                  'temperature': self.temperature, 
                  'jack_state': self.jacking, 
                  'url': self.url, 
                  'ip': self.ip, 
                  'url': self.url, 
                  'casting': self.casting, 
                  'writing': self.writing,    
                  }
        return status
        
    def get_hosts(self):
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
        
    def get_ids(self):  
        edcast_pid = get_pid('edcast_jack', self.uid)
        deefuzzer_pid = get_pid('/usr/bin/deefuzzer '+self.user_dir+os.sep+'deefuzzer.xml', self.uid)
        jackd_pid = get_pid('jackd', self.uid)
        if jackd_pid == []:
            jackd_pid = get_pid('jackdbus', self.uid)
        self.writing = edcast_pid != []
        self.casting = deefuzzer_pid != []
        self.jacking = jackd_pid != []
