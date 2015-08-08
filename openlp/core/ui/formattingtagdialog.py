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
The UI widgets for the formatting tags window.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import UiStrings, translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_FormattingTagDialog(object):
    """
    The UI widgets for the formatting tags window.
    """
    def setupUi(self, formatting_tag_dialog):
        """
        Set up the UI
        """
        formatting_tag_dialog.setObjectName('formatting_tag_dialog')
        formatting_tag_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        formatting_tag_dialog.resize(725, 548)
        self.list_data_grid_layout = QtGui.QVBoxLayout(formatting_tag_dialog)
        self.list_data_grid_layout.setMargin(8)
        self.list_data_grid_layout.setObjectName('list_data_grid_layout')
        self.tag_table_widget_read_label = QtGui.QLabel()
        self.list_data_grid_layout.addWidget(self.tag_table_widget_read_label)
        self.tag_table_widget_read = QtGui.QTableWidget(formatting_tag_dialog)
        self.tag_table_widget_read.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tag_table_widget_read.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tag_table_widget_read.setAlternatingRowColors(True)
        self.tag_table_widget_read.setCornerButtonEnabled(False)
        self.tag_table_widget_read.setObjectName('tag_table_widget_read')
        self.tag_table_widget_read.setColumnCount(4)
        self.tag_table_widget_read.setRowCount(0)
        self.tag_table_widget_read.horizontalHeader().setStretchLastSection(True)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget_read.setHorizontalHeaderItem(3, item)
        self.list_data_grid_layout.addWidget(self.tag_table_widget_read)
        self.tag_table_widget_label = QtGui.QLabel()
        self.list_data_grid_layout.addWidget(self.tag_table_widget_label)
        self.tag_table_widget = QtGui.QTableWidget(formatting_tag_dialog)
        self.tag_table_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tag_table_widget.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.tag_table_widget.setAlternatingRowColors(True)
        self.tag_table_widget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tag_table_widget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tag_table_widget.setCornerButtonEnabled(False)
        self.tag_table_widget.setObjectName('tag_table_widget')
        self.tag_table_widget.setColumnCount(4)
        self.tag_table_widget.setRowCount(0)
        self.tag_table_widget.horizontalHeader().setStretchLastSection(True)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tag_table_widget.setHorizontalHeaderItem(3, item)
        self.list_data_grid_layout.addWidget(self.tag_table_widget)
        self.edit_button_layout = QtGui.QHBoxLayout()
        self.new_button = QtGui.QPushButton(formatting_tag_dialog)
        self.new_button.setIcon(build_icon(':/general/general_new.png'))
        self.new_button.setObjectName('new_button')
        self.edit_button_layout.addWidget(self.new_button)
        self.delete_button = QtGui.QPushButton(formatting_tag_dialog)
        self.delete_button.setIcon(build_icon(':/general/general_delete.png'))
        self.delete_button.setObjectName('delete_button')
        self.edit_button_layout.addWidget(self.delete_button)
        self.edit_button_layout.addStretch()
        self.list_data_grid_layout.addLayout(self.edit_button_layout)
        self.button_box = create_button_box(formatting_tag_dialog, 'button_box', ['cancel', 'save', 'defaults'])
        self.save_button = self.button_box.button(QtGui.QDialogButtonBox.Save)
        self.save_button.setObjectName('save_button')
        self.restore_button = self.button_box.button(QtGui.QDialogButtonBox.RestoreDefaults)
        self.restore_button.setIcon(build_icon(':/general/general_revert.png'))
        self.restore_button.setObjectName('restore_button')
        self.list_data_grid_layout.addWidget(self.button_box)
        self.retranslateUi(formatting_tag_dialog)

    def retranslateUi(self, formatting_tag_dialog):
        """
        Translate the UI on the fly
        """
        formatting_tag_dialog.setWindowTitle(translate('OpenLP.FormattingTagDialog', 'Configure Formatting Tags'))
        self.delete_button.setText(UiStrings().Delete)
        self.new_button.setText(UiStrings().New)
        self.tag_table_widget_read_label.setText(translate('OpenLP.FormattingTagDialog', 'Default Formatting'))
        self.tag_table_widget_read.horizontalHeaderItem(0).\
            setText(translate('OpenLP.FormattingTagDialog', 'Description'))
        self.tag_table_widget_read.horizontalHeaderItem(1).setText(translate('OpenLP.FormattingTagDialog', 'Tag'))
        self.tag_table_widget_read.horizontalHeaderItem(2).\
            setText(translate('OpenLP.FormattingTagDialog', 'Start HTML'))
        self.tag_table_widget_read.horizontalHeaderItem(3).setText(translate('OpenLP.FormattingTagDialog', 'End HTML'))
        self.tag_table_widget_read.setColumnWidth(0, 120)
        self.tag_table_widget_read.setColumnWidth(1, 80)
        self.tag_table_widget_read.setColumnWidth(2, 330)
        self.tag_table_widget_label.setText(translate('OpenLP.FormattingTagDialog', 'Custom Formatting'))
        self.tag_table_widget.horizontalHeaderItem(0).setText(translate('OpenLP.FormattingTagDialog', 'Description'))
        self.tag_table_widget.horizontalHeaderItem(1).setText(translate('OpenLP.FormattingTagDialog', 'Tag'))
        self.tag_table_widget.horizontalHeaderItem(2).setText(translate('OpenLP.FormattingTagDialog', 'Start HTML'))
        self.tag_table_widget.horizontalHeaderItem(3).setText(translate('OpenLP.FormattingTagDialog', 'End HTML'))
        self.tag_table_widget.setColumnWidth(0, 120)
        self.tag_table_widget.setColumnWidth(1, 80)
        self.tag_table_widget.setColumnWidth(2, 330)
