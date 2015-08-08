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
Package to test the openlp.core.lib.pluginmanager package.
"""
from unittest import TestCase

from openlp.core.common import Registry, Settings
from openlp.core.lib.pluginmanager import PluginManager
from openlp.core.lib import PluginStatus
from tests.functional import MagicMock


class TestPluginManager(TestCase):
    """
    Test the PluginManager class
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        self.mocked_main_window = MagicMock()
        self.mocked_main_window.file_import_menu.return_value = None
        self.mocked_main_window.file_export_menu.return_value = None
        self.mocked_main_window.file_export_menu.return_value = None
        self.mocked_settings_form = MagicMock()
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('main_window', self.mocked_main_window)
        Registry().register('settings_form', self.mocked_settings_form)

    def hook_media_manager_with_disabled_plugin_test(self):
        """
        Test running the hook_media_manager() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_media_manager()
        plugin_manager.hook_media_manager()

        # THEN: The create_media_manager_item() method should have been called
        self.assertEqual(0, mocked_plugin.create_media_manager_item.call_count,
                         'The create_media_manager_item() method should not have been called.')

    def hook_media_manager_with_active_plugin_test(self):
        """
        Test running the hook_media_manager() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_media_manager()
        plugin_manager.hook_media_manager()

        # THEN: The create_media_manager_item() method should have been called
        mocked_plugin.create_media_manager_item.assert_called_with()

    def hook_settings_tabs_with_disabled_plugin_and_no_form_test(self):
        """
        Test running the hook_settings_tabs() method with a disabled plugin and no form
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_settings_tabs()
        plugin_manager.hook_settings_tabs()

        # THEN: The hook_settings_tabs() method should have been called
        self.assertEqual(0, mocked_plugin.create_media_manager_item.call_count,
                         'The create_media_manager_item() method should not have been called.')

    def hook_settings_tabs_with_disabled_plugin_and_mocked_form_test(self):
        """
        Test running the hook_settings_tabs() method with a disabled plugin and a mocked form
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]
        mocked_settings_form = MagicMock()
        # Replace the autoloaded plugin with the version for testing in real code this would error
        mocked_settings_form.plugin_manager = plugin_manager

        # WHEN: We run hook_settings_tabs()
        plugin_manager.hook_settings_tabs()

        # THEN: The create_settings_tab() method should not have been called, but the plugins lists should be the same
        self.assertEqual(0, mocked_plugin.create_settings_tab.call_count,
                         'The create_media_manager_item() method should not have been called.')
        self.assertEqual(mocked_settings_form.plugin_manager.plugins, plugin_manager.plugins,
                         'The plugins on the settings form should be the same as the plugins in the plugin manager')

    def hook_settings_tabs_with_active_plugin_and_mocked_form_test(self):
        """
        Test running the hook_settings_tabs() method with an active plugin and a mocked settings form
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]
        mocked_settings_form = MagicMock()
        # Replace the autoloaded plugin with the version for testing in real code this would error
        mocked_settings_form.plugin_manager = plugin_manager

        # WHEN: We run hook_settings_tabs()
        plugin_manager.hook_settings_tabs()

        # THEN: The create_media_manager_item() method should have been called with the mocked settings form
        self.assertEqual(1, mocked_plugin.create_settings_tab.call_count,
                         'The create_media_manager_item() method should have been called once.')
        self.assertEqual(plugin_manager.plugins, mocked_settings_form.plugin_manager.plugins,
                         'The plugins on the settings form should be the same as the plugins in the plugin manager')

    def hook_settings_tabs_with_active_plugin_and_no_form_test(self):
        """
        Test running the hook_settings_tabs() method with an active plugin and no settings form
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_settings_tabs()
        plugin_manager.hook_settings_tabs()

        # THEN: The create_settings_tab() method should have been called
        mocked_plugin.create_settings_tab.assert_called_with(self.mocked_settings_form)

    def hook_import_menu_with_disabled_plugin_test(self):
        """
        Test running the hook_import_menu() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_import_menu()
        plugin_manager.hook_import_menu()

        # THEN: The create_media_manager_item() method should have been called
        self.assertEqual(0, mocked_plugin.add_import_menu_item.call_count,
                         'The add_import_menu_item() method should not have been called.')

    def hook_import_menu_with_active_plugin_test(self):
        """
        Test running the hook_import_menu() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_import_menu()
        plugin_manager.hook_import_menu()

        # THEN: The add_import_menu_item() method should have been called
        mocked_plugin.add_import_menu_item.assert_called_with(self.mocked_main_window.file_import_menu)

    def hook_export_menu_with_disabled_plugin_test(self):
        """
        Test running the hook_export_menu() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_export_menu()
        plugin_manager.hook_export_menu()

        # THEN: The add_export_menu_item() method should not have been called
        self.assertEqual(0, mocked_plugin.add_export_menu_item.call_count,
                         'The add_export_menu_item() method should not have been called.')

    def hook_export_menu_with_active_plugin_test(self):
        """
        Test running the hook_export_menu() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_export_menu()
        plugin_manager.hook_export_menu()

        # THEN: The add_export_menu_item() method should have been called
        mocked_plugin.add_export_menu_item.assert_called_with(self.mocked_main_window.file_export_menu)

    def hook_upgrade_plugin_settings_with_disabled_plugin_test(self):
        """
        Test running the hook_upgrade_plugin_settings() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]
        settings = Settings()

        # WHEN: We run hook_upgrade_plugin_settings()
        plugin_manager.hook_upgrade_plugin_settings(settings)

        # THEN: The upgrade_settings() method should not have been called
        self.assertEqual(0, mocked_plugin.upgrade_settings.call_count,
                         'The upgrade_settings() method should not have been called.')

    def hook_upgrade_plugin_settings_with_active_plugin_test(self):
        """
        Test running the hook_upgrade_plugin_settings() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]
        settings = Settings()

        # WHEN: We run hook_upgrade_plugin_settings()
        plugin_manager.hook_upgrade_plugin_settings(settings)

        # THEN: The add_export_menu_item() method should have been called
        mocked_plugin.upgrade_settings.assert_called_with(settings)

    def hook_tools_menu_with_disabled_plugin_test(self):
        """
        Test running the hook_tools_menu() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_tools_menu()
        plugin_manager.hook_tools_menu()

        # THEN: The add_tools_menu_item() method should have been called
        self.assertEqual(0, mocked_plugin.add_tools_menu_item.call_count,
                         'The add_tools_menu_item() method should not have been called.')

    def hook_tools_menu_with_active_plugin_test(self):
        """
        Test running the hook_tools_menu() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run hook_tools_menu()
        plugin_manager.hook_tools_menu()

        # THEN: The add_tools_menu_item() method should have been called
        mocked_plugin.add_tools_menu_item.assert_called_with(self.mocked_main_window.tools_menu)

    def initialise_plugins_with_disabled_plugin_test(self):
        """
        Test running the initialise_plugins() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        mocked_plugin.is_active.return_value = False
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run initialise_plugins()
        plugin_manager.initialise_plugins()

        # THEN: The is_active() method should have been called, and initialise() method should NOT have been called
        mocked_plugin.is_active.assert_called_with()
        self.assertEqual(0, mocked_plugin.initialise.call_count, 'The initialise() method should not have been called.')

    def initialise_plugins_with_active_plugin_test(self):
        """
        Test running the initialise_plugins() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        mocked_plugin.is_active.return_value = True
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run initialise_plugins()
        plugin_manager.initialise_plugins()

        # THEN: The is_active() and initialise() methods should have been called
        mocked_plugin.is_active.assert_called_with()
        mocked_plugin.initialise.assert_called_with()

    def finalise_plugins_with_disabled_plugin_test(self):
        """
        Test running the finalise_plugins() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        mocked_plugin.is_active.return_value = False
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run finalise_plugins()
        plugin_manager.finalise_plugins()

        # THEN: The is_active() method should have been called, and initialise() method should NOT have been called
        mocked_plugin.is_active.assert_called_with()
        self.assertEqual(0, mocked_plugin.finalise.call_count, 'The finalise() method should not have been called.')

    def finalise_plugins_with_active_plugin_test(self):
        """
        Test running the finalise_plugins() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        mocked_plugin.is_active.return_value = True
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run finalise_plugins()
        plugin_manager.finalise_plugins()

        # THEN: The is_active() and finalise() methods should have been called
        mocked_plugin.is_active.assert_called_with()
        mocked_plugin.finalise.assert_called_with()

    def get_plugin_by_name_does_not_exist_test(self):
        """
        Test running the get_plugin_by_name() method to find a plugin that does not exist
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.name = 'Mocked Plugin'
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run finalise_plugins()
        result = plugin_manager.get_plugin_by_name('Missing Plugin')

        # THEN: The is_active() and finalise() methods should have been called
        self.assertIsNone(result, 'The result for get_plugin_by_name should be None')

    def get_plugin_by_name_exists_test(self):
        """
        Test running the get_plugin_by_name() method to find a plugin that exists
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.name = 'Mocked Plugin'
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run finalise_plugins()
        result = plugin_manager.get_plugin_by_name('Mocked Plugin')

        # THEN: The is_active() and finalise() methods should have been called
        self.assertEqual(result, mocked_plugin, 'The result for get_plugin_by_name should be the mocked plugin')

    def new_service_created_with_disabled_plugin_test(self):
        """
        Test running the new_service_created() method with a disabled plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Disabled
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Disabled
        mocked_plugin.is_active.return_value = False
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run finalise_plugins()
        plugin_manager.new_service_created()

        # THEN: The isActive() method should have been called, and initialise() method should NOT have been called
        mocked_plugin.is_active.assert_called_with()
        self.assertEqual(0, mocked_plugin.new_service_created.call_count,
                         'The new_service_created() method should not have been called.')

    def new_service_created_with_active_plugin_test(self):
        """
        Test running the new_service_created() method with an active plugin
        """
        # GIVEN: A PluginManager instance and a list with a mocked up plugin whose status is set to Active
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        mocked_plugin.is_active.return_value = True
        plugin_manager = PluginManager()
        plugin_manager.plugins = [mocked_plugin]

        # WHEN: We run new_service_created()
        plugin_manager.new_service_created()

        # THEN: The is_active() and finalise() methods should have been called
        mocked_plugin.is_active.assert_called_with()
        mocked_plugin.new_service_created.assert_called_with()
