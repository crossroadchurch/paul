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
Module implementing LanguageForm.
"""
import logging

from PyQt4.QtGui import QDialog

from openlp.core.common import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.forms.languagedialog import Ui_LanguageDialog
from openlp.plugins.bibles.lib.db import BiblesResourcesDB


log = logging.getLogger(__name__)


class LanguageForm(QDialog, Ui_LanguageDialog):
    """
    Class to manage a dialog which ask the user for a language.
    """
    log.info('LanguageForm loaded')

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(LanguageForm, self).__init__(parent)
        self.setupUi(self)

    def exec_(self, bible_name):
        self.language_combo_box.addItem('')
        if bible_name:
            self.bible_label.setText(str(bible_name))
        items = BiblesResourcesDB.get_languages()
        self.language_combo_box.addItems([item['name'] for item in items])
        return QDialog.exec_(self)

    def accept(self):
        if not self.language_combo_box.currentText():
            critical_error_message_box(message=translate('BiblesPlugin.LanguageForm', 'You need to choose a language.'))
            self.language_combo_box.setFocus()
            return False
        else:
            return QDialog.accept(self)
