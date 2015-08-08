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
Package to test the openlp.core.ui.thememanager package.
"""
import os
import shutil

from unittest import TestCase
from tempfile import mkdtemp

from PyQt4 import QtGui
from tempfile import mkdtemp

from openlp.core.ui import ThemeManager
from openlp.core.common import Registry

from tests.utils.constants import TEST_RESOURCES_PATH
from tests.functional import ANY, MagicMock, patch


class TestThemeManager(TestCase):

    def setUp(self):
        """
        Set up the tests
        """
        Registry.create()
        self.temp_folder = mkdtemp()

    def tearDown(self):
        """
        Clean up
        """
        shutil.rmtree(self.temp_folder)

    def export_theme_test(self):
        """
        Test exporting a theme .
        """
        # GIVEN: A new ThemeManager instance.
        theme_manager = ThemeManager()
        theme_manager.path = os.path.join(TEST_RESOURCES_PATH, 'themes')
        with patch('zipfile.ZipFile.__init__') as mocked_zipfile_init, \
                patch('zipfile.ZipFile.write') as mocked_zipfile_write:
            mocked_zipfile_init.return_value = None

            # WHEN: The theme is exported
            theme_manager._export_theme(os.path.join('some', 'path'), 'Default')

            # THEN: The zipfile should be created at the given path
            mocked_zipfile_init.assert_called_with(os.path.join('some', 'path', 'Default.otz'), 'w')
            mocked_zipfile_write.assert_called_with(os.path.join(TEST_RESOURCES_PATH, 'themes',
                                                                 'Default', 'Default.xml'),
                                                    os.path.join('Default', 'Default.xml'))

    def initial_theme_manager_test(self):
        """
        Test the instantiation of theme manager.
        """
        # GIVEN: A new service manager instance.
        ThemeManager(None)

        # WHEN: the default theme manager is built.
        # THEN: The the controller should be registered in the registry.
        self.assertIsNotNone(Registry().get('theme_manager'), 'The base theme manager should be registered')

    def write_theme_same_image_test(self):
        """
        Test that we don't try to overwrite a theme background image with itself
        """
        # GIVEN: A new theme manager instance, with mocked builtins.open, shutil.copyfile,
        #        theme, check_directory_exists and thememanager-attributes.
        with patch('builtins.open') as mocked_open, \
                patch('openlp.core.ui.thememanager.shutil.copyfile') as mocked_copyfile, \
                patch('openlp.core.ui.thememanager.check_directory_exists') as mocked_check_directory_exists:
            mocked_open.return_value = MagicMock()
            theme_manager = ThemeManager(None)
            theme_manager.old_background_image = None
            theme_manager.generate_and_save_image = MagicMock()
            theme_manager.path = ''
            mocked_theme = MagicMock()
            mocked_theme.theme_name = 'themename'
            mocked_theme.extract_formatted_xml = MagicMock()
            mocked_theme.extract_formatted_xml.return_value = 'fake_theme_xml'.encode()

            # WHEN: Calling _write_theme with path to the same image, but the path written slightly different
            file_name1 = os.path.join(TEST_RESOURCES_PATH, 'church.jpg')
            # Do replacement from end of string to avoid problems with path start
            file_name2 = file_name1[::-1].replace(os.sep, os.sep + os.sep, 2)[::-1]
            theme_manager._write_theme(mocked_theme, file_name1, file_name2)

            # THEN: The mocked_copyfile should not have been called
            self.assertFalse(mocked_copyfile.called, 'shutil.copyfile should not be called')

    def write_theme_diff_images_test(self):
        """
        Test that we do overwrite a theme background image when a new is submitted
        """
        # GIVEN: A new theme manager instance, with mocked builtins.open, shutil.copyfile,
        #        theme, check_directory_exists and thememanager-attributes.
        with patch('builtins.open') as mocked_open, \
                patch('openlp.core.ui.thememanager.shutil.copyfile') as mocked_copyfile, \
                patch('openlp.core.ui.thememanager.check_directory_exists') as mocked_check_directory_exists:
            mocked_open.return_value = MagicMock()
            theme_manager = ThemeManager(None)
            theme_manager.old_background_image = None
            theme_manager.generate_and_save_image = MagicMock()
            theme_manager.path = ''
            mocked_theme = MagicMock()
            mocked_theme.theme_name = 'themename'
            mocked_theme.extract_formatted_xml = MagicMock()
            mocked_theme.extract_formatted_xml.return_value = 'fake_theme_xml'.encode()

            # WHEN: Calling _write_theme with path to different images
            file_name1 = os.path.join(TEST_RESOURCES_PATH, 'church.jpg')
            file_name2 = os.path.join(TEST_RESOURCES_PATH, 'church2.jpg')
            theme_manager._write_theme(mocked_theme, file_name1, file_name2)

            # THEN: The mocked_copyfile should not have been called
            self.assertTrue(mocked_copyfile.called, 'shutil.copyfile should be called')

    def write_theme_special_char_name_test(self):
        """
        Test that we can save themes with special characters in the name
        """
        # GIVEN: A new theme manager instance, with mocked theme and thememanager-attributes.
        theme_manager = ThemeManager(None)
        theme_manager.old_background_image = None
        theme_manager.generate_and_save_image = MagicMock()
        theme_manager.path = self.temp_folder
        mocked_theme = MagicMock()
        mocked_theme.theme_name = 'theme 愛 name'
        mocked_theme.extract_formatted_xml = MagicMock()
        mocked_theme.extract_formatted_xml.return_value = 'fake theme 愛 XML'.encode()

        # WHEN: Calling _write_theme with a theme with a name with special characters in it
        theme_manager._write_theme(mocked_theme, None, None)

        # THEN: It should have been created
        self.assertTrue(os.path.exists(os.path.join(self.temp_folder, 'theme 愛 name', 'theme 愛 name.xml')),
                        'Theme with special characters should have been created!')

    def over_write_message_box_yes_test(self):
        """
        Test that theme_manager.over_write_message_box returns True when the user clicks yes.
        """
        # GIVEN: A patched QMessageBox.question and an instance of ThemeManager
        with patch('openlp.core.ui.thememanager.QtGui.QMessageBox.question', return_value=QtGui.QMessageBox.Yes)\
                as mocked_qmessagebox_question,\
                patch('openlp.core.ui.thememanager.translate') as mocked_translate:
            mocked_translate.side_effect = lambda context, text: text
            theme_manager = ThemeManager(None)

            # WHEN: Calling over_write_message_box with 'Theme Name'
            result = theme_manager.over_write_message_box('Theme Name')

            # THEN: over_write_message_box should return True and the message box should contain the theme name
            self.assertTrue(result)
            mocked_qmessagebox_question.assert_called_once_with(
                theme_manager, 'Theme Already Exists', 'Theme Theme Name already exists. Do you want to replace it?',
                ANY, ANY)

    def over_write_message_box_no_test(self):
        """
        Test that theme_manager.over_write_message_box returns False when the user clicks no.
        """
        # GIVEN: A patched QMessageBox.question and an instance of ThemeManager
        with patch('openlp.core.ui.thememanager.QtGui.QMessageBox.question', return_value=QtGui.QMessageBox.No)\
                as mocked_qmessagebox_question,\
                patch('openlp.core.ui.thememanager.translate') as mocked_translate:
            mocked_translate.side_effect = lambda context, text: text
            theme_manager = ThemeManager(None)

            # WHEN: Calling over_write_message_box with 'Theme Name'
            result = theme_manager.over_write_message_box('Theme Name')

            # THEN: over_write_message_box should return False and the message box should contain the theme name
            self.assertFalse(result)
            mocked_qmessagebox_question.assert_called_once_with(
                theme_manager, 'Theme Already Exists', 'Theme Theme Name already exists. Do you want to replace it?',
                ANY, ANY)

    def unzip_theme_test(self):
        """
        Test that unzipping of themes works
        """
        # GIVEN: A theme file, a output folder and some mocked out internal functions
        with patch('openlp.core.ui.thememanager.critical_error_message_box') \
                as mocked_critical_error_message_box:
            theme_manager = ThemeManager(None)
            theme_manager._create_theme_from_xml = MagicMock()
            theme_manager.generate_and_save_image = MagicMock()
            theme_manager.path = ''
            folder = mkdtemp()
            theme_file = os.path.join(TEST_RESOURCES_PATH, 'themes', 'Moss_on_tree.otz')

            # WHEN: We try to unzip it
            theme_manager.unzip_theme(theme_file, folder)

            # THEN: Files should be unpacked
            self.assertTrue(os.path.exists(os.path.join(folder, 'Moss on tree', 'Moss on tree.xml')))
            self.assertEqual(mocked_critical_error_message_box.call_count, 0, 'No errors should have happened')
            shutil.rmtree(folder)

    def unzip_theme_invalid_version_test(self):
        """
        Test that themes with invalid (< 2.0) or with no version attributes are rejected
        """
        # GIVEN: An instance of ThemeManager whilst mocking a theme that returns a theme with no version attribute
        with patch('openlp.core.ui.thememanager.zipfile.ZipFile') as mocked_zip_file,\
                patch('openlp.core.ui.thememanager.ElementTree.getroot') as mocked_getroot,\
                patch('openlp.core.ui.thememanager.XML'),\
                patch('openlp.core.ui.thememanager.critical_error_message_box') as mocked_critical_error_message_box:

            mocked_zip_file.return_value = MagicMock(**{'namelist.return_value': [os.path.join('theme', 'theme.xml')]})
            mocked_getroot.return_value = MagicMock(**{'get.return_value': None})
            theme_manager = ThemeManager(None)

            # WHEN: unzip_theme is called
            theme_manager.unzip_theme('theme.file', 'folder')

            # THEN: The critical_error_message_box should have been called
            mocked_critical_error_message_box.assert_called_once(ANY, ANY)
