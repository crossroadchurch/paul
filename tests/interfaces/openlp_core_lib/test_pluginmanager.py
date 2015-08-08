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
import sys
import shutil
import gc
from tempfile import mkdtemp
from unittest import TestCase

from PyQt4 import QtGui

from openlp.core.common import Registry, Settings
from openlp.core.lib.pluginmanager import PluginManager
from tests.interfaces import MagicMock
from tests.helpers.testmixin import TestMixin


class TestPluginManager(TestCase, TestMixin):
    """
    Test the PluginManager class
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        Settings.setDefaultFormat(Settings.IniFormat)
        self.build_settings()
        self.temp_dir = mkdtemp('openlp')
        Settings().setValue('advanced/data path', self.temp_dir)
        Registry.create()
        Registry().register('service_list', MagicMock())
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)

    def tearDown(self):
        Settings().remove('advanced/data path')
        self.destroy_settings()
        del self.main_window
        # On windows we need to manually garbage collect to close sqlalchemy files
        # to avoid errors when temporary files are deleted.
        gc.collect()
        shutil.rmtree(self.temp_dir)

    def find_plugins_test(self):
        """
        Test the find_plugins() method to ensure it imports the correct plugins
        """
        # GIVEN: A plugin manager
        plugin_manager = PluginManager()

        # WHEN: We mock out sys.platform to make it return "darwin" and then find the plugins
        old_platform = sys.platform
        sys.platform = 'darwin'
        plugin_manager.find_plugins()
        sys.platform = old_platform

        # THEN: We should find the "Songs", "Bibles", etc in the plugins list
        plugin_names = [plugin.name for plugin in plugin_manager.plugins]
        self.assertIn('songs', plugin_names, 'There should be a "songs" plugin')
        self.assertIn('bibles', plugin_names, 'There should be a "bibles" plugin')
        self.assertIn('presentations', plugin_names, 'There should be a "presentations" plugin')
        self.assertIn('images', plugin_names, 'There should be a "images" plugin')
        self.assertIn('media', plugin_names, 'There should be a "media" plugin')
        self.assertIn('custom', plugin_names, 'There should be a "custom" plugin')
        self.assertIn('songusage', plugin_names, 'There should be a "songusage" plugin')
        self.assertIn('alerts', plugin_names, 'There should be a "alerts" plugin')
        self.assertIn('remotes', plugin_names, 'There should be a "remotes" plugin')
