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
The Themes configuration tab
"""


from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, Settings, ThemeLevel, UiStrings, translate
from openlp.core.lib import SettingsTab
from openlp.core.lib.ui import find_and_set_in_combo_box


class ThemesTab(SettingsTab):
    """
    ThemesTab is the theme settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.icon_path = ':/themes/theme_new.png'
        theme_translated = translate('OpenLP.ThemesTab', 'Themes')
        super(ThemesTab, self).__init__(parent, 'Themes', theme_translated)

    def setupUi(self):
        """
        Set up the UI
        """
        self.setObjectName('ThemesTab')
        super(ThemesTab, self).setupUi()
        self.global_group_box = QtGui.QGroupBox(self.left_column)
        self.global_group_box.setObjectName('global_group_box')
        self.global_group_box_layout = QtGui.QVBoxLayout(self.global_group_box)
        self.global_group_box_layout.setObjectName('global_group_box_layout')
        self.default_combo_box = QtGui.QComboBox(self.global_group_box)
        self.default_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.default_combo_box.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.default_combo_box.setObjectName('default_combo_box')
        self.global_group_box_layout.addWidget(self.default_combo_box)
        self.default_list_view = QtGui.QLabel(self.global_group_box)
        self.default_list_view.setObjectName('default_list_view')
        self.global_group_box_layout.addWidget(self.default_list_view)
        self.left_layout.addWidget(self.global_group_box)
        self.universal_group_box = QtGui.QGroupBox(self.left_column)
        self.universal_group_box.setObjectName('universal_group_box')
        self.universal_group_box_layout = QtGui.QVBoxLayout(self.universal_group_box)
        self.universal_group_box_layout.setObjectName('universal_group_box_layout')
        self.wrap_footer_check_box = QtGui.QCheckBox(self.universal_group_box)
        self.wrap_footer_check_box.setObjectName('wrap_footer_check_box')
        self.universal_group_box_layout.addWidget(self.wrap_footer_check_box)
        self.left_layout.addWidget(self.universal_group_box)
        self.left_layout.addStretch()
        self.level_group_box = QtGui.QGroupBox(self.right_column)
        self.level_group_box.setObjectName('level_group_box')
        self.level_layout = QtGui.QFormLayout(self.level_group_box)
        self.level_layout.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.level_layout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.level_layout.setObjectName('level_layout')
        self.song_level_radio_button = QtGui.QRadioButton(self.level_group_box)
        self.song_level_radio_button.setObjectName('song_level_radio_button')
        self.song_level_label = QtGui.QLabel(self.level_group_box)
        self.song_level_label.setObjectName('song_level_label')
        self.level_layout.addRow(self.song_level_radio_button, self.song_level_label)
        self.service_level_radio_button = QtGui.QRadioButton(self.level_group_box)
        self.service_level_radio_button.setObjectName('service_level_radio_button')
        self.service_level_label = QtGui.QLabel(self.level_group_box)
        self.service_level_label.setObjectName('service_level_label')
        self.level_layout.addRow(self.service_level_radio_button, self.service_level_label)
        self.global_level_radio_button = QtGui.QRadioButton(self.level_group_box)
        self.global_level_radio_button.setObjectName('global_level_radio_button')
        self.global_level_label = QtGui.QLabel(self.level_group_box)
        self.global_level_label.setObjectName('global_level_label')
        self.level_layout.addRow(self.global_level_radio_button, self.global_level_label)
        label_top_margin = (self.song_level_radio_button.sizeHint().height() -
                            self.song_level_label.sizeHint().height()) // 2
        for label in [self.song_level_label, self.service_level_label, self.global_level_label]:
            rect = label.rect()
            rect.setTop(rect.top() + label_top_margin)
            label.setFrameRect(rect)
            label.setWordWrap(True)
        self.right_layout.addWidget(self.level_group_box)
        self.right_layout.addStretch()
        self.song_level_radio_button.clicked.connect(self.on_song_level_button_clicked)
        self.service_level_radio_button.clicked.connect(self.on_service_level_button_clicked)
        self.global_level_radio_button.clicked.connect(self.on_global_level_button_clicked)
        self.default_combo_box.activated.connect(self.on_default_combo_box_changed)
        Registry().register_function('theme_update_list', self.update_theme_list)

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.tab_title_visible = UiStrings().Themes
        self.global_group_box.setTitle(translate('OpenLP.ThemesTab', 'Global Theme'))
        self.universal_group_box.setTitle(translate('OpenLP.ThemesTab', 'Universal Settings'))
        self.wrap_footer_check_box.setText(translate('OpenLP.ThemesTab', '&Wrap footer text'))
        self.level_group_box.setTitle(translate('OpenLP.ThemesTab', 'Theme Level'))
        self.song_level_radio_button.setText(translate('OpenLP.ThemesTab', 'S&ong Level'))
        self.song_level_label.setText(
            translate('OpenLP.ThemesTab', 'Use the theme from each song in the database. If a song doesn\'t have a '
                                          'theme associated with it, then use the service\'s theme. If the service '
                                          'doesn\'t have a theme, then use the global theme.'))
        self.service_level_radio_button.setText(translate('OpenLP.ThemesTab', '&Service Level'))
        self.service_level_label.setText(
            translate('OpenLP.ThemesTab', 'Use the theme from the service, overriding any of the individual '
                                          'songs\' themes. If the service doesn\'t have a theme, then use the global '
                                          'theme.'))
        self.global_level_radio_button.setText(translate('OpenLP.ThemesTab', '&Global Level'))
        self.global_level_label.setText(translate('OpenLP.ThemesTab', 'Use the global theme, overriding any themes '
                                                                      'associated with either the service or the '
                                                                      'songs.'))

    def load(self):
        """
        Load the theme settings into the tab
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.theme_level = settings.value('theme level')
        self.global_theme = settings.value('global theme')
        self.wrap_footer_check_box.setChecked(settings.value('wrap footer'))
        settings.endGroup()
        if self.theme_level == ThemeLevel.Global:
            self.global_level_radio_button.setChecked(True)
        elif self.theme_level == ThemeLevel.Service:
            self.service_level_radio_button.setChecked(True)
        else:
            self.song_level_radio_button.setChecked(True)

    def save(self):
        """
        Save the settings
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('theme level', self.theme_level)
        settings.setValue('global theme', self.global_theme)
        settings.setValue('wrap footer', self.wrap_footer_check_box.isChecked())
        settings.endGroup()
        self.renderer.set_theme_level(self.theme_level)
        if self.tab_visited:
            self.settings_form.register_post_process('theme_update_global')
        self.tab_visited = False

    def on_song_level_button_clicked(self):
        """
        Set the theme level
        """
        self.theme_level = ThemeLevel.Song

    def on_service_level_button_clicked(self):
        """
        Set the theme level
        """
        self.theme_level = ThemeLevel.Service

    def on_global_level_button_clicked(self):
        """
        Set the theme level
        """
        self.theme_level = ThemeLevel.Global

    def on_default_combo_box_changed(self, value):
        """
        Set the global default theme
        """
        self.global_theme = self.default_combo_box.currentText()
        self.renderer.set_global_theme()
        self._preview_global_theme()

    def update_theme_list(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed.

        :param theme_list: The list of available themes::

                ['Bible Theme', 'Song Theme']
        """
        # Reload as may have been triggered by the ThemeManager.
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        self.default_combo_box.clear()
        self.default_combo_box.addItems(theme_list)
        find_and_set_in_combo_box(self.default_combo_box, self.global_theme)
        self.renderer.set_global_theme()
        self.renderer.set_theme_level(self.theme_level)
        if self.global_theme is not '':
            self._preview_global_theme()

    def _preview_global_theme(self):
        """
        Utility method to update the global theme preview image.
        """
        image = self.theme_manager.get_preview_image(self.global_theme)
        preview = QtGui.QPixmap(str(image))
        if not preview.isNull():
            preview = preview.scaled(300, 255, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.default_list_view.setPixmap(preview)
