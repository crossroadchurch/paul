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
The :mod:`~openlp.core.ui.media.playertab` module holds the configuration tab for the media stuff.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, Settings, UiStrings, translate
from openlp.core.lib import ColorButton, SettingsTab
from openlp.core.lib.ui import create_button
from openlp.core.ui.media import get_media_players, set_media_players


class MediaQCheckBox(QtGui.QCheckBox):
    """
    MediaQCheckBox adds an extra property, player_name to the QCheckBox class.
    """
    def set_player_name(self, name):
        """
        Set the player name
        """
        self.player_name = name


class PlayerTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.media_players = Registry().get('media_controller').media_players
        self.saved_used_players = None
        self.icon_path = ':/media/multimedia-player.png'
        player_translated = translate('OpenLP.PlayerTab', 'Players')
        super(PlayerTab, self).__init__(parent, 'Players', player_translated)

    def setupUi(self):
        """
        Set up the UI
        """
        self.setObjectName('MediaTab')
        super(PlayerTab, self).setupUi()
        self.background_color_group_box = QtGui.QGroupBox(self.left_column)
        self.background_color_group_box.setObjectName('background_color_group_box')
        self.form_layout = QtGui.QFormLayout(self.background_color_group_box)
        self.form_layout.setObjectName('form_layout')
        self.color_layout = QtGui.QHBoxLayout()
        self.background_color_label = QtGui.QLabel(self.background_color_group_box)
        self.background_color_label.setObjectName('background_color_label')
        self.color_layout.addWidget(self.background_color_label)
        self.background_color_button = ColorButton(self.background_color_group_box)
        self.background_color_button.setObjectName('background_color_button')
        self.color_layout.addWidget(self.background_color_button)
        self.form_layout.addRow(self.color_layout)
        self.information_label = QtGui.QLabel(self.background_color_group_box)
        self.information_label.setObjectName('information_label')
        self.information_label.setWordWrap(True)
        self.form_layout.addRow(self.information_label)
        self.left_layout.addWidget(self.background_color_group_box)
        self.right_column.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.media_player_group_box = QtGui.QGroupBox(self.left_column)
        self.media_player_group_box.setObjectName('media_player_group_box')
        self.media_player_layout = QtGui.QVBoxLayout(self.media_player_group_box)
        self.media_player_layout.setObjectName('media_player_layout')
        self.player_check_boxes = {}
        self.left_layout.addWidget(self.media_player_group_box)
        self.player_order_group_box = QtGui.QGroupBox(self.left_column)
        self.player_order_group_box.setObjectName('player_order_group_box')
        self.player_order_layout = QtGui.QHBoxLayout(self.player_order_group_box)
        self.player_order_layout.setObjectName('player_order_layout')
        self.player_order_list_widget = QtGui.QListWidget(self.player_order_group_box)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.player_order_list_widget.sizePolicy().hasHeightForWidth())
        self.player_order_list_widget.setSizePolicy(size_policy)
        self.player_order_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.player_order_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.player_order_list_widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.player_order_list_widget.setObjectName('player_order_list_widget')
        self.player_order_layout.addWidget(self.player_order_list_widget)
        self.ordering_button_layout = QtGui.QVBoxLayout()
        self.ordering_button_layout.setObjectName('ordering_button_layout')
        self.ordering_button_layout.addStretch(1)
        self.ordering_up_button = create_button(self, 'ordering_up_button', role='up',
                                                click=self.on_up_button_clicked)
        self.ordering_down_button = create_button(self, 'ordering_down_button', role='down',
                                                  click=self.on_down_button_clicked)
        self.ordering_button_layout.addWidget(self.ordering_up_button)
        self.ordering_button_layout.addWidget(self.ordering_down_button)
        self.ordering_button_layout.addStretch(1)
        self.player_order_layout.addLayout(self.ordering_button_layout)
        self.left_layout.addWidget(self.player_order_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        # Signals and slots
        self.background_color_button.colorChanged.connect(self.on_background_color_changed)

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.media_player_group_box.setTitle(translate('OpenLP.PlayerTab', 'Available Media Players'))
        self.player_order_group_box.setTitle(translate('OpenLP.PlayerTab', 'Player Search Order'))
        self.background_color_group_box.setTitle(UiStrings().BackgroundColor)
        self.background_color_label.setText(UiStrings().DefaultColor)
        self.information_label.setText(translate('OpenLP.PlayerTab',
                                       'Visible background for videos with aspect ratio different to screen.'))
        self.retranslate_players()

    def on_background_color_changed(self, color):
        """
        Set the background color
        """
        self.background_color = color

    def on_player_check_box_changed(self, check_state):
        """
        Add or remove players depending on their status
        """
        player = self.sender().player_name
        if check_state == QtCore.Qt.Checked:
            if player not in self.used_players:
                self.used_players.append(player)
        else:
            if player in self.used_players:
                self.used_players.remove(player)
        self.update_player_list()

    def update_player_list(self):
        """
        Update the list of media players
        """
        self.player_order_list_widget.clear()
        for player in self.used_players:
            if player in list(self.player_check_boxes.keys()):
                if len(self.used_players) == 1:
                    # At least one media player has to stay active
                    self.player_check_boxes['%s' % player].setEnabled(False)
                else:
                    self.player_check_boxes['%s' % player].setEnabled(True)
                self.player_order_list_widget.addItem(self.media_players[str(player)].original_name)

    def on_up_button_clicked(self):
        """
        Move a media player up in the order
        """
        row = self.player_order_list_widget.currentRow()
        if row <= 0:
            return
        item = self.player_order_list_widget.takeItem(row)
        self.player_order_list_widget.insertItem(row - 1, item)
        self.player_order_list_widget.setCurrentRow(row - 1)
        self.used_players.insert(row - 1, self.used_players.pop(row))

    def on_down_button_clicked(self):
        """
        Move a media player down in the order
        """
        row = self.player_order_list_widget.currentRow()
        if row == -1 or row > self.player_order_list_widget.count() - 1:
            return
        item = self.player_order_list_widget.takeItem(row)
        self.player_order_list_widget.insertItem(row + 1, item)
        self.player_order_list_widget.setCurrentRow(row + 1)
        self.used_players.insert(row + 1, self.used_players.pop(row))

    def load(self):
        """
        Load the settings
        """
        if self.saved_used_players:
            self.used_players = self.saved_used_players
        self.used_players = get_media_players()[0]
        self.saved_used_players = self.used_players
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.update_player_list()
        self.background_color = settings.value('background color')
        self.initial_color = self.background_color
        settings.endGroup()
        self.background_color_button.color = self.background_color

    def save(self):
        """
        Save the settings
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('background color', self.background_color)
        settings.endGroup()
        old_players, override_player = get_media_players()
        if self.used_players != old_players:
            # clean old Media stuff
            set_media_players(self.used_players, override_player)
            self.settings_form.register_post_process('mediaitem_suffix_reset')
            self.settings_form.register_post_process('mediaitem_media_rebuild')
            self.settings_form.register_post_process('config_screen_changed')

    def post_set_up(self):
        """
        Late setup for players as the MediaController has to be initialised first.
        """
        for key, player in self.media_players.items():
            player = self.media_players[key]
            checkbox = MediaQCheckBox(self.media_player_group_box)
            checkbox.setEnabled(player.available)
            checkbox.setObjectName(player.name + '_check_box')
            checkbox.setToolTip(player.get_info())
            checkbox.set_player_name(player.name)
            self.player_check_boxes[player.name] = checkbox
            checkbox.stateChanged.connect(self.on_player_check_box_changed)
            self.media_player_layout.addWidget(checkbox)
            if player.available and player.name in self.used_players:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        self.update_player_list()
        self.retranslate_players()

    def retranslate_players(self):
        """
        Translations for players is dependent on  their setup as well
         """
        for key in self.media_players and self.player_check_boxes:
            player = self.media_players[key]
            checkbox = self.player_check_boxes[player.name]
            checkbox.set_player_name(player.name)
            if player.available:
                checkbox.setText(player.display_name)
            else:
                checkbox.setText(translate('OpenLP.PlayerTab', '%s (unavailable)') % player.display_name)
