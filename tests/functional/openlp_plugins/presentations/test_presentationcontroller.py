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
Functional tests to test the PresentationController and PresentationDocument
classes and related methods.
"""
from unittest import TestCase
import os
from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument
from tests.functional import MagicMock, mock_open, patch

FOLDER_TO_PATCH = 'openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder'


class TestPresentationController(TestCase):
    """
    Test the PresentationController.
    """
    # TODO: Items left to test
    #   PresentationController
    #       __init__
    #       enabled
    #       is_available
    #       check_available
    #       start_process
    #       kill
    #       add_document
    #       remove_doc
    #       close_presentation
    #       _get_plugin_manager

    def setUp(self):
        mocked_plugin = MagicMock()
        mocked_plugin.settings_section = 'presentations'
        self.presentation = PresentationController(mocked_plugin)
        self.document = PresentationDocument(self.presentation, '')

    def constructor_test(self):
        """
        Test the Constructor
        """
        # GIVEN: A mocked plugin

        # WHEN: The PresentationController is created

        # THEN: The name of the presentation controller should be correct
        self.assertEqual('PresentationController', self.presentation.name,
                         'The name of the presentation controller should be correct')

    def save_titles_and_notes_test(self):
        """
        Test PresentationDocument.save_titles_and_notes method with two valid lists
        """
        # GIVEN: two lists of length==2 and a mocked open and get_thumbnail_folder
        mocked_open = mock_open()
        with patch('builtins.open', mocked_open), patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            titles = ['uno', 'dos']
            notes = ['one', 'two']

            # WHEN: calling save_titles_and_notes
            mocked_get_thumbnail_folder.return_value = 'test'
            self.document.save_titles_and_notes(titles, notes)

            # THEN: the last call to open should have been for slideNotes2.txt
            mocked_open.assert_any_call(os.path.join('test', 'titles.txt'), mode='wt', encoding='utf-8')
            mocked_open.assert_any_call(os.path.join('test', 'slideNotes1.txt'), mode='wt', encoding='utf-8')
            mocked_open.assert_any_call(os.path.join('test', 'slideNotes2.txt'), mode='wt', encoding='utf-8')
            self.assertEqual(mocked_open.call_count, 3, 'There should be exactly three files opened')
            mocked_open().writelines.assert_called_once_with(['uno', 'dos'])
            mocked_open().write.assert_called_any('one')
            mocked_open().write.assert_called_any('two')

    def save_titles_and_notes_with_None_test(self):
        """
        Test PresentationDocument.save_titles_and_notes method with no data
        """
        # GIVEN: None and an empty list and a mocked open and get_thumbnail_folder
        with patch('builtins.open') as mocked_open, patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
            titles = None
            notes = None

            # WHEN: calling save_titles_and_notes
            mocked_get_thumbnail_folder.return_value = 'test'
            self.document.save_titles_and_notes(titles, notes)

            # THEN: No file should have been created
            self.assertEqual(mocked_open.call_count, 0, 'No file should be created')

    def get_titles_and_notes_test(self):
        """
        Test PresentationDocument.get_titles_and_notes method
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists

        with patch('builtins.open', mock_open(read_data='uno\ndos\n')) as mocked_open, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder, \
                patch('openlp.plugins.presentations.lib.presentationcontroller.os.path.exists') as mocked_exists:
            mocked_get_thumbnail_folder.return_value = 'test'
            mocked_exists.return_value = True

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two items for the titles and two empty strings for the notes
            self.assertIs(type(result_titles), list, 'result_titles should be of type list')
            self.assertEqual(len(result_titles), 2, 'There should be two items in the titles')
            self.assertIs(type(result_notes), list, 'result_notes should be of type list')
            self.assertEqual(len(result_notes), 2, 'There should be two items in the notes')
            self.assertEqual(mocked_open.call_count, 3, 'Three files should be opened')
            mocked_open.assert_any_call(os.path.join('test', 'titles.txt'), encoding='utf-8')
            mocked_open.assert_any_call(os.path.join('test', 'slideNotes1.txt'), encoding='utf-8')
            mocked_open.assert_any_call(os.path.join('test', 'slideNotes2.txt'), encoding='utf-8')
            self.assertEqual(mocked_exists.call_count, 3, 'Three files should have been checked')

    def get_titles_and_notes_with_file_not_found_test(self):
        """
        Test PresentationDocument.get_titles_and_notes method with file not found
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists
        with patch('builtins.open') as mocked_open, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder, \
                patch('openlp.plugins.presentations.lib.presentationcontroller.os.path.exists') as mocked_exists:
            mocked_get_thumbnail_folder.return_value = 'test'
            mocked_exists.return_value = False

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two empty lists
            self.assertIs(type(result_titles), list, 'result_titles should be of type list')
            self.assertEqual(len(result_titles), 0, 'there be no titles')
            self.assertIs(type(result_notes), list, 'result_notes should be a list')
            self.assertEqual(len(result_notes), 0, 'but the list should be empty')
            self.assertEqual(mocked_open.call_count, 0, 'No calls to open files')
            self.assertEqual(mocked_exists.call_count, 1, 'There should be one call to file exists')

    def get_titles_and_notes_with_file_error_test(self):
        """
        Test PresentationDocument.get_titles_and_notes method with file errors
        """
        # GIVEN: A mocked open, get_thumbnail_folder and exists
        with patch('builtins.open') as mocked_open, \
                patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder, \
                patch('openlp.plugins.presentations.lib.presentationcontroller.os.path.exists') as mocked_exists:
            mocked_get_thumbnail_folder.return_value = 'test'
            mocked_exists.return_value = True
            mocked_open.side_effect = IOError()

            # WHEN: calling get_titles_and_notes
            result_titles, result_notes = self.document.get_titles_and_notes()

            # THEN: it should return two empty lists
            self.assertIs(type(result_titles), list, 'result_titles should be a list')


class TestPresentationDocument(TestCase):
    """
    Test the PresentationDocument Class
    """
    # TODO: Items left to test
    #   PresentationDocument
    #       __init__
    #       presentation_deleted
    #       get_thumbnail_folder
    #       get_temp_folder
    #       check_thumbnails
    #       close_presentation
    #       is_active
    #       is_loaded
    #       blank_screen
    #       unblank_screen
    #       is_blank
    #       stop_presentation
    #       start_presentation
    #       get_slide_number
    #       get_slide_count
    #       goto_slide
    #       next_step
    #       previous_step
    #       convert_thumbnail
    #       get_thumbnail_path
    #       poll_slidenumber
    #       get_slide_text
    #       get_slide_notes

    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.check_directory_exists_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.check_directory_exists')
        self.get_thumbnail_folder_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder')
        self.os_patcher = patch('openlp.plugins.presentations.lib.presentationcontroller.os')
        self._setup_patcher = \
            patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument._setup')

        self.mock_check_directory_exists = self.check_directory_exists_patcher.start()
        self.mock_get_thumbnail_folder = self.get_thumbnail_folder_patcher.start()
        self.mock_os = self.os_patcher.start()
        self.mock_setup = self._setup_patcher.start()

        self.mock_controller = MagicMock()

        self.mock_get_thumbnail_folder.return_value = 'returned/path/'

    def tearDown(self):
        """
        Stop the patches
        """
        self.check_directory_exists_patcher.stop()
        self.get_thumbnail_folder_patcher.stop()
        self.os_patcher.stop()
        self._setup_patcher.stop()

    def initialise_presentation_document_test(self):
        """
        Test the PresentationDocument __init__ method when initialising the PresentationDocument Class
        """
        # GIVEN: A mocked setup method and mocked controller
        self.mock_setup.reset()

        # WHEN: Creating an instance of PresentationDocument
        PresentationDocument(self.mock_controller, 'Name')

        # THEN: PresentationDocument._setup should have been called with the argument 'Name'
        self.mock_setup.assert_called_once_with('Name')

    def presentation_document_setup_test(self):
        """
        Test the PresentationDocument _setup method when initialising the PresentationDocument Class
        """
        self._setup_patcher.stop()

        # GIVEN: A mocked controller, patched check_directory_exists and get_thumbnail_folder methods

        # WHEN: Creating an instance of PresentationDocument
        PresentationDocument(self.mock_controller, 'Name')

        # THEN: check_directory_exists should have been called with 'returned/path/'
        self.mock_check_directory_exists.assert_called_once_with('returned/path/')

        self._setup_patcher.start()

    def load_presentation_test(self):
        """
        Test the PresentationDocument.load_presentation method.
        """

        # GIVEN: An instance of PresentationDocument
        instance = PresentationDocument(self.mock_controller, 'Name')

        # WHEN: Calling load_presentation()
        result = instance.load_presentation()

        # THEN: load_presentation should return false
        self.assertFalse(result, "PresentationDocument.load_presentation should return false.")

    def get_file_name_test(self):
        """
        Test the PresentationDocument.get_file_name method.
        """

        # GIVEN: A mocked os.path.split which returns a list, an instance of PresentationDocument and
        #       arbitary file_path.
        self.mock_os.path.split.return_value = ['directory', 'file.ext']
        instance = PresentationDocument(self.mock_controller, 'Name')
        instance.file_path = 'filepath'

        # WHEN: Calling get_file_name
        result = instance.get_file_name()

        # THEN: get_file_name should return 'file.ext'
        self.assertEqual(result, 'file.ext')
