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
from openlp.core.lib import ColorButton, SettingsTab
from openlp.core.lib.ui import create_valign_selection_widgets


class AlertsTab(SettingsTab):
    """
    AlertsTab is the alerts settings tab in the settings dialog.
    """
    def __init__(self, parent, name, visible_title, icon_path):
        super(AlertsTab, self).__init__(parent, name, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('AlertsTab')
        super(AlertsTab, self).setupUi()
        self.font_group_box = QtGui.QGroupBox(self.left_column)
        self.font_group_box.setObjectName('font_group_box')
        self.font_layout = QtGui.QFormLayout(self.font_group_box)
        self.font_layout.setObjectName('font_layout')
        self.font_label = QtGui.QLabel(self.font_group_box)
        self.font_label.setObjectName('font_label')
        self.font_combo_box = QtGui.QFontComboBox(self.font_group_box)
        self.font_combo_box.setObjectName('font_combo_box')
        self.font_layout.addRow(self.font_label, self.font_combo_box)
        self.font_color_label = QtGui.QLabel(self.font_group_box)
        self.font_color_label.setObjectName('font_color_label')
        self.color_layout = QtGui.QHBoxLayout()
        self.color_layout.setObjectName('color_layout')
        self.font_color_button = ColorButton(self.font_group_box)
        self.font_color_button.setObjectName('font_color_button')
        self.color_layout.addWidget(self.font_color_button)
        self.color_layout.addSpacing(20)
        self.background_color_label = QtGui.QLabel(self.font_group_box)
        self.background_color_label.setObjectName('background_color_label')
        self.color_layout.addWidget(self.background_color_label)
        self.background_color_button = ColorButton(self.font_group_box)
        self.background_color_button.setObjectName('background_color_button')
        self.color_layout.addWidget(self.background_color_button)
        self.font_layout.addRow(self.font_color_label, self.color_layout)
        self.font_size_label = QtGui.QLabel(self.font_group_box)
        self.font_size_label.setObjectName('font_size_label')
        self.font_size_spin_box = QtGui.QSpinBox(self.font_group_box)
        self.font_size_spin_box.setObjectName('font_size_spin_box')
        self.font_layout.addRow(self.font_size_label, self.font_size_spin_box)
        self.timeout_label = QtGui.QLabel(self.font_group_box)
        self.timeout_label.setObjectName('timeout_label')
        self.timeout_spin_box = QtGui.QSpinBox(self.font_group_box)
        self.timeout_spin_box.setMaximum(180)
        self.timeout_spin_box.setObjectName('timeout_spin_box')
        self.font_layout.addRow(self.timeout_label, self.timeout_spin_box)
        self.vertical_label, self.vertical_combo_box = create_valign_selection_widgets(self.font_group_box)
        self.vertical_label.setObjectName('vertical_label')
        self.vertical_combo_box.setObjectName('vertical_combo_box')
        self.font_layout.addRow(self.vertical_label, self.vertical_combo_box)
        self.left_layout.addWidget(self.font_group_box)
        self.left_layout.addStretch()
        self.preview_group_box = QtGui.QGroupBox(self.right_column)
        self.preview_group_box.setObjectName('preview_group_box')
        self.preview_layout = QtGui.QVBoxLayout(self.preview_group_box)
        self.preview_layout.setObjectName('preview_layout')
        self.font_preview = QtGui.QLineEdit(self.preview_group_box)
        self.font_preview.setObjectName('font_preview')
        self.preview_layout.addWidget(self.font_preview)
        self.right_layout.addWidget(self.preview_group_box)
        self.right_layout.addStretch()
        # Signals and slots
        self.background_color_button.colorChanged.connect(self.on_background_color_changed)
        self.font_color_button.colorChanged.connect(self.on_font_color_changed)
        self.font_combo_box.activated.connect(self.on_font_combo_box_clicked)
        self.timeout_spin_box.valueChanged.connect(self.on_timeout_spin_box_changed)
        self.font_size_spin_box.valueChanged.connect(self.on_font_size_spin_box_changed)

    def retranslateUi(self):
        self.font_group_box.setTitle(translate('AlertsPlugin.AlertsTab', 'Font'))
        self.font_label.setText(translate('AlertsPlugin.AlertsTab', 'Font name:'))
        self.font_color_label.setText(translate('AlertsPlugin.AlertsTab', 'Font color:'))
        self.background_color_label.setText(translate('AlertsPlugin.AlertsTab', 'Background color:'))
        self.font_size_label.setText(translate('AlertsPlugin.AlertsTab', 'Font size:'))
        self.font_size_spin_box.setSuffix(UiStrings().FontSizePtUnit)
        self.timeout_label.setText(translate('AlertsPlugin.AlertsTab', 'Alert timeout:'))
        self.timeout_spin_box.setSuffix(UiStrings().Seconds)
        self.preview_group_box.setTitle(UiStrings().Preview)
        self.font_preview.setText(UiStrings().OLPV2x)

    def on_background_color_changed(self, color):
        """
        The background color has been changed.
        """
        self.background_color = color
        self.update_display()

    def on_font_combo_box_clicked(self):
        """
        The Font Combo was changed.
        """
        self.update_display()

    def on_font_color_changed(self, color):
        """
        The Font Color button has clicked.
        """
        self.font_color = color
        self.update_display()

    def on_timeout_spin_box_changed(self):
        """
        The Time out spin box has changed.

        """
        self.timeout = self.timeout_spin_box.value()
        self.changed = True

    def on_font_size_spin_box_changed(self):
        """
        The font size spin box has changed.
        """
        self.font_size = self.font_size_spin_box.value()
        self.update_display()

    def load(self):
        """
        Load the settings into the UI.
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.timeout = settings.value('timeout')
        self.font_color = settings.value('font color')
        self.font_size = settings.value('font size')
        self.background_color = settings.value('background color')
        self.font_face = settings.value('font face')
        self.location = settings.value('location')
        settings.endGroup()
        self.font_size_spin_box.setValue(self.font_size)
        self.timeout_spin_box.setValue(self.timeout)
        self.font_color_button.color = self.font_color
        self.background_color_button.color = self.background_color
        self.vertical_combo_box.setCurrentIndex(self.location)
        font = QtGui.QFont()
        font.setFamily(self.font_face)
        self.font_combo_box.setCurrentFont(font)
        self.update_display()
        self.changed = False

    def save(self):
        """
        Save the changes on exit of the Settings dialog.
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        # Check value has changed as no event handles this field
        if settings.value('location') != self.vertical_combo_box.currentIndex():
            self.changed = True
        settings.setValue('background color', self.background_color)
        settings.setValue('font color', self.font_color)
        settings.setValue('font size', self.font_size)
        self.font_face = self.font_combo_box.currentFont().family()
        settings.setValue('font face', self.font_face)
        settings.setValue('timeout', self.timeout)
        self.location = self.vertical_combo_box.currentIndex()
        settings.setValue('location', self.location)
        settings.endGroup()
        if self.changed:
            self.settings_form.register_post_process('update_display_css')
        self.changed = False

    def update_display(self):
        """
        Update the preview display after changes have been made,
        """
        font = QtGui.QFont()
        font.setFamily(self.font_combo_box.currentFont().family())
        font.setBold(True)
        font.setPointSize(self.font_size)
        self.font_preview.setFont(font)
        self.font_preview.setStyleSheet('background-color: %s; color: %s' % (self.background_color, self.font_color))
        self.changed = True
