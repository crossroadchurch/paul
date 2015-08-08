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
Provide Error Handling and login Services
"""
import logging
import inspect

from openlp.core.common import trace_error_handler

DO_NOT_TRACE_EVENTS = ['timerEvent', 'paintEvent', 'drag_enter_event', 'drop_event', 'on_controller_size_changed',
                       'preview_size_changed', 'resizeEvent']


class OpenLPMixin(object):
    """
    Base Calling object for OpenLP classes.
    """
    def __init__(self, *args, **kwargs):
        super(OpenLPMixin, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))
        if self.logger.getEffectiveLevel() == logging.DEBUG:
            for name, m in inspect.getmembers(self, inspect.ismethod):
                if name not in DO_NOT_TRACE_EVENTS:
                    if not name.startswith("_") and not name.startswith("log"):
                        setattr(self, name, self.logging_wrapper(m, self))

    def logging_wrapper(self, func, parent):
        """
        Code to added debug wrapper to work on called functions within a decorated class.
        """
        def wrapped(*args, **kwargs):
            parent.logger.debug("Entering %s" % func.__name__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if parent.logger.getEffectiveLevel() <= logging.ERROR:
                    parent.logger.error('Exception in %s : %s' % (func.__name__, e))
                raise e
        return wrapped

    def log_debug(self, message):
        """
        Common log debug handler
        """
        self.logger.debug(message)

    def log_info(self, message):
        """
        Common log info handler
        """
        self.logger.info(message)

    def log_error(self, message):
        """
        Common log error handler which prints the calling path
        """
        trace_error_handler(self.logger)
        self.logger.error(message)

    def log_exception(self, message):
        """
        Common log exception handler which prints the calling path
        """
        trace_error_handler(self.logger)
        self.logger.exception(message)
