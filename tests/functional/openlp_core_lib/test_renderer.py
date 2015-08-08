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
Package to test the openlp.core.ui.renderer package.
"""
from unittest import TestCase

from PyQt4 import QtCore

from openlp.core.common import Registry
from openlp.core.lib import Renderer, ScreenList, ServiceItem

from tests.functional import MagicMock

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestRenderer(TestCase):

    def setUp(self):
        """
        Set up the components need for all tests
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        Registry.create()

    def tearDown(self):
        """
        Delete QApplication.
        """
        del self.screens

    def default_screen_layout_test(self):
        """
        Test the default layout calculations
        """
        # GIVEN: A new renderer instance.
        renderer = Renderer()
        # WHEN: given the default screen size has been created.
        # THEN: The renderer have created a default screen.
        self.assertEqual(renderer.width, 1024, 'The base renderer should be a live controller')
        self.assertEqual(renderer.height, 768, 'The base renderer should be a live controller')
        self.assertEqual(renderer.screen_ratio, 0.75, 'The base renderer should be a live controller')
        self.assertEqual(renderer.footer_start, 691, 'The base renderer should be a live controller')

    def _get_start_tags_test(self):
        """
        Test the _get_start_tags() method
        """
        # GIVEN: A new renderer instance. Broken raw_text (missing closing tags).
        renderer = Renderer()
        given_raw_text = '{st}{r}Text text text'
        expected_tuple = ('{st}{r}Text text text{/r}{/st}', '{st}{r}',
                          '<strong><span style="-webkit-text-fill-color:red">')

        # WHEN: The renderer converts the start tags
        result = renderer._get_start_tags(given_raw_text)

        # THEN: Check if the correct tuple is returned.
        self.assertEqual(result, expected_tuple), 'A tuple should be returned containing the text with correct ' \
            'tags, the opening tags, and the opening html tags.'

    def _word_split_test(self):
        """
        Test the _word_split() method
        """
        # GIVEN: A line of text
        renderer = Renderer()
        given_line = 'beginning asdf \n end asdf'
        expected_words = ['beginning', 'asdf', 'end', 'asdf']

        # WHEN: Split the line based on word split rules
        result_words = renderer._words_split(given_line)

        # THEN: The word lists should be the same.
        self.assertListEqual(result_words, expected_words)

    def format_slide_logical_split_test(self):
        """
        Test that a line with text and a logic break does not break the renderer just returns the input
        """
        # GIVEN: A line of with a space text and the logical split
        renderer = Renderer()
        renderer.empty_height = 25
        given_line = 'a\n[---]\nb'
        expected_words = ['a<br>[---]<br>b']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The word lists should be the same.
        self.assertListEqual(result_words, expected_words)

    def format_slide_blank_before_split_test(self):
        """
        Test that a line with blanks before the logical split at handled
        """
        # GIVEN: A line of with a space before the logical split
        renderer = Renderer()
        renderer.empty_height = 25
        given_line = '\n       [---]\n'
        expected_words = ['<br>       [---]']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The blanks have been removed.
        self.assertListEqual(result_words, expected_words)

    def format_slide_blank_after_split_test(self):
        """
        Test that a line with blanks before the logical split at handled
        """
        # GIVEN: A line of with a space after the logical split
        renderer = Renderer()
        renderer.empty_height = 25
        given_line = '\n[---]  \n'
        expected_words = ['<br>[---]  ']
        service_item = ServiceItem(None)

        # WHEN: Split the line based on word split rules
        result_words = renderer.format_slide(given_line, service_item)

        # THEN: The blanks have been removed.
        self.assertListEqual(result_words, expected_words)
