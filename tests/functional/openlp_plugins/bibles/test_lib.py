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
This module contains tests for the lib submodule of the Bibles plugin.
"""
from unittest import TestCase

from openlp.plugins.bibles import lib
from openlp.plugins.bibles.lib import SearchResults
from tests.functional import MagicMock, patch


class TestLib(TestCase):
    """
    Test the functions in the :mod:`lib` module.
    """
    def get_reference_separator_test(self):
        """
        Test the get_reference_separator method
        """
        # GIVEN: A list of expected separators
        separators = {'sep_r': '\\s*(?:e)\\s*', 'sep_e_default': 'end', 'sep_v_display': 'w', 'sep_l_display': 'r',
                      'sep_v_default': ':|v|V|verse|verses', 'sep_l': '\\s*(?:r)\\s*', 'sep_l_default': ',|and',
                      'sep_e': '\\s*(?:t)\\s*', 'sep_v': '\\s*(?:w)\\s*', 'sep_r_display': 'e', 'sep_r_default': '-|to'}

        def side_effect():
            lib.REFERENCE_SEPARATORS = separators

        with patch('openlp.plugins.bibles.lib.update_reference_separators',
                   **{'side_effect': side_effect}) as mocked_update_reference_separators:

            # WHEN: Calling get_reference_separator
            for key, value in separators.items():
                ret = lib.get_reference_separator(key)

                # THEN: get_reference_separator should return the correct separator
                self.assertEqual(separators[key], value)
            mocked_update_reference_separators.assert_called_once_with()

    def search_results_creation_test(self):
        """
        Test the creation and construction of the SearchResults class
        """
        # GIVEN: A book, chapter and a verse list
        book = 'Genesis'
        chapter = 1
        verse_list = {
            1: 'In the beginning God created the heavens and the earth.',
            2: 'The earth was without form and void, and darkness was over the face of the deep. And the Spirit of '
               'God was hovering over the face of the waters.'
        }

        # WHEN: We create the search results object
        search_results = SearchResults(book, chapter, verse_list)

        # THEN: It should have a book, a chapter and a verse list
        self.assertIsNotNone(search_results, 'The search_results object should not be None')
        self.assertEqual(search_results.book, book, 'The book should be "Genesis"')
        self.assertEqual(search_results.chapter, chapter, 'The chapter should be 1')
        self.assertDictEqual(search_results.verse_list, verse_list, 'The verse lists should be identical')

    def search_results_has_verse_list_test(self):
        """
        Test that a SearchResults object with a valid verse list returns True when checking ``has_verse_list()``
        """
        # GIVEN: A valid SearchResults object with a proper verse list
        search_results = SearchResults('Genesis', 1, {1: 'In the beginning God created the heavens and the earth.'})

        # WHEN: We check that the SearchResults object has a verse list
        has_verse_list = search_results.has_verse_list()

        # THEN: It should be True
        self.assertTrue(has_verse_list, 'The SearchResults object should have a verse list')

    def search_results_has_no_verse_list_test(self):
        """
        Test that a SearchResults object with an empty verse list returns False when checking ``has_verse_list()``
        """
        # GIVEN: A valid SearchResults object with an empty verse list
        search_results = SearchResults('Genesis', 1, {})

        # WHEN: We check that the SearchResults object has a verse list
        has_verse_list = search_results.has_verse_list()

        # THEN: It should be False
        self.assertFalse(has_verse_list, 'The SearchResults object should have a verse list')
