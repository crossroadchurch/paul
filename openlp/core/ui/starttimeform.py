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
The actual start time form.
"""
from PyQt4 import QtGui

from .starttimedialog import Ui_StartTimeDialog

from openlp.core.common import Registry, RegistryProperties, UiStrings, translate
from openlp.core.lib.ui import critical_error_message_box


class StartTimeForm(QtGui.QDialog, Ui_StartTimeDialog, RegistryProperties):
    """
    The start time dialog
    """
    def __init__(self):
        """
        Constructor
        """
        super(StartTimeForm, self).__init__(Registry().get('main_window'))
        self.setupUi(self)

    def exec_(self):
        """
        Run the Dialog with correct heading.
        """
        hour, minutes, seconds = self._time_split(self.item['service_item'].start_time)
        self.hour_spin_box.setValue(hour)
        self.minute_spin_box.setValue(minutes)
        self.second_spin_box.setValue(seconds)
        hours, minutes, seconds = self._time_split(self.item['service_item'].end_time)
        if hours == 0 and minutes == 0 and seconds == 0:
            hours, minutes, seconds = self._time_split(self.item['service_item'].media_length)
        self.hour_finish_spin_box.setValue(hours)
        self.minute_finish_spin_box.setValue(minutes)
        self.second_finish_spin_box.setValue(seconds)
        self.hour_finish_label.setText('%s%s' % (str(hour), UiStrings().Hours))
        self.minute_finish_label.setText('%s%s' % (str(minutes), UiStrings().Minutes))
        self.second_finish_label.setText('%s%s' % (str(seconds), UiStrings().Seconds))
        return QtGui.QDialog.exec_(self)

    def accept(self):
        """
        When the dialog succeeds, this is run
        """
        start = self.hour_spin_box.value() * 3600 + self.minute_spin_box.value() * 60 + self.second_spin_box.value()
        end = self.hour_finish_spin_box.value() * 3600 + \
            self.minute_finish_spin_box.value() * 60 + self.second_finish_spin_box.value()
        if end > self.item['service_item'].media_length:
            critical_error_message_box(title=translate('OpenLP.StartTime_form', 'Time Validation Error'),
                                       message=translate('OpenLP.StartTime_form',
                                                         'Finish time is set after the end of the media item'))
            return
        elif start > end:
            critical_error_message_box(title=translate('OpenLP.StartTime_form', 'Time Validation Error'),
                                       message=translate('OpenLP.StartTime_form',
                                                         'Start time is after the finish time of the media item'))
            return
        self.item['service_item'].start_time = start
        self.item['service_item'].end_time = end
        return QtGui.QDialog.accept(self)

    def _time_split(self, seconds):
        """
        Split time up into hours minutes and seconds from seconds
        """
        hours = seconds // 3600
        seconds -= 3600 * hours
        minutes = seconds // 60
        seconds -= 60 * minutes
        return hours, minutes, seconds
