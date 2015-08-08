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

from openlp.core.lib import translate, build_icon
from openlp.core.lib.ui import create_button_box


class Ui_SongBookDialog(object):
    """
    The user interface for the song book dialog.
    """
    def setupUi(self, song_book_dialog):
        """
        Set up the user interface.
        """
        song_book_dialog.setObjectName('song_book_dialog')
        song_book_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        song_book_dialog.resize(300, 10)
        self.dialog_layout = QtGui.QVBoxLayout(song_book_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.book_layout = QtGui.QFormLayout()
        self.book_layout.setObjectName('book_layout')
        self.name_label = QtGui.QLabel(song_book_dialog)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtGui.QLineEdit(song_book_dialog)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.book_layout.addRow(self.name_label, self.name_edit)
        self.publisher_label = QtGui.QLabel(song_book_dialog)
        self.publisher_label.setObjectName('publisher_label')
        self.publisher_edit = QtGui.QLineEdit(song_book_dialog)
        self.publisher_edit.setObjectName('publisher_edit')
        self.publisher_label.setBuddy(self.publisher_edit)
        self.book_layout.addRow(self.publisher_label, self.publisher_edit)
        self.dialog_layout.addLayout(self.book_layout)
        self.button_box = create_button_box(song_book_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(song_book_dialog)
        song_book_dialog.setMaximumHeight(song_book_dialog.sizeHint().height())

    def retranslateUi(self, song_book_dialog):
        """
        Translate the UI on the fly.
        """
        song_book_dialog.setWindowTitle(translate('SongsPlugin.SongBookForm', 'Song Book Maintenance'))
        self.name_label.setText(translate('SongsPlugin.SongBookForm', '&Name:'))
        self.publisher_label.setText(translate('SongsPlugin.SongBookForm', '&Publisher:'))
