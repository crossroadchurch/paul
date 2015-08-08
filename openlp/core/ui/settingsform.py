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
The :mod:`settingsform` provides a user interface for the OpenLP settings
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties
from openlp.core.lib import build_icon
from openlp.core.ui import AdvancedTab, GeneralTab, ThemesTab
from openlp.core.ui.media import PlayerTab
from .settingsdialog import Ui_SettingsDialog
from openlp.core.ui.projector.tab import ProjectorTab

log = logging.getLogger(__name__)


class SettingsForm(QtGui.QDialog, Ui_SettingsDialog, RegistryProperties):
    """
    Provide the form to manipulate the settings for OpenLP
    """
    def __init__(self, parent=None):
        """
        Initialise the settings form
        """
        Registry().register('settings_form', self)
        Registry().register_function('bootstrap_post_set_up', self.bootstrap_post_set_up)
        super(SettingsForm, self).__init__(parent)
        self.processes = []
        self.setupUi(self)
        self.setting_list_widget.currentRowChanged.connect(self.list_item_changed)
        self.general_tab = None
        self.themes_tab = None
        self.projector_tab = None
        self.advanced_tab = None
        self.player_tab = None

    def exec_(self):
        """
        Execute the form
        """
        # load all the settings
        self.setting_list_widget.clear()
        while self.stacked_layout.count():
            # take at 0 and the rest shuffle up.
            self.stacked_layout.takeAt(0)
        self.insert_tab(self.general_tab)
        self.insert_tab(self.themes_tab)
        self.insert_tab(self.advanced_tab)
        self.insert_tab(self.player_tab)
        self.insert_tab(self.projector_tab)
        for plugin in self.plugin_manager.plugins:
            if plugin.settings_tab:
                self.insert_tab(plugin.settings_tab, plugin.is_active())
        self.setting_list_widget.setCurrentRow(0)
        return QtGui.QDialog.exec_(self)

    def insert_tab(self, tab_widget, is_visible=True):
        """
        Add a tab to the form at a specific location

        :param tab_widget: The widget to add
        :param is_visible: If this tab should be visible
        """
        log.debug('Inserting %s tab' % tab_widget.tab_title)
        # add the tab to get it to display in the correct part of the screen
        self.stacked_layout.addWidget(tab_widget)
        if is_visible:
            list_item = QtGui.QListWidgetItem(build_icon(tab_widget.icon_path), tab_widget.tab_title_visible)
            list_item.setData(QtCore.Qt.UserRole, tab_widget.tab_title)
            self.setting_list_widget.addItem(list_item)

    def accept(self):
        """
        Process the form saving the settings
        """
        log.debug('Processing settings exit')
        # We add all the forms into the stacked layout, even if the plugin is inactive,
        # but we don't add the item to the list on the side if the plugin is inactive,
        # so loop through the list items, and then find the tab for that item.
        for item_index in range(self.setting_list_widget.count()):
            # Get the list item
            list_item = self.setting_list_widget.item(item_index)
            if not list_item:
                continue
            # Now figure out if there's a tab for it, and save the tab.
            plugin_name = list_item.data(QtCore.Qt.UserRole)
            for tab_index in range(self.stacked_layout.count()):
                tab_widget = self.stacked_layout.widget(tab_index)
                if tab_widget.tab_title == plugin_name:
                    tab_widget.save()
        # if the image background has been changed we need to regenerate the image cache
        if 'images_config_updated' in self.processes or 'config_screen_changed' in self.processes:
            self.register_post_process('images_regenerate')
        # Now lets process all the post save handlers
        while self.processes:
            Registry().execute(self.processes.pop(0))
        return QtGui.QDialog.accept(self)

    def reject(self):
        """
        Process the form saving the settings
        """
        self.processes = []
        # Same as accept(), we need to loop over the visible tabs, and skip the inactive ones
        for item_index in range(self.setting_list_widget.count()):
            # Get the list item
            list_item = self.setting_list_widget.item(item_index)
            if not list_item:
                continue
            # Now figure out if there's a tab for it, and save the tab.
            plugin_name = list_item.data(QtCore.Qt.UserRole)
            for tab_index in range(self.stacked_layout.count()):
                tab_widget = self.stacked_layout.widget(tab_index)
                if tab_widget.tab_title == plugin_name:
                    tab_widget.cancel()
        return QtGui.QDialog.reject(self)

    def bootstrap_post_set_up(self):
        """
        Run any post-setup code for the tabs on the form
        """
        # General tab
        self.general_tab = GeneralTab(self)
        # Themes tab
        self.themes_tab = ThemesTab(self)
        # Projector Tab
        self.projector_tab = ProjectorTab(self)
        # Advanced tab
        self.advanced_tab = AdvancedTab(self)
        # Advanced tab
        self.player_tab = PlayerTab(self)
        self.general_tab.post_set_up()
        self.themes_tab.post_set_up()
        self.advanced_tab.post_set_up()
        self.player_tab.post_set_up()
        for plugin in self.plugin_manager.plugins:
            if plugin.settings_tab:
                plugin.settings_tab.post_set_up()

    def list_item_changed(self, item_index):
        """
        A different settings tab is selected

        :param item_index: The index of the item that was selected
        """
        # Get the item we clicked on
        list_item = self.setting_list_widget.item(item_index)
        # Quick exit to the left if the item doesn't exist (maybe -1?)
        if not list_item:
            return
        # Loop through the list of tabs in the stacked layout
        for tab_index in range(self.stacked_layout.count()):
            # Get the widget
            tab_widget = self.stacked_layout.itemAt(tab_index).widget()
            # Check that the title of the tab (i.e. plugin name) is the same as the data in the list item
            if tab_widget.tab_title == list_item.data(QtCore.Qt.UserRole):
                # Make the matching tab visible
                self.stacked_layout.setCurrentIndex(tab_index)
                self.stacked_layout.currentWidget().tab_visible()

    def register_post_process(self, function):
        """
        Register for updates to be done on save removing duplicate functions

        :param function:  The function to be called
        """
        if function not in self.processes:
            self.processes.append(function)
