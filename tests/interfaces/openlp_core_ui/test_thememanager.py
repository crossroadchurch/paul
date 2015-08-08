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
Interface tests to test the themeManager class and related methods.
"""
from unittest import TestCase

from openlp.core.common import Registry, Settings
from openlp.core.ui import ThemeManager, ThemeForm, FileRenameForm
from tests.functional import patch, MagicMock
from tests.helpers.testmixin import TestMixin


class TestThemeManager(TestCase, TestMixin):
    """
    Test the functions in the ThemeManager module
    """
    def setUp(self):
        """
        Create the UI
        """
        self.build_settings()
        self.setup_application()
        Registry.create()
        self.theme_manager = ThemeManager()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()
        del self.theme_manager

    def initialise_test(self):
        """
        Test the thememanager initialise - basic test
        """
        # GIVEN: A new a call to initialise
        self.theme_manager.build_theme_path = MagicMock()
        self.theme_manager.load_first_time_themes = MagicMock()
        Settings().setValue('themes/global theme', 'my_theme')

        # WHEN: the initialisation is run
        self.theme_manager.bootstrap_initialise()

        # THEN:
        self.assertEqual(1, self.theme_manager.build_theme_path.call_count,
                         'The function build_theme_path should have been called')
        self.assertEqual(1, self.theme_manager.load_first_time_themes.call_count,
                         'The function load_first_time_themes should have been called only once')
        self.assertEqual(self.theme_manager.global_theme, 'my_theme',
                         'The global theme should have been set to my_theme')

    def build_theme_path_test(self):
        """
        Test the thememanager build_theme_path - basic test
        """
        # GIVEN: A new a call to initialise
        with patch('openlp.core.common.applocation.check_directory_exists') as mocked_check_directory_exists:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_directory()
            mocked_check_directory_exists.return_value = True
        Settings().setValue('themes/global theme', 'my_theme')

        self.theme_manager.theme_form = MagicMock()
        self.theme_manager.load_first_time_themes = MagicMock()

        # WHEN: the build_theme_path is run
        self.theme_manager.build_theme_path()

        #  THEN:
        assert self.theme_manager.thumb_path.startswith(self.theme_manager.path) is True, \
            'The thumb path and the main path should start with the same value'

    def click_on_new_theme_test(self):
        """
        Test the on_add_theme event handler is called by the UI
        """
        # GIVEN: An initial form
        Settings().setValue('themes/global theme', 'my_theme')
        mocked_event = MagicMock()
        self.theme_manager.on_add_theme = mocked_event
        self.theme_manager.setup_ui(self.theme_manager)

        # WHEN displaying the UI and pressing cancel
        new_theme = self.theme_manager.toolbar.actions['newTheme']
        new_theme.trigger()

        assert mocked_event.call_count == 1, 'The on_add_theme method should have been called once'

    @patch('openlp.core.ui.themeform.ThemeForm._setup')
    @patch('openlp.core.ui.filerenameform.FileRenameForm._setup')
    def bootstrap_post_test(self, mocked_theme_form, mocked_rename_form):
        """
        Test the functions of bootstrap_post_setup are called.
        """
        # GIVEN:
        self.theme_manager.load_themes = MagicMock()
        self.theme_manager.path = MagicMock()

        # WHEN:
        self.theme_manager.bootstrap_post_set_up()

        # THEN:
        self.assertEqual(self.theme_manager.path, self.theme_manager.theme_form.path)
        self.assertEqual(1, self.theme_manager.load_themes.call_count, "load_themes should have been called once")
