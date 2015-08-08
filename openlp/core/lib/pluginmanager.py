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
Provide plugin management
"""
import os
import sys
import imp

from openlp.core.lib import Plugin, PluginStatus
from openlp.core.common import AppLocation, RegistryProperties, OpenLPMixin, RegistryMixin


class PluginManager(RegistryMixin, OpenLPMixin, RegistryProperties):
    """
    This is the Plugin manager, which loads all the plugins,
    and executes all the hooks, as and when necessary.
    """
    def __init__(self, parent=None):
        """
        The constructor for the plugin manager. Passes the controllers on to
        the plugins for them to interact with via their ServiceItems.
        """
        super(PluginManager, self).__init__(parent)
        self.log_info('Plugin manager Initialising')
        self.base_path = os.path.abspath(AppLocation.get_directory(AppLocation.PluginsDir))
        self.log_debug('Base path %s ' % self.base_path)
        self.plugins = []
        self.log_info('Plugin manager Initialised')

    def bootstrap_initialise(self):
        """
        Bootstrap all the plugin manager functions
        """
        self.find_plugins()
        # hook methods have to happen after find_plugins. Find plugins needs
        # the controllers hence the hooks have moved from setupUI() to here
        # Find and insert settings tabs
        self.hook_settings_tabs()
        # Find and insert media manager items
        self.hook_media_manager()
        # Call the hook method to pull in import menus.
        self.hook_import_menu()
        # Call the hook method to pull in export menus.
        self.hook_export_menu()
        # Call the hook method to pull in tools menus.
        self.hook_tools_menu()
        # Call the initialise method to setup plugins.
        self.initialise_plugins()

    def find_plugins(self):
        """
        Scan a directory for objects inheriting from the ``Plugin`` class.
        """
        start_depth = len(os.path.abspath(self.base_path).split(os.sep))
        present_plugin_dir = os.path.join(self.base_path, 'presentations')
        self.log_debug('finding plugins in %s at depth %d' % (self.base_path, start_depth))
        for root, dirs, files in os.walk(self.base_path):
            for name in files:
                if name.endswith('.py') and not name.startswith('__'):
                    path = os.path.abspath(os.path.join(root, name))
                    this_depth = len(path.split(os.sep))
                    if this_depth - start_depth > 2:
                        # skip anything lower down
                        break
                    module_name = name[:-3]
                    # import the modules
                    self.log_debug('Importing %s from %s. Depth %d' % (module_name, root, this_depth))
                    try:
                        # Use the "imp" library to try to get around a problem with the PyUNO library which
                        # monkey-patches the __import__ function to do some magic. This causes issues with our tests.
                        # First, try to find the module we want to import, searching the directory in root
                        fp, path_name, description = imp.find_module(module_name, [root])
                        # Then load the module (do the actual import) using the details from find_module()
                        imp.load_module(module_name, fp, path_name, description)
                    except ImportError as e:
                        self.log_exception('Failed to import module %s on path %s: %s'
                                           % (module_name, path, e.args[0]))
        plugin_classes = Plugin.__subclasses__()
        plugin_objects = []
        for p in plugin_classes:
            try:
                plugin = p()
                self.log_debug('Loaded plugin %s' % str(p))
                plugin_objects.append(plugin)
            except TypeError:
                self.log_exception('Failed to load plugin %s' % str(p))
        plugins_list = sorted(plugin_objects, key=lambda plugin: plugin.weight)
        for plugin in plugins_list:
            if plugin.check_pre_conditions():
                self.log_debug('Plugin %s active' % str(plugin.name))
                plugin.set_status()
            else:
                plugin.status = PluginStatus.Disabled
            self.plugins.append(plugin)

    def hook_media_manager(self):
        """
        Create the plugins' media manager items.
        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.create_media_manager_item()

    def hook_settings_tabs(self):
        """
        Loop through all the plugins. If a plugin has a valid settings tab
        item, add it to the settings tab.
        Tabs are set for all plugins not just Active ones

        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.create_settings_tab(self.settings_form)

    def hook_import_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the import menu.

        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.add_import_menu_item(self.main_window.file_import_menu)

    def hook_export_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the export menu.
        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.add_export_menu_item(self.main_window.file_export_menu)

    def hook_tools_menu(self):
        """
        Loop through all the plugins and give them an opportunity to add an
        item to the tools menu.
        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.add_tools_menu_item(self.main_window.tools_menu)

    def hook_upgrade_plugin_settings(self, settings):
        """
        Loop through all the plugins and give them an opportunity to upgrade their settings.

        :param settings: The Settings object containing the old settings.
        """
        for plugin in self.plugins:
            if plugin.status is not PluginStatus.Disabled:
                plugin.upgrade_settings(settings)

    def initialise_plugins(self):
        """
        Loop through all the plugins and give them an opportunity to initialise themselves.
        """
        for plugin in self.plugins:
            self.log_info('initialising plugins %s in a %s state' % (plugin.name, plugin.is_active()))
            if plugin.is_active():
                plugin.initialise()
                self.log_info('Initialisation Complete for %s ' % plugin.name)

    def finalise_plugins(self):
        """
        Loop through all the plugins and give them an opportunity to clean themselves up
        """
        for plugin in self.plugins:
            if plugin.is_active():
                plugin.finalise()
                self.log_info('Finalisation Complete for %s ' % plugin.name)

    def get_plugin_by_name(self, name):
        """
        Return the plugin which has a name with value ``name``.
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    def new_service_created(self):
        """
        Loop through all the plugins and give them an opportunity to handle a new service
        """
        for plugin in self.plugins:
            if plugin.is_active():
                plugin.new_service_created()
