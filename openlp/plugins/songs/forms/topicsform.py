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
This module contains the topic edit form.
"""

from PyQt4 import QtGui

from openlp.core.lib import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.forms.topicsdialog import Ui_TopicsDialog


class TopicsForm(QtGui.QDialog, Ui_TopicsDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TopicsForm, self).__init__(parent)
        self.setupUi(self)

    def exec_(self, clear=True):
        """
        Execute the dialog.
        """
        if clear:
            self.name_edit.clear()
        self.name_edit.setFocus()
        return QtGui.QDialog.exec_(self)

    def accept(self):
        """
        Override the inherited method to check before we close.
        """
        if not self.name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.TopicsForm', 'You need to type in a topic name.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtGui.QDialog.accept(self)

    def _get_name(self):
        """
        Return the name of the topic.
        """
        return self.name_edit.text()

    def _set_name(self, value):
        """
        Set the topic name.
        """
        self.name_edit.setText(value)

    name = property(_get_name, _set_name)
