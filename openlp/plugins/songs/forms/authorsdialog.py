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


class Ui_AuthorsDialog(object):
    """
    The :class:`~openlp.plugins.songs.forms.authorsdialog.Ui_AuthorsDialog` class defines the user interface for the
    AuthorsForm dialog.
    """
    def setupUi(self, authors_dialog):
        """
        Set up the UI for the dialog.
        """
        authors_dialog.setObjectName('authors_dialog')
        authors_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        authors_dialog.resize(300, 10)
        authors_dialog.setModal(True)
        self.dialog_layout = QtGui.QVBoxLayout(authors_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.author_layout = QtGui.QFormLayout()
        self.author_layout.setObjectName('author_layout')
        self.first_name_label = QtGui.QLabel(authors_dialog)
        self.first_name_label.setObjectName('first_name_label')
        self.first_name_edit = QtGui.QLineEdit(authors_dialog)
        self.first_name_edit.setObjectName('first_name_edit')
        self.first_name_label.setBuddy(self.first_name_edit)
        self.author_layout.addRow(self.first_name_label, self.first_name_edit)
        self.last_name_label = QtGui.QLabel(authors_dialog)
        self.last_name_label.setObjectName('last_name_label')
        self.last_name_edit = QtGui.QLineEdit(authors_dialog)
        self.last_name_edit.setObjectName('last_name_edit')
        self.last_name_label.setBuddy(self.last_name_edit)
        self.author_layout.addRow(self.last_name_label, self.last_name_edit)
        self.display_label = QtGui.QLabel(authors_dialog)
        self.display_label.setObjectName('display_label')
        self.display_edit = QtGui.QLineEdit(authors_dialog)
        self.display_edit.setObjectName('display_edit')
        self.display_label.setBuddy(self.display_edit)
        self.author_layout.addRow(self.display_label, self.display_edit)
        self.dialog_layout.addLayout(self.author_layout)
        self.button_box = create_button_box(authors_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(authors_dialog)
        authors_dialog.setMaximumHeight(authors_dialog.sizeHint().height())

    def retranslateUi(self, authors_dialog):
        """
        Translate the UI on the fly.
        """
        authors_dialog.setWindowTitle(translate('SongsPlugin.AuthorsForm', 'Author Maintenance'))
        self.display_label.setText(translate('SongsPlugin.AuthorsForm', 'Display name:'))
        self.first_name_label.setText(translate('SongsPlugin.AuthorsForm', 'First name:'))
        self.last_name_label.setText(translate('SongsPlugin.AuthorsForm', 'Last name:'))
