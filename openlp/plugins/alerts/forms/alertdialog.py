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

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button, create_button_box


class Ui_AlertDialog(object):
    """
    Alert UI Class
    """
    def setupUi(self, alert_dialog):
        """
        Setup the Alert UI dialog

        :param alert_dialog: The dialog
        """
        alert_dialog.setObjectName('alert_dialog')
        alert_dialog.resize(400, 300)
        alert_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        self.alert_dialog_layout = QtGui.QGridLayout(alert_dialog)
        self.alert_dialog_layout.setObjectName('alert_dialog_layout')
        self.alert_text_layout = QtGui.QFormLayout()
        self.alert_text_layout.setObjectName('alert_text_layout')
        self.alert_entry_label = QtGui.QLabel(alert_dialog)
        self.alert_entry_label.setObjectName('alert_entry_label')
        self.alert_text_edit = QtGui.QLineEdit(alert_dialog)
        self.alert_text_edit.setObjectName('alert_text_edit')
        self.alert_entry_label.setBuddy(self.alert_text_edit)
        self.alert_text_layout.addRow(self.alert_entry_label, self.alert_text_edit)
        self.alert_parameter = QtGui.QLabel(alert_dialog)
        self.alert_parameter.setObjectName('alert_parameter')
        self.parameter_edit = QtGui.QLineEdit(alert_dialog)
        self.parameter_edit.setObjectName('parameter_edit')
        self.alert_parameter.setBuddy(self.parameter_edit)
        self.alert_text_layout.addRow(self.alert_parameter, self.parameter_edit)
        self.alert_dialog_layout.addLayout(self.alert_text_layout, 0, 0, 1, 2)
        self.alert_list_widget = QtGui.QListWidget(alert_dialog)
        self.alert_list_widget.setAlternatingRowColors(True)
        self.alert_list_widget.setObjectName('alert_list_widget')
        self.alert_dialog_layout.addWidget(self.alert_list_widget, 1, 0)
        self.manage_button_layout = QtGui.QVBoxLayout()
        self.manage_button_layout.setObjectName('manage_button_layout')
        self.new_button = QtGui.QPushButton(alert_dialog)
        self.new_button.setIcon(build_icon(':/general/general_new.png'))
        self.new_button.setObjectName('new_button')
        self.manage_button_layout.addWidget(self.new_button)
        self.save_button = QtGui.QPushButton(alert_dialog)
        self.save_button.setEnabled(False)
        self.save_button.setIcon(build_icon(':/general/general_save.png'))
        self.save_button.setObjectName('save_button')
        self.manage_button_layout.addWidget(self.save_button)
        self.delete_button = create_button(alert_dialog, 'delete_button', role='delete', enabled=False,
                                           click=alert_dialog.on_delete_button_clicked)
        self.manage_button_layout.addWidget(self.delete_button)
        self.manage_button_layout.addStretch()
        self.alert_dialog_layout.addLayout(self.manage_button_layout, 1, 1)
        display_icon = build_icon(':/general/general_live.png')
        self.display_button = create_button(alert_dialog, 'display_button', icon=display_icon, enabled=False)
        self.display_close_button = create_button(alert_dialog, 'display_close_button', icon=display_icon,
                                                  enabled=False)
        self.button_box = create_button_box(alert_dialog, 'button_box', ['close'],
                                            [self.display_button, self.display_close_button])
        self.alert_dialog_layout.addWidget(self.button_box, 2, 0, 1, 2)
        self.retranslateUi(alert_dialog)

    def retranslateUi(self, alert_dialog):
        """
        Retranslate the UI strings

        :param alert_dialog: The dialog
        """
        alert_dialog.setWindowTitle(translate('AlertsPlugin.AlertForm', 'Alert Message'))
        self.alert_entry_label.setText(translate('AlertsPlugin.AlertForm', 'Alert &text:'))
        self.alert_parameter.setText(translate('AlertsPlugin.AlertForm', '&Parameter:'))
        self.new_button.setText(translate('AlertsPlugin.AlertForm', '&New'))
        self.save_button.setText(translate('AlertsPlugin.AlertForm', '&Save'))
        self.display_button.setText(translate('AlertsPlugin.AlertForm', 'Displ&ay'))
        self.display_close_button.setText(translate('AlertsPlugin.AlertForm', 'Display && Cl&ose'))
