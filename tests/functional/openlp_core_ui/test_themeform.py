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
Package to test the openlp.core.ui.themeform package.
"""

from unittest import TestCase

from openlp.core.ui import ThemeForm

from tests.functional import MagicMock, patch


class TestThemeManager(TestCase):
    """
    Test the functions in the ThemeManager Class
    """
    def select_image_file_dialog_cancelled_test(self):
        """
        Test the select image file dialog when the user presses cancel
        """
        # GIVEN: An instance of Theme Form and mocked QFileDialog which returns an empty string (similating a user
        #       pressing cancel)
        with patch('openlp.core.ui.ThemeForm._setup'),\
                patch('openlp.core.ui.themeform.get_images_filter',
                      **{'return_value': 'Image Files (*.bmp; *.gif)(*.bmp *.gif)'}),\
                patch('openlp.core.ui.themeform.QtGui.QFileDialog.getOpenFileName',
                      **{'return_value': ''}) as mocked_get_open_file_name,\
                patch('openlp.core.ui.themeform.translate', **{'return_value': 'Translated String'}),\
                patch('openlp.core.ui.ThemeForm.set_background_page_values') as mocked_set_background_page_values:
            instance = ThemeForm(None)
            mocked_image_file_edit = MagicMock()
            mocked_image_file_edit.text.return_value = '/original_path/file.ext'
            instance.image_file_edit = mocked_image_file_edit

            # WHEN: on_image_browse_button is clicked
            instance.on_image_browse_button_clicked()

            # THEN: The QFileDialog getOpenFileName and set_background_page_values moethods should have been called
            #       with known arguments
            mocked_get_open_file_name.assert_called_once_with(instance, 'Translated String', '/original_path/file.ext',
                                                              'Image Files (*.bmp; *.gif)(*.bmp *.gif);;'
                                                              'All Files (*.*)')
            mocked_set_background_page_values.assert_called_once_with()

    def select_image_file_dialog_new_file_test(self):
        """
        Test the select image file dialog when the user presses ok
        """
        # GIVEN: An instance of Theme Form and mocked QFileDialog which returns a file path
        with patch('openlp.core.ui.ThemeForm._setup'),\
                patch('openlp.core.ui.themeform.get_images_filter',
                      **{'return_value': 'Image Files (*.bmp; *.gif)(*.bmp *.gif)'}),\
                patch('openlp.core.ui.themeform.QtGui.QFileDialog.getOpenFileName',
                      **{'return_value': '/new_path/file.ext'}) as mocked_get_open_file_name,\
                patch('openlp.core.ui.themeform.translate', **{'return_value': 'Translated String'}),\
                patch('openlp.core.ui.ThemeForm.set_background_page_values') as mocked_background_page_values:
            instance = ThemeForm(None)
            mocked_image_file_edit = MagicMock()
            mocked_image_file_edit.text.return_value = '/original_path/file.ext'
            instance.image_file_edit = mocked_image_file_edit
            instance.theme = MagicMock()

            # WHEN: on_image_browse_button is clicked
            instance.on_image_browse_button_clicked()

            # THEN: The QFileDialog getOpenFileName and set_background_page_values moethods should have been called
            #       with known arguments and theme.background_filename should be set
            mocked_get_open_file_name.assert_called_once_with(instance, 'Translated String', '/original_path/file.ext',
                                                              'Image Files (*.bmp; *.gif)(*.bmp *.gif);;'
                                                              'All Files (*.*)')
            self.assertEqual(instance.theme.background_filename, '/new_path/file.ext',
                             'theme.background_filename should be set to the path that the file dialog returns')
            mocked_background_page_values.assert_called_once_with()
