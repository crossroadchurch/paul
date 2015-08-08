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

from openlp.core.common import Settings, UiStrings, translate
from openlp.core.lib import SettingsTab


class MediaTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent, title, visible_title, icon_path):
        self.parent = parent
        super(MediaTab, self).__init__(parent, title, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('MediaTab')
        super(MediaTab, self).setupUi()
        self.advanced_group_box = QtGui.QGroupBox(self.left_column)
        self.advanced_group_box.setObjectName('advanced_group_box')
        self.advanced_layout = QtGui.QVBoxLayout(self.advanced_group_box)
        self.advanced_layout.setObjectName('advanced_layout')
        self.override_player_check_box = QtGui.QCheckBox(self.advanced_group_box)
        self.override_player_check_box.setObjectName('override_player_check_box')
        self.advanced_layout.addWidget(self.override_player_check_box)
        self.auto_start_check_box = QtGui.QCheckBox(self.advanced_group_box)
        self.auto_start_check_box.setObjectName('auto_start_check_box')
        self.advanced_layout.addWidget(self.auto_start_check_box)
        self.left_layout.addWidget(self.advanced_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()

    def retranslateUi(self):
        self.advanced_group_box.setTitle(UiStrings().Advanced)
        self.override_player_check_box.setText(translate('MediaPlugin.MediaTab', 'Allow media player to be overridden'))
        self.auto_start_check_box.setText(translate('MediaPlugin.MediaTab', 'Start Live items automatically'))

    def load(self):
        self.override_player_check_box.setChecked(Settings().value(self.settings_section + '/override player'))
        self.auto_start_check_box.setChecked(Settings().value(self.settings_section + '/media auto start'))

    def save(self):
        setting_key = self.settings_section + '/override player'
        if Settings().value(setting_key) != self.override_player_check_box.checkState():
            Settings().setValue(setting_key, self.override_player_check_box.checkState())
            self.settings_form.register_post_process('mediaitem_suffix_reset')
            self.settings_form.register_post_process('mediaitem_media_rebuild')
            self.settings_form.register_post_process('mediaitem_suffixes')
        setting_key = self.settings_section + '/media auto start'
        if Settings().value(setting_key) != self.auto_start_check_box.checkState():
            Settings().setValue(setting_key, self.auto_start_check_box.checkState())
