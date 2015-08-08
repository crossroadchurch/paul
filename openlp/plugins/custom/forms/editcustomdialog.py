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

from openlp.core.common import UiStrings, translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box, create_button


class Ui_CustomEditDialog(object):
    def setupUi(self, custom_edit_dialog):
        """
        Build the Edit Dialog UI
        :param custom_edit_dialog: The Dialog
        """
        custom_edit_dialog.setObjectName('custom_edit_dialog')
        custom_edit_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        custom_edit_dialog.resize(450, 350)
        self.dialog_layout = QtGui.QVBoxLayout(custom_edit_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.title_layout = QtGui.QHBoxLayout()
        self.title_layout.setObjectName('title_layout')
        self.title_label = QtGui.QLabel(custom_edit_dialog)
        self.title_label.setObjectName('title_label')
        self.title_layout.addWidget(self.title_label)
        self.title_edit = QtGui.QLineEdit(custom_edit_dialog)
        self.title_label.setBuddy(self.title_edit)
        self.title_edit.setObjectName('title_edit')
        self.title_layout.addWidget(self.title_edit)
        self.dialog_layout.addLayout(self.title_layout)
        self.central_layout = QtGui.QHBoxLayout()
        self.central_layout.setObjectName('central_layout')
        self.slide_list_view = QtGui.QListWidget(custom_edit_dialog)
        self.slide_list_view.setAlternatingRowColors(True)
        self.slide_list_view.setObjectName('slide_list_view')
        self.central_layout.addWidget(self.slide_list_view)
        self.button_layout = QtGui.QVBoxLayout()
        self.button_layout.setObjectName('button_layout')
        self.add_button = QtGui.QPushButton(custom_edit_dialog)
        self.add_button.setObjectName('add_button')
        self.button_layout.addWidget(self.add_button)
        self.edit_button = QtGui.QPushButton(custom_edit_dialog)
        self.edit_button.setEnabled(False)
        self.edit_button.setObjectName('edit_button')
        self.button_layout.addWidget(self.edit_button)
        self.edit_all_button = QtGui.QPushButton(custom_edit_dialog)
        self.edit_all_button.setObjectName('edit_all_button')
        self.button_layout.addWidget(self.edit_all_button)
        self.delete_button = create_button(custom_edit_dialog, 'delete_button', role='delete',
                                           click=custom_edit_dialog.on_delete_button_clicked)
        self.delete_button.setEnabled(False)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.up_button = create_button(custom_edit_dialog, 'up_button', role='up', enabled=False,
                                       click=custom_edit_dialog.on_up_button_clicked)
        self.down_button = create_button(custom_edit_dialog, 'down_button', role='down', enabled=False,
                                         click=custom_edit_dialog.on_down_button_clicked)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.central_layout.addLayout(self.button_layout)
        self.dialog_layout.addLayout(self.central_layout)
        self.bottom_form_layout = QtGui.QFormLayout()
        self.bottom_form_layout.setObjectName('bottom_form_layout')
        self.theme_label = QtGui.QLabel(custom_edit_dialog)
        self.theme_label.setObjectName('theme_label')
        self.theme_combo_box = QtGui.QComboBox(custom_edit_dialog)
        self.theme_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.theme_combo_box.setObjectName('theme_combo_box')
        self.theme_label.setBuddy(self.theme_combo_box)
        self.bottom_form_layout.addRow(self.theme_label, self.theme_combo_box)
        self.credit_label = QtGui.QLabel(custom_edit_dialog)
        self.credit_label.setObjectName('credit_label')
        self.credit_edit = QtGui.QLineEdit(custom_edit_dialog)
        self.credit_edit.setObjectName('credit_edit')
        self.credit_label.setBuddy(self.credit_edit)
        self.bottom_form_layout.addRow(self.credit_label, self.credit_edit)
        self.dialog_layout.addLayout(self.bottom_form_layout)
        self.preview_button = QtGui.QPushButton()
        self.button_box = create_button_box(custom_edit_dialog, 'button_box', ['cancel', 'save'],
                                            [self.preview_button])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(custom_edit_dialog)

    def retranslateUi(self, custom_edit_dialog):
        custom_edit_dialog.setWindowTitle(translate('CustomPlugin.EditCustomForm', 'Edit Custom Slides'))
        self.title_label.setText(translate('CustomPlugin.EditCustomForm', '&Title:'))
        self.add_button.setText(UiStrings().Add)
        self.add_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Add a new slide at bottom.'))
        self.edit_button.setText(UiStrings().Edit)
        self.edit_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit the selected slide.'))
        self.edit_all_button.setText(translate('CustomPlugin.EditCustomForm', 'Ed&it All'))
        self.edit_all_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit all the slides at once.'))
        self.theme_label.setText(translate('CustomPlugin.EditCustomForm', 'The&me:'))
        self.credit_label.setText(translate('CustomPlugin.EditCustomForm', '&Credits:'))
        self.preview_button.setText(UiStrings().SaveAndPreview)
