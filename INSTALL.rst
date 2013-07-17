==================
INSTALL TeleCaster
==================


1. Operating System
===================

TeleCaster now only works on GNU/Linux systems. The installer and the following instructions
are based on Debian like software management so that it should work on Debian (>= Lenny)
or Ubuntu / Kubuntu (>= 10.4). So please install one of these OS before.


2. Install dependencies
=======================

Needed::

    sudo aptitude update

    sudo aptitude install python python-dev python-xml python-libxml2 python-setuptools python-twitter python-liblo python-mutagen \
                        icecast2 apache2 apache2-suexec jackd libjack-dev vorbis-tools procps meterbridge fluxbox \
                        vnc4server vncviewer swh-plugins jack-rack libshout3 libshout3-dev libmad0-dev libogg-dev g++ python-yaml

Warning: on Debian Squeeze or recent Ubuntu, change libjack-dev to libjack-jackd2-dev

Note that obtaining and installing a preempt RT kernel is STRONGLY advised to get a good audio (JACK) stability.
Moreover, edit the pam conf file to get RT "su" pam limits at boot::

    sudo vi /etc/pam.d/su

Uncomment::

    session    required   pam_limits.so


3. Install TeleCaster
=====================

Untar the archive. For example::

    tar xzf telecaster-0.5.tar.gz

Run the install script::

    cd telecaster-0.5/
    sudo python install.py


4. Configuration
================

Edit the following files to setup TeleCaster. Please be careful with the XML syntax::

    /etc/telecaster/telecaster.xml

and, ONLY if needed::

    /etc/default/jackd
    /etc/default/vncserver


5. Start audio deamons
======================

Just reboot your machine or start the deamons manually::

    sudo /etc/init.d/jackd start
    sudo /etc/init.d/vncserver start


6. Configure Apache2
====================

Configure your apache VirtualHost editing /etc/apache2/sites-available/telecaster.conf

Enable the VirtualHost::

    sudo a2ensite telecaster.conf

Maybe remove the default VirtualHost::

    sudo rm /etc/apache2/sites-enabled/000-default

Reload Apache::

    sudo /etc/init.d/apache2 reload


7. Usage
========

Browse the TeleCaster web control page:

    http://localhost/telecaster/telecaster.py

Fill in the form and start any free recording and broadcasting stream !

To change the form options, just edit the conf file as root::

    sudo vi /etc/telecaster/telecaster.xml


8. Contact
==========

Any questions, suggestions ? Please post a ticket on the dev platform:

    http://svn.parisson.org/telecaster

or contact the main developer:

    Guillaume Pellerin <yomguy@parisson.com>
