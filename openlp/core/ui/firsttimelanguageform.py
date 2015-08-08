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
The language selection dialog.
"""
from PyQt4 import QtGui

from openlp.core.lib.ui import create_action
from openlp.core.utils import LanguageManager
from .firsttimelanguagedialog import Ui_FirstTimeLanguageDialog


class FirstTimeLanguageForm(QtGui.QDialog, Ui_FirstTimeLanguageDialog):
    """
    The language selection dialog.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(FirstTimeLanguageForm, self).__init__(parent)
        self.setupUi(self)
        self.qm_list = LanguageManager.get_qm_list()
        self.language_combo_box.addItem('Autodetect')
        self.language_combo_box.addItems(sorted(self.qm_list.keys()))

    def exec_(self):
        """
        Run the Dialog with correct heading.
        """
        return QtGui.QDialog.exec_(self)

    def accept(self):
        """
        Run when the dialog is OKed.
        """
        # It's the first row so must be Automatic
        if self.language_combo_box.currentIndex() == 0:
            LanguageManager.auto_language = True
            LanguageManager.set_language(False, False)
        else:
            LanguageManager.auto_language = False
            action = create_action(None, self.language_combo_box.currentText())
            LanguageManager.set_language(action, False)
        return QtGui.QDialog.accept(self)

    def reject(self):
        """
        Run when the dialog is canceled.
        """
        LanguageManager.auto_language = True
        LanguageManager.set_language(False, False)
        return QtGui.QDialog.reject(self)
