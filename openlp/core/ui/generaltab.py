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
The general tab of the configuration dialog.
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, Settings, UiStrings, translate
from openlp.core.lib import SettingsTab, ScreenList

log = logging.getLogger(__name__)


class GeneralTab(SettingsTab):
    """
    GeneralTab is the general settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Initialise the general settings tab
        """
        self.screens = ScreenList()
        self.icon_path = ':/icon/openlp-logo-16x16.png'
        general_translated = translate('OpenLP.GeneralTab', 'General')
        super(GeneralTab, self).__init__(parent, 'Core', general_translated)

    def setupUi(self):
        """
        Create the user interface for the general settings tab
        """
        self.setObjectName('GeneralTab')
        super(GeneralTab, self).setupUi()
        self.tab_layout.setStretch(1, 1)
        # Monitors
        self.monitor_group_box = QtGui.QGroupBox(self.left_column)
        self.monitor_group_box.setObjectName('monitor_group_box')
        self.monitor_layout = QtGui.QGridLayout(self.monitor_group_box)
        self.monitor_layout.setObjectName('monitor_layout')
        self.monitor_radio_button = QtGui.QRadioButton(self.monitor_group_box)
        self.monitor_radio_button.setObjectName('monitor_radio_button')
        self.monitor_layout.addWidget(self.monitor_radio_button, 0, 0, 1, 5)
        self.monitor_combo_box = QtGui.QComboBox(self.monitor_group_box)
        self.monitor_combo_box.setObjectName('monitor_combo_box')
        self.monitor_layout.addWidget(self.monitor_combo_box, 1, 1, 1, 4)
        # Display Position
        self.override_radio_button = QtGui.QRadioButton(self.monitor_group_box)
        self.override_radio_button.setObjectName('override_radio_button')
        self.monitor_layout.addWidget(self.override_radio_button, 2, 0, 1, 5)
        # Custom position
        self.custom_x_label = QtGui.QLabel(self.monitor_group_box)
        self.custom_x_label.setObjectName('custom_x_label')
        self.monitor_layout.addWidget(self.custom_x_label, 3, 1)
        self.custom_X_value_edit = QtGui.QSpinBox(self.monitor_group_box)
        self.custom_X_value_edit.setObjectName('custom_X_value_edit')
        self.custom_X_value_edit.setRange(-9999, 9999)
        self.monitor_layout.addWidget(self.custom_X_value_edit, 4, 1)
        self.custom_y_label = QtGui.QLabel(self.monitor_group_box)
        self.custom_y_label.setObjectName('custom_y_label')
        self.monitor_layout.addWidget(self.custom_y_label, 3, 2)
        self.custom_Y_value_edit = QtGui.QSpinBox(self.monitor_group_box)
        self.custom_Y_value_edit.setObjectName('custom_Y_value_edit')
        self.custom_Y_value_edit.setRange(-9999, 9999)
        self.monitor_layout.addWidget(self.custom_Y_value_edit, 4, 2)
        self.custom_width_label = QtGui.QLabel(self.monitor_group_box)
        self.custom_width_label.setObjectName('custom_width_label')
        self.monitor_layout.addWidget(self.custom_width_label, 3, 3)
        self.custom_width_value_edit = QtGui.QSpinBox(self.monitor_group_box)
        self.custom_width_value_edit.setObjectName('custom_width_value_edit')
        self.custom_width_value_edit.setRange(1, 9999)
        self.monitor_layout.addWidget(self.custom_width_value_edit, 4, 3)
        self.custom_height_label = QtGui.QLabel(self.monitor_group_box)
        self.custom_height_label.setObjectName('custom_height_label')
        self.monitor_layout.addWidget(self.custom_height_label, 3, 4)
        self.custom_height_value_edit = QtGui.QSpinBox(self.monitor_group_box)
        self.custom_height_value_edit.setObjectName('custom_height_value_edit')
        self.custom_height_value_edit.setRange(1, 9999)
        self.monitor_layout.addWidget(self.custom_height_value_edit, 4, 4)
        self.display_on_monitor_check = QtGui.QCheckBox(self.monitor_group_box)
        self.display_on_monitor_check.setObjectName('monitor_combo_box')
        self.monitor_layout.addWidget(self.display_on_monitor_check, 5, 0, 1, 5)
        # Set up the stretchiness of each column, so that the first column
        # less stretchy (and therefore smaller) than the others
        self.monitor_layout.setColumnStretch(0, 1)
        self.monitor_layout.setColumnStretch(1, 3)
        self.monitor_layout.setColumnStretch(2, 3)
        self.monitor_layout.setColumnStretch(3, 3)
        self.monitor_layout.setColumnStretch(4, 3)
        self.left_layout.addWidget(self.monitor_group_box)
        # CCLI Details
        self.ccli_group_box = QtGui.QGroupBox(self.left_column)
        self.ccli_group_box.setObjectName('ccli_group_box')
        self.ccli_layout = QtGui.QFormLayout(self.ccli_group_box)
        self.ccli_layout.setObjectName('ccli_layout')
        self.number_label = QtGui.QLabel(self.ccli_group_box)
        self.number_label.setObjectName('number_label')
        self.number_edit = QtGui.QLineEdit(self.ccli_group_box)
        self.number_edit.setValidator(QtGui.QIntValidator())
        self.number_edit.setObjectName('number_edit')
        self.ccli_layout.addRow(self.number_label, self.number_edit)
        self.username_label = QtGui.QLabel(self.ccli_group_box)
        self.username_label.setObjectName('username_label')
        self.username_edit = QtGui.QLineEdit(self.ccli_group_box)
        self.username_edit.setObjectName('username_edit')
        self.ccli_layout.addRow(self.username_label, self.username_edit)
        self.password_label = QtGui.QLabel(self.ccli_group_box)
        self.password_label.setObjectName('password_label')
        self.password_edit = QtGui.QLineEdit(self.ccli_group_box)
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_edit.setObjectName('password_edit')
        self.ccli_layout.addRow(self.password_label, self.password_edit)
        self.left_layout.addWidget(self.ccli_group_box)
        # Background audio
        self.audio_group_box = QtGui.QGroupBox(self.left_column)
        self.audio_group_box.setObjectName('audio_group_box')
        self.audio_layout = QtGui.QVBoxLayout(self.audio_group_box)
        self.audio_layout.setObjectName('audio_layout')
        self.start_paused_check_box = QtGui.QCheckBox(self.audio_group_box)
        self.start_paused_check_box.setObjectName('start_paused_check_box')
        self.audio_layout.addWidget(self.start_paused_check_box)
        self.repeat_list_check_box = QtGui.QCheckBox(self.audio_group_box)
        self.repeat_list_check_box.setObjectName('repeat_list_check_box')
        self.audio_layout.addWidget(self.repeat_list_check_box)
        self.left_layout.addWidget(self.audio_group_box)
        self.left_layout.addStretch()
        # Application Startup
        self.startup_group_box = QtGui.QGroupBox(self.right_column)
        self.startup_group_box.setObjectName('startup_group_box')
        self.startup_layout = QtGui.QVBoxLayout(self.startup_group_box)
        self.startup_layout.setObjectName('startup_layout')
        self.warning_check_box = QtGui.QCheckBox(self.startup_group_box)
        self.warning_check_box.setObjectName('warning_check_box')
        self.startup_layout.addWidget(self.warning_check_box)
        self.auto_open_check_box = QtGui.QCheckBox(self.startup_group_box)
        self.auto_open_check_box.setObjectName('auto_open_check_box')
        self.startup_layout.addWidget(self.auto_open_check_box)
        self.show_splash_check_box = QtGui.QCheckBox(self.startup_group_box)
        self.show_splash_check_box.setObjectName('show_splash_check_box')
        self.startup_layout.addWidget(self.show_splash_check_box)
        self.check_for_updates_check_box = QtGui.QCheckBox(self.startup_group_box)
        self.check_for_updates_check_box.setObjectName('check_for_updates_check_box')
        self.startup_layout.addWidget(self.check_for_updates_check_box)
        self.right_layout.addWidget(self.startup_group_box)
        # Application Settings
        self.settings_group_box = QtGui.QGroupBox(self.right_column)
        self.settings_group_box.setObjectName('settings_group_box')
        self.settings_layout = QtGui.QFormLayout(self.settings_group_box)
        self.settings_layout.setObjectName('settings_layout')
        self.save_check_service_check_box = QtGui.QCheckBox(self.settings_group_box)
        self.save_check_service_check_box.setObjectName('save_check_service_check_box')
        self.settings_layout.addRow(self.save_check_service_check_box)
        self.auto_unblank_check_box = QtGui.QCheckBox(self.settings_group_box)
        self.auto_unblank_check_box.setObjectName('auto_unblank_check_box')
        self.settings_layout.addRow(self.auto_unblank_check_box)
        self.auto_preview_check_box = QtGui.QCheckBox(self.settings_group_box)
        self.auto_preview_check_box.setObjectName('auto_preview_check_box')
        self.settings_layout.addRow(self.auto_preview_check_box)
        # Moved here from image tab
        self.timeout_label = QtGui.QLabel(self.settings_group_box)
        self.timeout_label.setObjectName('timeout_label')
        self.timeout_spin_box = QtGui.QSpinBox(self.settings_group_box)
        self.timeout_spin_box.setObjectName('timeout_spin_box')
        self.timeout_spin_box.setRange(1, 180)
        self.settings_layout.addRow(self.timeout_label, self.timeout_spin_box)
        self.right_layout.addWidget(self.settings_group_box)
        self.right_layout.addStretch()
        # Signals and slots
        self.override_radio_button.toggled.connect(self.on_override_radio_button_pressed)
        self.custom_height_value_edit.valueChanged.connect(self.on_display_changed)
        self.custom_width_value_edit.valueChanged.connect(self.on_display_changed)
        self.custom_Y_value_edit.valueChanged.connect(self.on_display_changed)
        self.custom_X_value_edit.valueChanged.connect(self.on_display_changed)
        self.monitor_combo_box.currentIndexChanged.connect(self.on_display_changed)
        # Reload the tab, as the screen resolution/count may have changed.
        Registry().register_function('config_screen_changed', self.load)
        # Remove for now
        self.username_label.setVisible(False)
        self.username_edit.setVisible(False)
        self.password_label.setVisible(False)
        self.password_edit.setVisible(False)

    def retranslateUi(self):
        """
        Translate the general settings tab to the currently selected language
        """
        self.tab_title_visible = translate('OpenLP.GeneralTab', 'General')
        self.monitor_group_box.setTitle(translate('OpenLP.GeneralTab', 'Monitors'))
        self.monitor_radio_button.setText(translate('OpenLP.GeneralTab', 'Select monitor for output display:'))
        self.display_on_monitor_check.setText(translate('OpenLP.GeneralTab', 'Display if a single screen'))
        self.startup_group_box.setTitle(translate('OpenLP.GeneralTab', 'Application Startup'))
        self.warning_check_box.setText(translate('OpenLP.GeneralTab', 'Show blank screen warning'))
        self.auto_open_check_box.setText(translate('OpenLP.GeneralTab', 'Automatically open the last service'))
        self.show_splash_check_box.setText(translate('OpenLP.GeneralTab', 'Show the splash screen'))
        self.check_for_updates_check_box.setText(translate('OpenLP.GeneralTab', 'Check for updates to OpenLP'))
        self.settings_group_box.setTitle(translate('OpenLP.GeneralTab', 'Application Settings'))
        self.save_check_service_check_box.setText(translate('OpenLP.GeneralTab',
                                                  'Prompt to save before starting a new service'))
        self.auto_unblank_check_box.setText(translate('OpenLP.GeneralTab', 'Unblank display when adding new live item'))
        self.auto_preview_check_box.setText(translate('OpenLP.GeneralTab',
                                                      'Automatically preview next item in service'))
        self.timeout_label.setText(translate('OpenLP.GeneralTab', 'Timed slide interval:'))
        self.timeout_spin_box.setSuffix(translate('OpenLP.GeneralTab', ' sec'))
        self.ccli_group_box.setTitle(translate('OpenLP.GeneralTab', 'CCLI Details'))
        self.number_label.setText(UiStrings().CCLINumberLabel)
        self.username_label.setText(translate('OpenLP.GeneralTab', 'SongSelect username:'))
        self.password_label.setText(translate('OpenLP.GeneralTab', 'SongSelect password:'))
        # Moved from display tab
        self.override_radio_button.setText(translate('OpenLP.GeneralTab', 'Override display position:'))
        self.custom_x_label.setText(translate('OpenLP.GeneralTab', 'X'))
        self.custom_y_label.setText(translate('OpenLP.GeneralTab', 'Y'))
        self.custom_height_label.setText(translate('OpenLP.GeneralTab', 'Height'))
        self.custom_width_label.setText(translate('OpenLP.GeneralTab', 'Width'))
        self.audio_group_box.setTitle(translate('OpenLP.GeneralTab', 'Background Audio'))
        self.start_paused_check_box.setText(translate('OpenLP.GeneralTab', 'Start background audio paused'))
        self.repeat_list_check_box.setText(translate('OpenLP.GeneralTab', 'Repeat track list'))

    def load(self):
        """
        Load the settings to populate the form
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.monitor_combo_box.clear()
        self.monitor_combo_box.addItems(self.screens.get_screen_list())
        monitor_number = settings.value('monitor')
        self.monitor_combo_box.setCurrentIndex(monitor_number)
        self.number_edit.setText(settings.value('ccli number'))
        self.username_edit.setText(settings.value('songselect username'))
        self.password_edit.setText(settings.value('songselect password'))
        self.save_check_service_check_box.setChecked(settings.value('save prompt'))
        self.auto_unblank_check_box.setChecked(settings.value('auto unblank'))
        self.display_on_monitor_check.setChecked(self.screens.display)
        self.warning_check_box.setChecked(settings.value('blank warning'))
        self.auto_open_check_box.setChecked(settings.value('auto open'))
        self.show_splash_check_box.setChecked(settings.value('show splash'))
        self.check_for_updates_check_box.setChecked(settings.value('update check'))
        self.auto_preview_check_box.setChecked(settings.value('auto preview'))
        self.timeout_spin_box.setValue(settings.value('loop delay'))
        self.monitor_radio_button.setChecked(not settings.value('override position',))
        self.override_radio_button.setChecked(settings.value('override position'))
        self.custom_X_value_edit.setValue(settings.value('x position'))
        self.custom_Y_value_edit.setValue(settings.value('y position'))
        self.custom_height_value_edit.setValue(settings.value('height'))
        self.custom_width_value_edit.setValue(settings.value('width'))
        self.start_paused_check_box.setChecked(settings.value('audio start paused'))
        self.repeat_list_check_box.setChecked(settings.value('audio repeat list'))
        settings.endGroup()
        self.monitor_combo_box.setDisabled(self.override_radio_button.isChecked())
        self.custom_X_value_edit.setEnabled(self.override_radio_button.isChecked())
        self.custom_Y_value_edit.setEnabled(self.override_radio_button.isChecked())
        self.custom_height_value_edit.setEnabled(self.override_radio_button.isChecked())
        self.custom_width_value_edit.setEnabled(self.override_radio_button.isChecked())
        self.display_changed = False

    def save(self):
        """
        Save the settings from the form
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('monitor', self.monitor_combo_box.currentIndex())
        settings.setValue('display on monitor', self.display_on_monitor_check.isChecked())
        settings.setValue('blank warning', self.warning_check_box.isChecked())
        settings.setValue('auto open', self.auto_open_check_box.isChecked())
        settings.setValue('show splash', self.show_splash_check_box.isChecked())
        settings.setValue('update check', self.check_for_updates_check_box.isChecked())
        settings.setValue('save prompt', self.save_check_service_check_box.isChecked())
        settings.setValue('auto unblank', self.auto_unblank_check_box.isChecked())
        settings.setValue('auto preview', self.auto_preview_check_box.isChecked())
        settings.setValue('loop delay', self.timeout_spin_box.value())
        settings.setValue('ccli number', self.number_edit.displayText())
        settings.setValue('songselect username', self.username_edit.displayText())
        settings.setValue('songselect password', self.password_edit.displayText())
        settings.setValue('x position', self.custom_X_value_edit.value())
        settings.setValue('y position', self.custom_Y_value_edit.value())
        settings.setValue('height', self.custom_height_value_edit.value())
        settings.setValue('width', self.custom_width_value_edit.value())
        settings.setValue('override position', self.override_radio_button.isChecked())
        settings.setValue('audio start paused', self.start_paused_check_box.isChecked())
        settings.setValue('audio repeat list', self.repeat_list_check_box.isChecked())
        settings.endGroup()
        # On save update the screens as well
        self.post_set_up(True)

    def post_set_up(self, postUpdate=False):
        """
        Apply settings after settings tab has loaded and most of the system so must be delayed
        """
        self.settings_form.register_post_process('slidecontroller_live_spin_delay')
        # Do not continue on start up.
        if not postUpdate:
            return
        self.screens.set_current_display(self.monitor_combo_box.currentIndex())
        self.screens.display = self.display_on_monitor_check.isChecked()
        self.screens.override['size'] = QtCore.QRect(
            self.custom_X_value_edit.value(),
            self.custom_Y_value_edit.value(),
            self.custom_width_value_edit.value(),
            self.custom_height_value_edit.value())
        if self.override_radio_button.isChecked():
            self.screens.set_override_display()
        else:
            self.screens.reset_current_display()
        if self.display_changed:
            self.settings_form.register_post_process('config_screen_changed')
        self.display_changed = False

    def on_override_radio_button_pressed(self, checked):
        """
        Toggle screen state depending on check box state.

        :param checked: The state of the check box (boolean).
        """
        self.monitor_combo_box.setDisabled(checked)
        self.custom_X_value_edit.setEnabled(checked)
        self.custom_Y_value_edit.setEnabled(checked)
        self.custom_height_value_edit.setEnabled(checked)
        self.custom_width_value_edit.setEnabled(checked)
        self.display_changed = True

    def on_display_changed(self):
        """
        Called when the width, height, x position or y position has changed.
        """
        self.display_changed = True
