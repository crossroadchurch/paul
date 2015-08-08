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
Functional tests to test the PowerPointController class and related methods.
"""
import os
import shutil
from unittest import TestCase
from tempfile import mkdtemp

from tests.functional import patch, MagicMock
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH

from openlp.plugins.presentations.lib.powerpointcontroller import PowerpointController, PowerpointDocument,\
    _get_text_from_shapes
from openlp.core.common import is_win, Settings

if is_win():
    import pywintypes

__default_settings__ = {
    'presentations/powerpoint slide click advance': True
}


class TestPowerpointController(TestCase, TestMixin):
    """
    Test the PowerpointController Class
    """

    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.setup_application()
        self.build_settings()
        self.mock_plugin = MagicMock()
        self.temp_folder = mkdtemp()
        self.mock_plugin.settings_section = self.temp_folder

    def tearDown(self):
        """
        Stop the patches
        """
        self.destroy_settings()
        shutil.rmtree(self.temp_folder)

    def constructor_test(self):
        """
        Test the Constructor from the PowerpointController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = PowerpointController(plugin=self.mock_plugin)

        # THEN: The name of the presentation controller should be correct
        self.assertEqual('Powerpoint', controller.name,
                         'The name of the presentation controller should be correct')


class TestPowerpointDocument(TestCase, TestMixin):
    """
    Test the PowerpointDocument Class
    """

    def setUp(self):
        """
        Set up the patches and mocks need for all tests.
        """
        self.setup_application()
        self.build_settings()
        self.mock_plugin = MagicMock()
        self.temp_folder = mkdtemp()
        self.mock_plugin.settings_section = self.temp_folder
        self.powerpoint_document_stop_presentation_patcher = patch(
            'openlp.plugins.presentations.lib.powerpointcontroller.PowerpointDocument.stop_presentation')
        self.presentation_document_get_temp_folder_patcher = patch(
            'openlp.plugins.presentations.lib.powerpointcontroller.PresentationDocument.get_temp_folder')
        self.presentation_document_setup_patcher = patch(
            'openlp.plugins.presentations.lib.powerpointcontroller.PresentationDocument._setup')
        self.mock_powerpoint_document_stop_presentation = self.powerpoint_document_stop_presentation_patcher.start()
        self.mock_presentation_document_get_temp_folder = self.presentation_document_get_temp_folder_patcher.start()
        self.mock_presentation_document_setup = self.presentation_document_setup_patcher.start()
        self.mock_controller = MagicMock()
        self.mock_presentation = MagicMock()
        self.mock_presentation_document_get_temp_folder.return_value = 'temp folder'
        self.file_name = os.path.join(TEST_RESOURCES_PATH, 'presentations', 'test.pptx')
        self.real_controller = PowerpointController(self.mock_plugin)
        Settings().extend_default_settings(__default_settings__)

    def tearDown(self):
        """
        Stop the patches
        """
        self.powerpoint_document_stop_presentation_patcher.stop()
        self.presentation_document_get_temp_folder_patcher.stop()
        self.presentation_document_setup_patcher.stop()
        self.destroy_settings()
        shutil.rmtree(self.temp_folder)

    def show_error_msg_test(self):
        """
        Test the PowerpointDocument.show_error_msg() method gets called on com exception
        """
        if is_win():
            # GIVEN: A PowerpointDocument with mocked controller and presentation
            with patch('openlp.plugins.presentations.lib.powerpointcontroller.critical_error_message_box') as \
                    mocked_critical_error_message_box:
                instance = PowerpointDocument(self.mock_controller, self.mock_presentation)
                instance.presentation = MagicMock()
                instance.presentation.SlideShowWindow.View.GotoSlide = MagicMock(side_effect=pywintypes.com_error('1'))
                instance.index_map[42] = 42

                # WHEN: Calling goto_slide which will throw an exception
                instance.goto_slide(42)

                # THEN: mocked_critical_error_message_box should have been called
                mocked_critical_error_message_box.assert_called_with('Error', 'An error occurred in the Powerpoint '
                                                                     'integration and the presentation will be stopped.'
                                                                     ' Restart the presentation if you wish to '
                                                                     'present it.')

    # add _test to the following if necessary
    def verify_loading_document(self):
        """
        Test loading a document in PowerPoint
        """
        if is_win() and self.real_controller.check_available():
            # GIVEN: A PowerpointDocument and a presentation
            doc = PowerpointDocument(self.real_controller, self.file_name)

            # WHEN: loading the filename
            doc.load_presentation()
            result = doc.is_loaded()

            # THEN: result should be true
            self.assertEqual(result, True, 'The result should be True')
        else:
            self.skipTest('Powerpoint not available, skipping test.')

    def create_titles_and_notes_test(self):
        """
        Test creating the titles from PowerPoint
        """
        # GIVEN: mocked save_titles_and_notes, _get_text_from_shapes and two mocked slides
        self.doc = PowerpointDocument(self.mock_controller, self.file_name)
        self.doc.get_slide_count = MagicMock()
        self.doc.get_slide_count.return_value = 2
        self.doc.index_map = {1: 1, 2: 2}
        self.doc.save_titles_and_notes = MagicMock()
        self.doc._PowerpointDocument__get_text_from_shapes = MagicMock()
        slide = MagicMock()
        slide.Shapes.Title.TextFrame.TextRange.Text = 'SlideText'
        pres = MagicMock()
        pres.Slides = MagicMock(side_effect=[slide, slide])
        self.doc.presentation = pres

        # WHEN reading the titles and notes
        self.doc.create_titles_and_notes()

        # THEN the save should have been called exactly once with 2 titles and 2 notes
        self.doc.save_titles_and_notes.assert_called_once_with(['SlideText\n', 'SlideText\n'], [' ', ' '])

    def create_titles_and_notes_with_no_slides_test(self):
        """
        Test creating the titles from PowerPoint when it returns no slides
        """
        # GIVEN: mocked save_titles_and_notes, _get_text_from_shapes and two mocked slides
        doc = PowerpointDocument(self.mock_controller, self.file_name)
        doc.save_titles_and_notes = MagicMock()
        doc._PowerpointDocument__get_text_from_shapes = MagicMock()
        pres = MagicMock()
        pres.Slides = []
        doc.presentation = pres

        # WHEN reading the titles and notes
        doc.create_titles_and_notes()

        # THEN the save should have been called exactly once with empty titles and notes
        doc.save_titles_and_notes.assert_called_once_with([], [])

    def get_text_from_shapes_test(self):
        """
        Test getting text from powerpoint shapes
        """
        # GIVEN: mocked shapes
        shape = MagicMock()
        shape.PlaceholderFormat.Type = 2
        shape.HasTextFrame = shape.TextFrame.HasText = True
        shape.TextFrame.TextRange.Text = 'slideText'
        shapes = [shape, shape]

        # WHEN: getting the text
        result = _get_text_from_shapes(shapes)

        # THEN: it should return the text
        self.assertEqual(result, 'slideText\nslideText\n', 'result should match \'slideText\nslideText\n\'')

    def get_text_from_shapes_with_no_shapes_test(self):
        """
        Test getting text from powerpoint shapes with no shapes
        """
        # GIVEN: empty shapes array
        shapes = []

        # WHEN: getting the text
        result = _get_text_from_shapes(shapes)

        # THEN: it should not fail but return empty string
        self.assertEqual(result, '', 'result should be empty')

    def goto_slide_test(self):
        """
        Test that goto_slide goes to next effect if the slide is already displayed
        """
        # GIVEN: A Document with mocked controller, presentation, and mocked functions get_slide_number and next_step
        doc = PowerpointDocument(self.mock_controller, self.mock_presentation)
        doc.presentation = MagicMock()
        doc.presentation.SlideShowWindow.View.GetClickIndex.return_value = 1
        doc.presentation.SlideShowWindow.View.GetClickCount.return_value = 2
        doc.get_slide_number = MagicMock()
        doc.get_slide_number.return_value = 1
        doc.next_step = MagicMock()
        doc.index_map[1] = 1

        # WHEN: Calling goto_slide
        doc.goto_slide(1)

        # THEN: next_step() should be call to try to advance to the next effect.
        self.assertTrue(doc.next_step.called, 'next_step() should have been called!')

    def blank_screen_test(self):
        """
        Test that blank_screen works as expected
        """
        # GIVEN: A Document with mocked controller, presentation, and mocked function get_slide_number
        doc = PowerpointDocument(self.mock_controller, self.mock_presentation)
        doc.presentation = MagicMock()
        doc.presentation.SlideShowWindow.View.GetClickIndex.return_value = 3
        doc.presentation.Application.Version = 14.0
        doc.get_slide_number = MagicMock()
        doc.get_slide_number.return_value = 2

        # WHEN: Calling goto_slide
        doc.blank_screen()

        # THEN: The view state, doc.blank_slide and doc.blank_click should have new values
        self.assertEquals(doc.presentation.SlideShowWindow.View.State, 3, 'The View State should be 3')
        self.assertEquals(doc.blank_slide, 2, 'doc.blank_slide should be 2 because of the PowerPoint version')
        self.assertEquals(doc.blank_click, 3, 'doc.blank_click should be 3 because of the PowerPoint version')

    def unblank_screen_test(self):
        """
        Test that unblank_screen works as expected
        """
        # GIVEN: A Document with mocked controller, presentation, ScreenList, and mocked function get_slide_number
        with patch('openlp.plugins.presentations.lib.powerpointcontroller.ScreenList') as mocked_screen_list:
            mocked_screen_list_ret = MagicMock()
            mocked_screen_list_ret.screen_list = [1]
            mocked_screen_list.return_value = mocked_screen_list_ret
            doc = PowerpointDocument(self.mock_controller, self.mock_presentation)
            doc.presentation = MagicMock()
            doc.presentation.SlideShowWindow.View.GetClickIndex.return_value = 3
            doc.presentation.Application.Version = 14.0
            doc.get_slide_number = MagicMock()
            doc.get_slide_number.return_value = 2
            doc.index_map[1] = 1
            doc.blank_slide = 1
            doc.blank_click = 1

            # WHEN: Calling goto_slide
            doc.unblank_screen()

            # THEN: The view state have new value, and several function should have been called
            self.assertEquals(doc.presentation.SlideShowWindow.View.State, 1, 'The View State should be 1')
            self.assertEquals(doc.presentation.SlideShowWindow.Activate.called, True,
                              'SlideShowWindow.Activate should have been called')
            self.assertEquals(doc.presentation.SlideShowWindow.View.GotoSlide.called, True,
                              'View.GotoSlide should have been called because of the PowerPoint version')
            self.assertEquals(doc.presentation.SlideShowWindow.View.GotoClick.called, True,
                              'View.GotoClick should have been called because of the PowerPoint version')
