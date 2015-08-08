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
from openlp.core.lib.ui import create_button_box


class Ui_ChooseGroupDialog(object):
    """
    The UI for the "Choose Image Group" form.
    """
    def setupUi(self, choose_group_dialog):
        """
        Set up the UI.

        :param choose_group_dialog: The form object (not the class).
        """
        choose_group_dialog.setObjectName('choose_group_dialog')
        choose_group_dialog.resize(399, 119)
        self.choose_group_layout = QtGui.QFormLayout(choose_group_dialog)
        self.choose_group_layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.choose_group_layout.setMargin(8)
        self.choose_group_layout.setSpacing(8)
        self.choose_group_layout.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.choose_group_layout.setObjectName('choose_group_layout')
        self.group_question_label = QtGui.QLabel(choose_group_dialog)
        self.group_question_label.setWordWrap(True)
        self.group_question_label.setObjectName('group_question_label')
        self.choose_group_layout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.group_question_label)
        self.nogroup_radio_button = QtGui.QRadioButton(choose_group_dialog)
        self.nogroup_radio_button.setChecked(True)
        self.nogroup_radio_button.setObjectName('nogroup_radio_button')
        self.choose_group_layout.setWidget(2, QtGui.QFormLayout.LabelRole, self.nogroup_radio_button)
        self.existing_radio_button = QtGui.QRadioButton(choose_group_dialog)
        self.existing_radio_button.setChecked(False)
        self.existing_radio_button.setObjectName('existing_radio_button')
        self.choose_group_layout.setWidget(3, QtGui.QFormLayout.LabelRole, self.existing_radio_button)
        self.group_combobox = QtGui.QComboBox(choose_group_dialog)
        self.group_combobox.setObjectName('group_combobox')
        self.choose_group_layout.setWidget(3, QtGui.QFormLayout.FieldRole, self.group_combobox)
        self.new_radio_button = QtGui.QRadioButton(choose_group_dialog)
        self.new_radio_button.setChecked(False)
        self.new_radio_button.setObjectName('new_radio_button')
        self.choose_group_layout.setWidget(4, QtGui.QFormLayout.LabelRole, self.new_radio_button)
        self.new_group_edit = QtGui.QLineEdit(choose_group_dialog)
        self.new_group_edit.setObjectName('new_group_edit')
        self.choose_group_layout.setWidget(4, QtGui.QFormLayout.FieldRole, self.new_group_edit)
        self.group_button_box = create_button_box(choose_group_dialog, 'buttonBox', ['ok'])
        self.choose_group_layout.setWidget(5, QtGui.QFormLayout.FieldRole, self.group_button_box)

        self.retranslateUi(choose_group_dialog)
        QtCore.QMetaObject.connectSlotsByName(choose_group_dialog)

    def retranslateUi(self, choose_group_dialog):
        """
        Translate the UI on the fly.

        :param choose_group_dialog: The form object (not the class).
        """
        choose_group_dialog.setWindowTitle(translate('ImagePlugin.ChooseGroupForm', 'Select Image Group'))
        self.group_question_label.setText(translate('ImagePlugin.ChooseGroupForm', 'Add images to group:'))
        self.nogroup_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'No group'))
        self.existing_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'Existing group'))
        self.new_radio_button.setText(translate('ImagePlugin.ChooseGroupForm', 'New group'))
