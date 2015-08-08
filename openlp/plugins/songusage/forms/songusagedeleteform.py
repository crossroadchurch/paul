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

from PyQt4 import QtGui

from openlp.core.common import RegistryProperties, translate
from openlp.plugins.songusage.lib.db import SongUsageItem
from .songusagedeletedialog import Ui_SongUsageDeleteDialog


class SongUsageDeleteForm(QtGui.QDialog, Ui_SongUsageDeleteDialog, RegistryProperties):
    """
    Class documentation goes here.
    """
    def __init__(self, manager, parent):
        """
        Constructor
        """
        self.manager = manager
        super(SongUsageDeleteForm, self).__init__(parent)
        self.setupUi(self)
        self.button_box.clicked.connect(self.on_button_box_clicked)

    def on_button_box_clicked(self, button):
        """
        The button event has been triggered

        :param button: The button pressed
        """
        if self.button_box.standardButton(button) == QtGui.QDialogButtonBox.Ok:
            ret = QtGui.QMessageBox.question(
                self,
                translate('SongUsagePlugin.SongUsageDeleteForm', 'Delete Selected Song Usage Events?'),
                translate('SongUsagePlugin.SongUsageDeleteForm',
                          'Are you sure you want to delete selected Song Usage data?'),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No), QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.Yes:
                delete_date = self.delete_calendar.selectedDate().toPyDate()
                self.manager.delete_all_objects(SongUsageItem, SongUsageItem.usagedate <= delete_date)
                self.main_window.information_message(
                    translate('SongUsagePlugin.SongUsageDeleteForm', 'Deletion Successful'),
                    translate('SongUsagePlugin.SongUsageDeleteForm',
                              'All requested data has been deleted successfully.')
                )
                self.accept()
        else:
            self.reject()
