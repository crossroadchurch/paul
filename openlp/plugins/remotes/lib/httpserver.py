# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

"""
The :mod:`http` module contains the API web server. This is a lightweight web server used by remotes to interact
with OpenLP. It uses JSON to communicate with the remotes.
"""

import ssl
import socket
import os
import logging
import time

from PyQt4 import QtCore

from openlp.core.common import AppLocation, Settings, RegistryProperties

from openlp.plugins.remotes.lib import HttpRouter

from socketserver import BaseServer, ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

log = logging.getLogger(__name__)


class CustomHandler(BaseHTTPRequestHandler, HttpRouter):
    """
    Stateless session handler to handle the HTTP request and process it.
    This class handles just the overrides to the base methods and the logic to invoke the methods within the HttpRouter
    class.
    DO not try change the structure as this is as per the documentation.
    """

    def do_POST(self):
        """
        Present pages / data and invoke URL level user authentication.
        """
        self.do_post_processor()

    def do_GET(self):
        """
        Present pages / data and invoke URL level user authentication.
        """
        self.do_post_processor()

    def do_OPTIONS(self):
        """
        Allow JSON OPTIONS requests
        """
        self.do_post_processor()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class HttpThread(QtCore.QThread):
    """
    A special Qt thread class to allow the HTTP server to run at the same time as the UI.
    """
    def __init__(self, server):
        """
        Constructor for the thread class.

        :param server: The http server class.
        """
        super(HttpThread, self).__init__(None)
        self.http_server = server

    def run(self):
        """
        Run the thread.
        """
        self.http_server.start_server()

    def stop(self):
        log.debug("stop called")
        self.http_server.stop = True


class OpenLPServer(RegistryProperties):
    def __init__(self):
        """
        Initialise the http server, and start the server of the correct type http / https
        """
        super(OpenLPServer, self).__init__()
        log.debug('Initialise OpenLP')
        self.settings_section = 'remotes'
        self.http_thread = HttpThread(self)
        self.http_thread.start()

    def start_server(self):
        """
        Start the correct server and save the handler
        """
        address = Settings().value(self.settings_section + '/ip address')
        self.address = address
        self.is_secure = Settings().value(self.settings_section + '/https enabled')
        self.needs_authentication = Settings().value(self.settings_section + '/authentication enabled')
        if self.is_secure:
            port = Settings().value(self.settings_section + '/https port')
            self.port = port
            self.start_server_instance(address, port, HTTPSServer)
        else:
            port = Settings().value(self.settings_section + '/port')
            self.port = port
            self.start_server_instance(address, port, ThreadingHTTPServer)
        if hasattr(self, 'httpd') and self.httpd:
            self.httpd.serve_forever()
        else:
            log.debug('Failed to start server')

    def start_server_instance(self, address, port, server_class):
        """
        Start the server

        :param address: The server address
        :param port: The run port
        :param server_class: the class to start
        """
        loop = 1
        while loop < 4:
            try:
                self.httpd = server_class((address, port), CustomHandler)
                log.debug("Server started for class %s %s %d" % (server_class, address, port))
                break
            except OSError:
                log.debug("failed to start http server thread state %d %s" %
                          (loop, self.http_thread.isRunning()))
                loop += 1
                time.sleep(0.1)
            except:
                log.error('Failed to start server ')
                loop += 1
                time.sleep(0.1)

    def stop_server(self):
        """
        Stop the server
        """
        if self.http_thread.isRunning():
            self.http_thread.stop()
        self.httpd = None
        log.debug('Stopped the server.')


class HTTPSServer(HTTPServer):
    def __init__(self, address, handler):
        """
        Initialise the secure handlers for the SSL server if required.s
        """
        BaseServer.__init__(self, address, handler)
        local_data = AppLocation.get_directory(AppLocation.DataDir)
        self.socket = ssl.SSLSocket(
            sock=socket.socket(self.address_family, self.socket_type),
            ssl_version=ssl.PROTOCOL_TLSv1,
            certfile=os.path.join(local_data, 'remotes', 'openlp.crt'),
            keyfile=os.path.join(local_data, 'remotes', 'openlp.key'),
            server_side=True)
        self.server_bind()
        self.server_activate()
