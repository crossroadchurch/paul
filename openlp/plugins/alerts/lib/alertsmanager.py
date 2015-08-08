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
The :mod:`~openlp.plugins.alerts.lib.alertsmanager` module contains the part of the plugin which manages storing and
displaying of alerts.
"""

from PyQt4 import QtCore

from openlp.core.common import OpenLPMixin, RegistryMixin, Registry, RegistryProperties, Settings, translate


class AlertsManager(OpenLPMixin, RegistryMixin, QtCore.QObject, RegistryProperties):
    """
    AlertsManager manages the settings of Alerts.
    """
    def __init__(self, parent):
        super(AlertsManager, self).__init__(parent)
        self.timer_id = 0
        self.alert_list = []
        Registry().register_function('live_display_active', self.generate_alert)
        Registry().register_function('alerts_text', self.alert_text)
        QtCore.QObject.connect(self, QtCore.SIGNAL('alerts_text'), self.alert_text)

    def alert_text(self, message):
        """
        Called via a alerts_text event. Message is single element array containing text.

        :param message: The message text to be displayed
        """
        if message:
            self.display_alert(message[0])

    def display_alert(self, text=''):
        """
        Called from the Alert Tab to display an alert.

        :param text: The text to display
        """
        self.log_debug('display alert called %s' % text)
        if text:
            self.alert_list.append(text)
            if self.timer_id != 0:
                self.main_window.show_status_message(
                    translate('AlertsPlugin.AlertsManager', 'Alert message created and displayed.'))
                return
            self.main_window.show_status_message('')
            self.generate_alert()

    def generate_alert(self):
        """
        Format and request the Alert and start the timer.
        """
        if not self.alert_list or (self.live_controller.display.screens.display_count == 1 and
                                   not Settings().value('core/display on monitor')):
            return
        text = self.alert_list.pop(0)
        alert_tab = self.parent().settings_tab
        self.live_controller.display.alert(text, alert_tab.location)
        # Check to see if we have a timer running.
        if self.timer_id == 0:
            self.timer_id = self.startTimer(int(alert_tab.timeout) * 1000)

    def timerEvent(self, event):
        """
        Time has finished so if our time then request the next Alert if there is one and reset the timer.

        :param event: the QT event that has been triggered.
        """
        if event.timerId() == self.timer_id:
            alert_tab = self.parent().settings_tab
            self.live_controller.display.alert('', alert_tab.location)
        self.killTimer(self.timer_id)
        self.timer_id = 0
        self.generate_alert()
