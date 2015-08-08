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

import logging
import os

from PyQt4 import QtGui
from sqlalchemy.sql import and_

from openlp.core.common import RegistryProperties, Settings, check_directory_exists, translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songusage.lib.db import SongUsageItem
from .songusagedetaildialog import Ui_SongUsageDetailDialog

log = logging.getLogger(__name__)


class SongUsageDetailForm(QtGui.QDialog, Ui_SongUsageDetailDialog, RegistryProperties):
    """
    Class documentation goes here.
    """
    log.info('SongUsage Detail Form Loaded')

    def __init__(self, plugin, parent):
        """
        Initialise the form
        """
        super(SongUsageDetailForm, self).__init__(parent)
        self.plugin = plugin
        self.setupUi(self)

    def initialise(self):
        """
        We need to set up the screen
        """
        self.from_date_calendar.setSelectedDate(Settings().value(self.plugin.settings_section + '/from date'))
        self.to_date_calendar.setSelectedDate(Settings().value(self.plugin.settings_section + '/to date'))
        self.file_line_edit.setText(Settings().value(self.plugin.settings_section + '/last directory export'))

    def define_output_location(self):
        """
        Triggered when the Directory selection button is clicked
        """
        path = QtGui.QFileDialog.getExistingDirectory(
            self, translate('SongUsagePlugin.SongUsageDetailForm', 'Output File Location'),
            Settings().value(self.plugin.settings_section + '/last directory export'))
        if path:
            Settings().setValue(self.plugin.settings_section + '/last directory export', path)
            self.file_line_edit.setText(path)

    def accept(self):
        """
        Ok was triggered so lets save the data and run the report
        """
        log.debug('accept')
        path = self.file_line_edit.text()
        if not path:
            self.main_window.error_message(
                translate('SongUsagePlugin.SongUsageDetailForm', 'Output Path Not Selected'),
                translate('SongUsagePlugin.SongUsageDetailForm', 'You have not set a valid output location for your'
                          ' song usage report. \nPlease select an existing path on your computer.')
            )
            return
        check_directory_exists(path)
        file_name = translate('SongUsagePlugin.SongUsageDetailForm', 'usage_detail_%s_%s.txt') % \
            (self.from_date_calendar.selectedDate().toString('ddMMyyyy'),
             self.to_date_calendar.selectedDate().toString('ddMMyyyy'))
        Settings().setValue(self.plugin.settings_section + '/from date', self.from_date_calendar.selectedDate())
        Settings().setValue(self.plugin.settings_section + '/to date', self.to_date_calendar.selectedDate())
        usage = self.plugin.manager.get_all_objects(
            SongUsageItem, and_(SongUsageItem.usagedate >= self.from_date_calendar.selectedDate().toPyDate(),
                                SongUsageItem.usagedate < self.to_date_calendar.selectedDate().toPyDate()),
            [SongUsageItem.usagedate, SongUsageItem.usagetime])
        report_file_name = os.path.join(path, file_name)
        file_handle = None
        try:
            file_handle = open(report_file_name, 'wb')
            for instance in usage:
                record = '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",' \
                    '\"%s\",\"%s\"\n' % \
                         (instance.usagedate, instance.usagetime, instance.title, instance.copyright,
                          instance.ccl_number, instance.authors, instance.plugin_name, instance.source)
                file_handle.write(record.encode('utf-8'))
            self.main_window.information_message(
                translate('SongUsagePlugin.SongUsageDetailForm', 'Report Creation'),
                translate('SongUsagePlugin.SongUsageDetailForm',
                          'Report \n%s \nhas been successfully created. ') % report_file_name
            )
        except OSError as ose:
            log.exception('Failed to write out song usage records')
            critical_error_message_box(translate('SongUsagePlugin.SongUsageDetailForm', 'Report Creation Failed'),
                                       translate('SongUsagePlugin.SongUsageDetailForm',
                                                 'An error occurred while creating the report: %s') % ose.strerror)
        finally:
            if file_handle:
                file_handle.close()
        self.close()
