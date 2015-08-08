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
Functional tests to test the AppLocation class and related methods.
"""
import copy
import os
from unittest import TestCase

from openlp.core.common import AppLocation, get_frozen_path
from tests.functional import patch

FILE_LIST = ['file1', 'file2', 'file3.txt', 'file4.txt', 'file5.mp3', 'file6.mp3']


class TestAppLocation(TestCase):
    """
    A test suite to test out various methods around the AppLocation class.
    """
    def get_data_path_test(self):
        """
        Test the AppLocation.get_data_path() method
        """
        with patch('openlp.core.common.applocation.Settings') as mocked_class, \
                patch('openlp.core.common.AppLocation.get_directory') as mocked_get_directory, \
                patch('openlp.core.common.applocation.check_directory_exists') as mocked_check_directory_exists, \
                patch('openlp.core.common.applocation.os') as mocked_os:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_directory()
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_directory.return_value = os.path.join('test', 'dir')
            mocked_check_directory_exists.return_value = True
            mocked_os.path.normpath.return_value = os.path.join('test', 'dir')

            # WHEN: we call AppLocation.get_data_path()
            data_path = AppLocation.get_data_path()

            # THEN: check that all the correct methods were called, and the result is correct
            mocked_settings.contains.assert_called_with('advanced/data path')
            mocked_get_directory.assert_called_with(AppLocation.DataDir)
            mocked_check_directory_exists.assert_called_with(os.path.join('test', 'dir'))
            self.assertEqual(os.path.join('test', 'dir'), data_path, 'Result should be "test/dir"')

    def get_data_path_with_custom_location_test(self):
        """
        Test the AppLocation.get_data_path() method when a custom location is set in the settings
        """
        with patch('openlp.core.common.applocation.Settings') as mocked_class,\
                patch('openlp.core.common.applocation.os') as mocked_os:
            # GIVEN: A mocked out Settings class which returns a custom data location
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = True
            mocked_settings.value.return_value.toString.return_value = 'custom/dir'
            mocked_os.path.normpath.return_value = 'custom/dir'

            # WHEN: we call AppLocation.get_data_path()
            data_path = AppLocation.get_data_path()

            # THEN: the mocked Settings methods were called and the value returned was our set up value
            mocked_settings.contains.assert_called_with('advanced/data path')
            mocked_settings.value.assert_called_with('advanced/data path')
            self.assertEqual('custom/dir', data_path, 'Result should be "custom/dir"')

    def get_files_no_section_no_extension_test(self):
        """
        Test the AppLocation.get_files() method with no parameters passed.
        """
        with patch('openlp.core.common.AppLocation.get_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.os.listdir') as mocked_listdir:
            # GIVEN: Our mocked modules/methods.
            mocked_get_data_path.return_value = 'test/dir'
            mocked_listdir.return_value = copy.deepcopy(FILE_LIST)

            # When: Get the list of files.
            result = AppLocation.get_files()

            # Then: check if the file lists are identical.
            self.assertListEqual(FILE_LIST, result, 'The file lists should be identical.')

    def get_files_test(self):
        """
        Test the AppLocation.get_files() method with all parameters passed.
        """
        with patch('openlp.core.common.AppLocation.get_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.os.listdir') as mocked_listdir:
            # GIVEN: Our mocked modules/methods.
            mocked_get_data_path.return_value = os.path.join('test', 'dir')
            mocked_listdir.return_value = copy.deepcopy(FILE_LIST)

            # When: Get the list of files.
            result = AppLocation.get_files('section', '.mp3')

            # Then: Check if the section parameter was used correctly.
            mocked_listdir.assert_called_with(os.path.join('test', 'dir', 'section'))

            # Then: check if the file lists are identical.
            self.assertListEqual(['file5.mp3', 'file6.mp3'], result, 'The file lists should be identical.')

    def get_section_data_path_test(self):
        """
        Test the AppLocation.get_section_data_path() method
        """
        with patch('openlp.core.common.AppLocation.get_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.check_directory_exists') as mocked_check_directory_exists:
            # GIVEN: A mocked out AppLocation.get_data_path()
            mocked_get_data_path.return_value = os.path.join('test', 'dir')
            mocked_check_directory_exists.return_value = True

            # WHEN: we call AppLocation.get_data_path()
            data_path = AppLocation.get_section_data_path('section')

            # THEN: check that all the correct methods were called, and the result is correct
            mocked_check_directory_exists.assert_called_with(os.path.join('test', 'dir', 'section'))
            self.assertEqual(os.path.join('test', 'dir', 'section'), data_path, 'Result should be "test/dir/section"')

    def get_directory_for_app_dir_test(self):
        """
        Test the AppLocation.get_directory() method for AppLocation.AppDir
        """
        # GIVEN: A mocked out _get_frozen_path function
        with patch('openlp.core.common.applocation.get_frozen_path') as mocked_get_frozen_path:
            mocked_get_frozen_path.return_value = os.path.join('app', 'dir')

            # WHEN: We call AppLocation.get_directory
            directory = AppLocation.get_directory(AppLocation.AppDir)

            # THEN: check that the correct directory is returned
            self.assertEqual(os.path.join('app', 'dir'), directory, 'Directory should be "app/dir"')

    def get_directory_for_plugins_dir_test(self):
        """
        Test the AppLocation.get_directory() method for AppLocation.PluginsDir
        """
        # GIVEN: _get_frozen_path, abspath, split and sys are mocked out
        with patch('openlp.core.common.applocation.get_frozen_path') as mocked_get_frozen_path, \
                patch('openlp.core.common.applocation.os.path.abspath') as mocked_abspath, \
                patch('openlp.core.common.applocation.os.path.split') as mocked_split, \
                patch('openlp.core.common.applocation.sys') as mocked_sys:
            mocked_abspath.return_value = os.path.join('plugins', 'dir')
            mocked_split.return_value = ['openlp']
            mocked_get_frozen_path.return_value = os.path.join('plugins', 'dir')
            mocked_sys.frozen = 1
            mocked_sys.argv = ['openlp']

            # WHEN: We call AppLocation.get_directory
            directory = AppLocation.get_directory(AppLocation.PluginsDir)

            # THEN: The correct directory should be returned
            self.assertEqual(os.path.join('plugins', 'dir'), directory, 'Directory should be "plugins/dir"')

    def get_frozen_path_in_unfrozen_app_test(self):
        """
        Test the _get_frozen_path() function when the application is not frozen (compiled by PyInstaller)
        """
        with patch('openlp.core.utils.sys') as mocked_sys:
            # GIVEN: The sys module "without" a "frozen" attribute
            mocked_sys.frozen = None

            # WHEN: We call _get_frozen_path() with two parameters
            frozen_path = get_frozen_path('frozen', 'not frozen')

            # THEN: The non-frozen parameter is returned
            self.assertEqual('not frozen', frozen_path, '_get_frozen_path should return "not frozen"')

    def get_frozen_path_in_frozen_app_test(self):
        """
        Test the get_frozen_path() function when the application is frozen (compiled by PyInstaller)
        """
        with patch('openlp.core.common.sys') as mocked_sys:
            # GIVEN: The sys module *with* a "frozen" attribute
            mocked_sys.frozen = 1

            # WHEN: We call _get_frozen_path() with two parameters
            frozen_path = get_frozen_path('frozen', 'not frozen')

            # THEN: The frozen parameter is returned
            self.assertEqual('frozen', frozen_path, 'Should return "frozen"')
