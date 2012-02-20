#!/usr/bin/python
# *-* coding: utf-8 *-*
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

from django.conf.urls.defaults import *
from django.conf import settings
from telecaster.models import *
from telecaster.views import WebView
from jsonrpc import jsonrpc_site
import os.path


# initialization
web_view = WebView(settings.TELECASTER_CONF)
htdocs = os.path.dirname(__file__) + '/htdocs'

urlpatterns = patterns('',
    url(r'^$', web_view.index, name="telecaster-index"),
    url(r'^record/$', web_view.record, name="telecaster-record"),
    url(r'^items/(?P<id>.*)$', web_view.index, name="telecaster-item"),

    # CSS+Images (FIXME: for developement only)
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': htdocs+'/css'}, name="telecaster-css"),
    url(r'images/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': htdocs+'/images'}, name="telecaster-images"),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': htdocs+'/js'}, name="telecaster-js"),

    # JSON RPC
    url(r'json/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
#    url(r'^items/json/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint2'),
    # for the graphical browser/web console only, omissible
#    url(r'json/browse/', 'jsonrpc.views.browse', name="jsonrpc_browser"),

)
