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

from PyQt4 import QtCore, QtGui

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_BookNameDialog(object):
    def setupUi(self, book_name_dialog):
        book_name_dialog.setObjectName('book_name_dialog')
        book_name_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        book_name_dialog.resize(400, 271)
        self.book_name_layout = QtGui.QVBoxLayout(book_name_dialog)
        self.book_name_layout.setSpacing(8)
        self.book_name_layout.setMargin(8)
        self.book_name_layout.setObjectName('book_name_layout')
        self.info_label = QtGui.QLabel(book_name_dialog)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('info_label')
        self.book_name_layout.addWidget(self.info_label)
        self.corresponding_layout = QtGui.QGridLayout()
        self.corresponding_layout.setColumnStretch(1, 1)
        self.corresponding_layout.setSpacing(8)
        self.corresponding_layout.setObjectName('corresponding_layout')
        self.current_label = QtGui.QLabel(book_name_dialog)
        self.current_label.setObjectName('current_label')
        self.corresponding_layout.addWidget(self.current_label, 0, 0, 1, 1)
        self.current_book_label = QtGui.QLabel(book_name_dialog)
        self.current_book_label.setObjectName('current_book_label')
        self.corresponding_layout.addWidget(self.current_book_label, 0, 1, 1, 1)
        self.corresponding_label = QtGui.QLabel(book_name_dialog)
        self.corresponding_label.setObjectName('corresponding_label')
        self.corresponding_layout.addWidget(self.corresponding_label, 1, 0, 1, 1)
        self.corresponding_combo_box = QtGui.QComboBox(book_name_dialog)
        self.corresponding_combo_box.setObjectName('corresponding_combo_box')
        self.corresponding_layout.addWidget(self.corresponding_combo_box, 1, 1, 1, 1)
        self.book_name_layout.addLayout(self.corresponding_layout)
        self.options_group_box = QtGui.QGroupBox(book_name_dialog)
        self.options_group_box.setObjectName('options_group_box')
        self.options_layout = QtGui.QVBoxLayout(self.options_group_box)
        self.options_layout.setSpacing(8)
        self.options_layout.setMargin(8)
        self.options_layout.setObjectName('options_layout')
        self.old_testament_check_box = QtGui.QCheckBox(self.options_group_box)
        self.old_testament_check_box.setObjectName('old_testament_check_box')
        self.old_testament_check_box.setCheckState(QtCore.Qt.Checked)
        self.options_layout.addWidget(self.old_testament_check_box)
        self.new_testament_check_box = QtGui.QCheckBox(self.options_group_box)
        self.new_testament_check_box.setObjectName('new_testament_check_box')
        self.new_testament_check_box.setCheckState(QtCore.Qt.Checked)
        self.options_layout.addWidget(self.new_testament_check_box)
        self.apocrypha_check_box = QtGui.QCheckBox(self.options_group_box)
        self.apocrypha_check_box.setObjectName('apocrypha_check_box')
        self.apocrypha_check_box.setCheckState(QtCore.Qt.Checked)
        self.options_layout.addWidget(self.apocrypha_check_box)
        self.book_name_layout.addWidget(self.options_group_box)
        self.button_box = create_button_box(book_name_dialog, 'button_box', ['cancel', 'ok'])
        self.book_name_layout.addWidget(self.button_box)

        self.retranslateUi(book_name_dialog)

    def retranslateUi(self, book_name_dialog):
        book_name_dialog.setWindowTitle(translate('BiblesPlugin.BookNameDialog', 'Select Book Name'))
        self.info_label.setText(
            translate('BiblesPlugin.BookNameDialog', 'The following book name cannot be matched up internally. '
                      'Please select the corresponding name from the list.'))
        self.current_label.setText(translate('BiblesPlugin.BookNameDialog', 'Current name:'))
        self.corresponding_label.setText(translate('BiblesPlugin.BookNameDialog', 'Corresponding name:'))
        self.options_group_box.setTitle(translate('BiblesPlugin.BookNameDialog', 'Show Books From'))
        self.old_testament_check_box.setText(translate('BiblesPlugin.BookNameDialog', 'Old Testament'))
        self.new_testament_check_box.setText(translate('BiblesPlugin.BookNameDialog', 'New Testament'))
        self.apocrypha_check_box.setText(translate('BiblesPlugin.BookNameDialog', 'Apocrypha'))
