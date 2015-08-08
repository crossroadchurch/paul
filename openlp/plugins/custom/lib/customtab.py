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
The :mod:`~openlp.plugins.custom.lib.customtab` module contains the settings tab
for the Custom Slides plugin, which is inserted into the configuration dialog.
"""

from PyQt4 import QtCore, QtGui

from openlp.core.common import Settings, translate
from openlp.core.lib import SettingsTab


class CustomTab(SettingsTab):
    """
    CustomTab is the Custom settings tab in the settings dialog.
    """
    def __init__(self, parent, title, visible_title, icon_path):
        super(CustomTab, self).__init__(parent, title, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('CustomTab')
        super(CustomTab, self).setupUi()
        self.custom_mode_group_box = QtGui.QGroupBox(self.left_column)
        self.custom_mode_group_box.setObjectName('custom_mode_group_box')
        self.custom_mode_layout = QtGui.QFormLayout(self.custom_mode_group_box)
        self.custom_mode_layout.setObjectName('custom_mode_layout')
        self.display_footer_check_box = QtGui.QCheckBox(self.custom_mode_group_box)
        self.display_footer_check_box.setObjectName('display_footer_check_box')
        self.custom_mode_layout.addRow(self.display_footer_check_box)
        self.add_from_service_checkbox = QtGui.QCheckBox(self.custom_mode_group_box)
        self.add_from_service_checkbox.setObjectName('add_from_service_checkbox')
        self.custom_mode_layout.addRow(self.add_from_service_checkbox)
        self.left_layout.addWidget(self.custom_mode_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        self.display_footer_check_box.stateChanged.connect(self.on_display_footer_check_box_changed)
        self.add_from_service_checkbox.stateChanged.connect(self.on_add_from_service_check_box_changed)

    def retranslateUi(self):
        self.custom_mode_group_box.setTitle(translate('CustomPlugin.CustomTab', 'Custom Display'))
        self.display_footer_check_box.setText(translate('CustomPlugin.CustomTab', 'Display footer'))
        self.add_from_service_checkbox.setText(translate('CustomPlugin.CustomTab',
                                               'Import missing custom slides from service files'))

    def on_display_footer_check_box_changed(self, check_state):
        """
        Toggle the setting for displaying the footer.

        :param check_state: The current check box state
        """
        self.display_footer = False
        # we have a set value convert to True/False
        if check_state == QtCore.Qt.Checked:
            self.display_footer = True

    def on_add_from_service_check_box_changed(self, check_state):
        """
        Allows service items to create Custom items.

        :param check_state: The current check box state
        """
        self.update_load = (check_state == QtCore.Qt.Checked)

    def load(self):
        """

        Load the settings into the dialog
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.display_footer = settings.value('display footer')
        self.update_load = settings.value('add custom from service')
        self.display_footer_check_box.setChecked(self.display_footer)
        self.add_from_service_checkbox.setChecked(self.update_load)
        settings.endGroup()

    def save(self):
        """
        Save the Dialog settings
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('display footer', self.display_footer)
        settings.setValue('add custom from service', self.update_load)
        settings.endGroup()
        if self.tab_visited:
            self.settings_form.register_post_process('custom_config_updated')
        self.tab_visited = False
