##############################################################################
##
## $Id: acpi.py,v 1.23 2003/12/15 20:04:09 riemer Exp $
##
## Copyright (C) 2002-2008 Tilo Riemer <riemer@lincvs.org>,
##                         Luc Sorgue  <luc.sorgue@laposte.net> and
##                         Rds <rds@rdsarts.com> and
##                         Guillaume Pellerin <yomguy@parisson.com>
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
## 3. The name of the author may not be used to endorse or promote products
##    derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
## IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
## IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
## NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
## THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################

import os,stat,sys


# genenal constants ###########################################################

#enums

VERSION      = "0.3.0"

OFFLINE      =  0
ONLINE       =  1
CHARGING     =  2   #implies ONLINE
FAN_OFF      =  0
FAN_ON       =  1



# exceptions ##################################################################

#exception enums
ERR_GENERIC               = -1
ERR_NO_DEVICE             = -2
ERR_NOT_IMPLEMENTED       = -3
ERR_NO_LOW_LEVEL          = -4
ERR_CONFIGURATION_CHANGED = -5   #reload module? or function reconfigure?
ERR_NOT_ALLOWED           = -6   #access for some resource not allowed --> better idea?

class AcpiError(Exception):
    """ACPI exceptions"""

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        if self.errno == ERR_GENERIC:
            return "Any ACPI error occured."
        elif self.errno == ERR_NO_DEVICE:
            return "ACPI is not configured on this host."
        elif self.errno == ERR_NOT_IMPLEMENTED:
            return "No implementation for this operating system."
        elif self.errno == ERR_NO_LOW_LEVEL:
            return "Acpi_lowlevel module not found."
        elif self.errno == ERR_CONFIGURATION_CHANGED:
            return "ACPI configuartion has been changed."
        else:
            return "Unknown error occured."



# interface ###################################################################

class Acpi:
    """Interface class for ACPI"""

    def __init__(self):
        res = sys.platform
        if res.find("freebsd4") > -1:
            self.acpi = None #throw exception
            raise AcpiError, ERR_NOT_IMPLEMENTED

        elif res.find("netbsd1") > -1:
            self.acpi = None #throw exception
            raise AcpiError, ERR_NOT_IMPLEMENTED

        elif res.find("linux2") > -1:
            self.acpi = AcpiLinux()

        elif res.find("linux") > -1:
            #some systems return linux instead of linux2. We should
            #show a warning or check by ourselves for Linux2
            self.acpi = AcpiLinux()

        else:
            self.acpi = None #throw exception (os unknown)
            raise AcpiError, ERR_NOT_IMPLEMENTED


    def identity(self):
        """Returns the identity of this module"""
        return "acpi.py"

    def version(self):
        """Returns the version of this module"""
        return VERSION

    def update(self):
        """Updates the ACPI state"""
        self.acpi.update()

    def percent(self):
        """Returns percentage capacity of all batteries"""
        return self.acpi.percent()

    def capacity(self):
        """Returns capacity of all batteries (in mWh)"""
        return self.acpi.capacity()

    def nb_of_batteries(self):
        """Returns the number of batteries"""
        return self.acpi.nb_of_batteries()

    def charging_state(self):
        """Returns ac state (off-/online/charging)"""
        return self.acpi.charging_state()

    def estimated_lifetime(self):
        """Returns Estimated Lifetime as real number"""
        return self.acpi.estimated_lifetime()

    def temperature(self, idx):
        """Returns Processor Temperature"""
        return self.acpi.temperature(idx)

    def fan_state(self, idx):
        """Returns fan states"""
        return self.acpi.fan_state(idx)


#unfinished: don't use it or better send us improvements ;-)
    def frequency(self, idx):
        """ Return  the frequency of the processor"""
        return self.acpi.frequency(idx)

    def performance_states(self, idx):
        """ Return a list of available frequencies for the proc """
        return self.acpi.performance_states(idx)

    def set_frequency(self, f):
        """ Set the processor frequency - Warning ! Needs root privileges to work """
        return self.acpi.set_frequency(f)



# implementation for Linux ####################################################

class AcpiLinux:
    def __init__(self):
        """init ACPI class and check for any ACPI features in /proc/acpi/"""

        #we read all acpi stuff from here
        dirs = ['/proc/acpi/ibm', '/proc/acpi']
        for dir in dirs:
            if os.path.exists(dir):
                self.proc_acpi_dir = dir
                break

        self.init_batteries()
        self.init_fans()
        #self.init_processors()
        self.init_temperatures()

        self.update()


    def update(self):
        """Read current states of supported acpi components"""

        self.update_batteries()
        self.update_fans()
        #self.update_processors()
        self.update_temperatures()

    # battery related functions
    def init_batteries(self):
        """Checks for and initializes the batteries"""

        self.proc_battery_dir = self.proc_acpi_dir + "/battery"

                # empty lists implies no battery, no capacity etc.
        self.design_capacity = {}
        self.life_capacity = {}
        self.present_rate = {}

        # empty list of battery sub directories; implies no batteries available
        self.battery_dir_entries = []

        try:
            battery_dir_entries = os.listdir(self.proc_battery_dir)
        except OSError:
            self.ac_line_state = ONLINE  # no batteries: we assume that a cable is plugged in ;-)
            return   #nothing more to do


        try:
            for i in battery_dir_entries:
                mode = os.stat(self.proc_battery_dir + "/" + i)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    self.battery_dir_entries.append(i)
        except OSError:
            # the battery module is not correctly loaded, or is broken.
            # currently self.battery_dir_entries has no batteries or only
            # the batteries which we could stat
            # because the appended dirs should be okay we do not return here
            pass

        self.ac_line_state = OFFLINE

#later: the newer acpi versions seems to generate always two BAT dirs...
#check info for present: no
        try:
            for i in self.battery_dir_entries:
                #print self.proc_battery_dir + "/" + i + "/info"
                info_file = open(self.proc_battery_dir + "/" + i + "/info")
                line = info_file.readline()

                while len(line) != 0:
                    if line.find("last full capacity:") == 0:
                        cap = line.split(":")[1].strip()
                        try:
                            self.design_capacity[i] = int(cap.split("m")[0].strip())
                        except ValueError:
                            #no value --> conversion to int failed
                            self.design_capacity[i] = 0

                    line = info_file.readline()
                info_file.close()
        except IOError:
            #print "No batt info found."
            # the battery module is not correctly loaded... the file info should exist.
            # wipe out all lists --> no battery infos
            self.battery_dir_entries = []
            self.design_capacity = {}
            self.life_capacity = {}
            self.present_rate = {}


    def update_batteries(self):
        """Read current state of batteries"""

        try:
            for i in self.battery_dir_entries:
                state_file = open(self.proc_battery_dir + "/" + i + "/state")
                line = state_file.readline()

                while len(line) != 0:
                    if line.find("remaining capacity") == 0:
                        cap = line.split(":")[1].strip()
                        try:
                            self.life_capacity[i] = int(cap.split("m")[0].strip())
                        except ValueError:
                            self.life_capacity[i] = 0

# it's possible that in battery/*/info the charging state is unknown
# --> then we must check ac_state...
# iterating over all batteries this way is not smart. better implementation needed
# better are funcs for capacity, acstate and prrate

                    # a little bit tricky... if loading of ac driver fails, we cant use info
                    # from /proc/ac_*/...
                    # if information in /proc/acpi/battery/*/state is wrong we had to
                    # track the capacity history.
                    # I assume that all battery state files get the same state.
                    if line.find("charging state") == 0:
                        state = line.split(":")[1].strip()
                        if state == "discharging":
                            self.ac_line_state = OFFLINE
                        elif state == "charging":
                            self.ac_line_state = CHARGING
                        else:
                            self.ac_line_state = ONLINE

                    # Read the present energy consumption to
                    # estimate life time

                    if line.find("present rate:") == 0:
                        try:
                            pr_rate = float(line.split(":")[1].strip().split("m")[0].strip())
                        except ValueError:
                            pr_rate = 0

                        self.present_rate[i] = pr_rate

                    line = state_file.readline()
                state_file.close()
        except IOError:
            raise AcpiError, ERR_CONFIGURATION_CHANGED

            # maybe we should restart init_batteries instead of generating an error ?
            # the user may have unplugged the battery.
            #init_batteries()
            # I prefer raising an exception because we would run into a recursion of
            # member funcs what is not a good idea.
            # the case that this error occurs should be very rare


    def init_temperatures(self):
        """Initializes temperature stuff"""

        self.proc_thermal_dir = self.proc_acpi_dir

        # empty list implies no thermal feature supported
        self.temperatures = {}

        # empty list of thermal sub directories; implies no thermal infos available
        self.thermal_dir_entries = []

        try:
            thermal_dir_entries = os.listdir(self.proc_thermal_dir)
            #thermal_dir_entries.append('')
        except OSError:
            return   #nothing more to do

        try:
            for i in thermal_dir_entries:
                if i == 'thermal':
                    self.thermal_dir_entries.append(i)
        except OSError:
            # the thermal module is not correctly loaded, or is broken.
            # because the appended dirs should be okay we do not return here
            pass


    def update_temperatures(self):
        """Read current temperatures"""

        try:
            for i in self.thermal_dir_entries:
                file = open(self.proc_thermal_dir + "/" + i)
                line = file.readline()
                while len(line) != 0:
                    if line.find("temperature") == 0:
                        self.temperatures[i] = line.split(":")[1].strip().split(' ')[0]
                    line = file.readline()
                file.close()
        except IOError:
            raise AcpiError,ERR_CONFIGURATION_CHANGED


    def init_fans(self):
        """Initialize fans"""

        self.proc_fan_dir = self.proc_acpi_dir + "/fan"

        self.fans = {}

        # empty list of fan sub directories; implies no fan infos available
        self.fan_dir_entries = []

        try:
            fan_dir_entries = os.listdir(self.proc_fan_dir)
        except OSError:
            return   #nothing more to do

        try:
            for i in fan_dir_entries:
                mode = os.stat(self.proc_fan_dir + "/" + i)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    self.fan_dir_entries.append(i)
        except OSError:
            # the fan module is not correctly loaded, or is broken.
            # because the appended dirs should be okay we do not return here
            pass


    def update_fans(self):
        """Read current state of fans"""

        try:
            for i in self.fan_dir_entries:
                file = open(self.proc_fan_dir + "/" + i + "/state")
                line = file.readline()
                while len(line) != 0:
                    if line.find("status") == 0:
                        if line.split(":")[1].strip() == 'on':
                            self.fans[i] = FAN_ON
                        else:
                            self.fans[i] = FAN_OFF
                    line = file.readline()
                file.close()
        except IOError:
            raise AcpiError,ERR_CONFIGURATION_CHANGED


    def init_processors(self):
        """Initialize processors"""

        self.proc_processor_dir = self.proc_acpi_dir + "/processor"

# TODO: adapt it for multiple CPUs --> we need a matrix instead of a vector!!!
        self.perf_states = {}   #empty list implies no processor support

        # empty list of processor sub directories; implies no processor infos available
        self.processor_dir_entries = []

        try:
            processor_dir_entries = os.listdir(self.proc_processor_dir)
        except OSError:
            return   #nothing more to do

        try:
            for i in processor_dir_entries:
                mode = os.stat(self.proc_processor_dir + "/" + i)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    self.processor_dir_entries.append(i)
        except OSError:
            # the processor module is not correctly loaded, or is broken.
            # because the appended dirs should be okay we do not return here
            pass

        try:
            for i in self.processor_dir_entries:
                file = open(self.proc_processor_dir + "/" + i + "/performance")
                line = file.readline()
                while(len(line)!=0):
                    if line.find("MHz") > -1:
                        state = line.split(":")[0].strip().split("P")[-1]
                        freq = line.split(":")[1].split(",")[0].strip()
                        self.perf_states[freq] = state
                    line = file.readline()
                file.close()
        except IOError:
            self.processor_dir_entries = []
            self.perf_states = {}   #reset list --> should we throw an exception? No!
            return


    def update_processors(self):
        """Read current state of processors"""

        try:
            for i in self.processor_dir_entries:
                file = open(self.proc_processor_dir + "/" + i + "/performance")
                line = file.readline()

                while(len(line)!=0):
                    if line.find("*") > -1:
                        self.freq = line.split(":")[1].strip().split(",")[0]
                    line = f.readline()
                file.close()
        except IOError:
            raise AcpiError,ERR_CONFIGURATION_CHANGED


    def percent(self):
        """Returns percentage capacity of all batteries"""

        life_capacity = 0
        design_capacity = 0
        for i,c in self.life_capacity.items():
            life_capacity = life_capacity + c
            design_capacity = design_capacity + self.design_capacity[i]

        if design_capacity == 0:
            return 0

        # should we use try catch instead of the check above?
        return (life_capacity * 100) / design_capacity


    def capacity(self):
        """Returns capacity of all batteries"""
        capacity = 0
        for i,c in self.life_capacity.items():
            capacity = capacity + c
        return capacity


    def nb_of_batteries(self):
        #returns the number of batteries
        #if it returns 0, maybe ACPI is not available or
        #battery driver is not loaded
        return len(self.battery_dir_entries)


    def charging_state(self):
        return self.ac_line_state


    def estimated_lifetime(self):

        # what should we return if state==charging?
        # it's not clean to return a time in one case and any
        # English string in another case.
        # The user can check for ac-state before call this func
        time = 0
        for batt,life_capacity in self.life_capacity.items():
            if self.present_rate[batt] > 0:
                time = time + life_capacity/self.present_rate[batt]
        return time


    # we need funcs like max_temperature and average_temperature
    def temperature(self, idx):
        #print self.temperatures
        #print self.thermal_dir_entries[idx]
        return self.temperatures[self.thermal_dir_entries[idx]]


    def fan_state(self, idx):
        #print self.fans
        return self.fans[self.fan_dir_entries[idx]]


    def performance_states(self, idx):
        return self.perf_states[idx].keys()


    def frequency(self, idx):
        #print self.freq
        return self.freq[idx]


# TODO: adapt it for multiple CPUs
    def set_frequency(self, f):
    #I think we should throw exceptions if someone goes wrong here

        if self.perf_states.has_key(f):
            state = self.perf_states[f]
            try:
                pr = os.listdir("/proc/acpi/processor")[0]
            except OSError:
                raise AcpiError, ERR_NOT_ALLOWED

            try:
                f = open("/proc/acpi/processor/"+pr+"/performance","w")
            except IOError:
                raise AcpiError, ERR_NOT_ALLOWED

            f.write(state)
            f.close()
        else:
            raise AcpiError, ERR_NOT_ALLOWED
