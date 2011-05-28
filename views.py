# Create your views here.

import os
import cgi
import datetime
import time
import string

from tools import *
from models import *
from forms import*


def render(request, template, data = None, mimetype = None):
    return render_to_response(template, data, context_instance=RequestContext(request),
                              mimetype=mimetype)
                              
class WebView(object):
    
    interfaces = ['eth0', 'eth1', 'eth2', 'eth0-eth2','eth3']
    acpi_states = {0: 'battery', 1: 'AC', 2: 'AC'}
    acpi = acpi.Acpi()
    
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
    
    def index(self, request):
        self.get_ids()
        stations = Station.objects.filter(started=True)
        
        if stations and (self.writing or self.casting):
            template = 'telecaster/stop.html'
            # FIXME: manage multiple stations
            station = stations[0]
            if request.method == 'POST':
                station.set_conf(self.conf)
                station.setup()
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
                
        return render(request, template, {'station': station})
            
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
        self.writing = edcast_pid != []
        self.casting = deefuzzer_pid != []
    
    def get_status(self):
        self.get_hosts()
        self.get_ids()
        self.acpi.update()
        status = {}
        status['acpi_state'] = acpi_states[self.acpi.charging_state()]
        status['acpi_percent'] = self.acpi.percent()
        status['acpi_temperature'] = self.acpi.temperature(0)
        status['jack_state'] = jackd_pid != []
        status['url'] = self.url
        status['ip'] = self.ip
        status['url'] = self.url
        status['casting'] = self.casting
        status['writing'] = self.writing
        return status
        
