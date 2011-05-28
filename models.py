#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
   telecaster

   Copyright (c) 2006-2011 Guillaume Pellerin <yomguy@parisson.com>

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

from django.db.models import *

app_label = 'telecaster'

class Organization(Model):
    
    name            = CharField(_('name'))
    description     = CharField(_('description'))
    
    class Meta:
        db_table = app_label + '_' + 'organization'

class Department(Model):
    
    name            = CharField(_('name'))
    description     = CharField(_('description'))

    class Meta:
        db_table = app_label + '_' + 'department'


class Conference(Model):
    
    title           = CharField(_('title'))
    description     = CharField(_('description'))
    department      = Foreignkey('Department', related_name='conferences', verbose_name='department')

    class Meta:
        db_table = app_label + '_' + 'conference'


class Session(Model):
    
    name            = CharField(_('name'))
    description     = CharField(_('description'))
    number          = IntegerField(_('number'))

    class Meta:
        db_table = app_label + '_' + 'session'


class Professor(Model):
    
    name            = CharField(_('name'))
    institution     = CharField(_('institution'))
    address         = CharField(_('address'))
    telephone       = CharField(_('telephone'))
    email           = CharField(_('email'))

    class Meta:
        db_table = app_label + '_' + 'professor'
    
    
class Station(Model):
    
    organization      = Foreignkey('Organization', related_name='stations', verbose_name='organization')
    conference        = Foreignkey('Conference', related_name='stations', verbose_name='conference')
    session           = Foreignkey('Session', related_name='stations', verbose_name='session')
    professor         = Foreignkey('Professor', related_name='stations', verbose_name='professor')
    comment           = TextField(_('comment'))
    started           = BooleanField(_('started'))
    datetime_start    = DateTimeField(_('datetime_start'), auto_now_add=True)
    datetime_stop     = DateTimeField(_('datetime_stop'))

    class Meta:
        db_table = app_label + '_' + 'station'
    
    
