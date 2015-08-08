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
The :mod:`~openlp.core.ui.servicenoteform` module contains the `ServiceNoteForm` class.
"""
from PyQt4 import QtGui

from openlp.core.common import Registry, RegistryProperties, translate
from openlp.core.lib import SpellTextEdit
from openlp.core.lib.ui import create_button_box


class ServiceNoteForm(QtGui.QDialog, RegistryProperties):
    """
    This is the form that is used to edit the verses of the song.
    """
    def __init__(self):
        """
        Constructor
        """
        super(ServiceNoteForm, self).__init__(Registry().get('main_window'))
        self.setupUi()
        self.retranslateUi()

    def exec_(self):
        """
        Execute the form and return the result.
        """
        self.text_edit.setFocus()
        return QtGui.QDialog.exec_(self)

    def setupUi(self):
        """
        Set up the UI of the dialog
        """
        self.setObjectName('serviceNoteEdit')
        self.dialog_layout = QtGui.QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setObjectName('vertical_layout')
        self.text_edit = SpellTextEdit(self, False)
        self.text_edit.setObjectName('textEdit')
        self.dialog_layout.addWidget(self.text_edit)
        self.button_box = create_button_box(self, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.setWindowTitle(translate('OpenLP.ServiceNoteForm', 'Service Item Notes'))
