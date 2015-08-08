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
This module contains the song book form
"""

from PyQt4 import QtGui

from openlp.core.lib import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.forms.songbookdialog import Ui_SongBookDialog


class SongBookForm(QtGui.QDialog, Ui_SongBookDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(SongBookForm, self).__init__(parent)
        self.setupUi(self)

    def exec_(self, clear=True):
        """
        Execute the song book form.

        :param clear: Clear the fields on the form before displaying it.
        """
        if clear:
            self.name_edit.clear()
            self.publisher_edit.clear()
        self.name_edit.setFocus()
        return QtGui.QDialog.exec_(self)

    def accept(self):
        """
        Override the inherited method to check that the name of the book has been typed in.
        """
        if not self.name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.SongBookForm', 'You need to type in a name for the book.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtGui.QDialog.accept(self)
