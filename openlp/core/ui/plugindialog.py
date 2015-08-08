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
The UI widgets of the plugin view dialog
#"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import UiStrings, translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_PluginViewDialog(object):
    """
    The UI of the plugin view dialog
    """
    def setupUi(self, pluginViewDialog):
        """
        Set up the UI
        """
        pluginViewDialog.setObjectName('pluginViewDialog')
        pluginViewDialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        pluginViewDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.plugin_layout = QtGui.QVBoxLayout(pluginViewDialog)
        self.plugin_layout.setObjectName('plugin_layout')
        self.list_layout = QtGui.QHBoxLayout()
        self.list_layout.setObjectName('list_layout')
        self.plugin_list_widget = QtGui.QListWidget(pluginViewDialog)
        self.plugin_list_widget.setObjectName('plugin_list_widget')
        self.list_layout.addWidget(self.plugin_list_widget)
        self.plugin_info_group_box = QtGui.QGroupBox(pluginViewDialog)
        self.plugin_info_group_box.setObjectName('plugin_info_group_box')
        self.plugin_info_layout = QtGui.QFormLayout(self.plugin_info_group_box)
        self.plugin_info_layout.setObjectName('plugin_info_layout')
        self.status_label = QtGui.QLabel(self.plugin_info_group_box)
        self.status_label.setObjectName('status_label')
        self.status_combo_box = QtGui.QComboBox(self.plugin_info_group_box)
        self.status_combo_box.addItems(('', ''))
        self.status_combo_box.setObjectName('status_combo_box')
        self.plugin_info_layout.addRow(self.status_label, self.status_combo_box)
        self.version_label = QtGui.QLabel(self.plugin_info_group_box)
        self.version_label.setObjectName('version_label')
        self.version_number_label = QtGui.QLabel(self.plugin_info_group_box)
        self.version_number_label.setObjectName('version_number_label')
        self.plugin_info_layout.addRow(self.version_label, self.version_number_label)
        self.about_label = QtGui.QLabel(self.plugin_info_group_box)
        self.about_label.setObjectName('about_label')
        self.about_text_browser = QtGui.QTextBrowser(self.plugin_info_group_box)
        self.about_text_browser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.about_text_browser.setObjectName('aboutTextBrowser')
        self.plugin_info_layout.addRow(self.about_label, self.about_text_browser)
        self.list_layout.addWidget(self.plugin_info_group_box)
        self.plugin_layout.addLayout(self.list_layout)
        self.button_box = create_button_box(pluginViewDialog, 'button_box', ['ok'])
        self.plugin_layout.addWidget(self.button_box)
        self.retranslateUi(pluginViewDialog)

    def retranslateUi(self, pluginViewDialog):
        """
        Translate the UI on the fly
        """
        pluginViewDialog.setWindowTitle(translate('OpenLP.PluginForm', 'Plugin List'))
        self.plugin_info_group_box.setTitle(translate('OpenLP.PluginForm', 'Plugin Details'))
        self.version_label.setText('%s:' % UiStrings().Version)
        self.about_label.setText('%s:' % UiStrings().About)
        self.status_label.setText(translate('OpenLP.PluginForm', 'Status:'))
        self.status_combo_box.setItemText(0, translate('OpenLP.PluginForm', 'Active'))
        self.status_combo_box.setItemText(1, translate('OpenLP.PluginForm', 'Inactive'))
