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
This module contains tests for the lib submodule of the Presentations plugin.
"""
from PyQt4 import QtGui

from unittest import TestCase
from openlp.plugins.bibles.lib.mediaitem import BibleMediaItem
from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMediaItem(TestCase, TestMixin):
    """
    Test the bible mediaitem methods.
    """

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        with patch('openlp.plugins.bibles.lib.mediaitem.MediaManagerItem._setup'),\
                patch('openlp.plugins.bibles.lib.mediaitem.BibleMediaItem.setup_item'):
            self.media_item = BibleMediaItem(None, MagicMock())
        self.setup_application()

    def display_results_no_results_test(self):
        """
        Test the display_results method when called with a single bible, returning no results
        """

        # GIVEN: A mocked build_display_results which returns an empty list
        with patch('openlp.plugins.bibles.lib.BibleMediaItem.build_display_results', **{'return_value': []}) \
                as mocked_build_display_results:
            mocked_list_view = MagicMock()
            self.media_item.search_results = 'results'
            self.media_item.list_view = mocked_list_view

            # WHEN: Calling display_results with a single bible version
            self.media_item.display_results('NIV')

            # THEN: No items should be added to the list, and select all should have been called.
            mocked_build_display_results.assert_called_once_with('NIV', '', 'results')
            self.assertFalse(mocked_list_view.addItem.called)
            mocked_list_view.selectAll.assert_called_once_with()
            self.assertEqual(self.media_item.search_results, {})
            self.assertEqual(self.media_item.second_search_results, {})

    def display_results_two_bibles_no_results_test(self):
        """
        Test the display_results method when called with two bibles, returning no results
        """

        # GIVEN: A mocked build_display_results which returns an empty list
        with patch('openlp.plugins.bibles.lib.BibleMediaItem.build_display_results', **{'return_value': []}) \
                as mocked_build_display_results:
            mocked_list_view = MagicMock()
            self.media_item.search_results = 'results'
            self.media_item.list_view = mocked_list_view

            # WHEN: Calling display_results with two single bible versions
            self.media_item.display_results('NIV', 'GNB')

            # THEN: build_display_results should have been called with two bible versions.
            #       No items should be added to the list, and select all should have been called.
            mocked_build_display_results.assert_called_once_with('NIV', 'GNB', 'results')
            self.assertFalse(mocked_list_view.addItem.called)
            mocked_list_view.selectAll.assert_called_once_with()
            self.assertEqual(self.media_item.search_results, {})
            self.assertEqual(self.media_item.second_search_results, {})

    def display_results_returns_lots_of_results_test_test(self):
            """
            Test the display_results method a large number of results (> 100) are returned
            """

            # GIVEN: A mocked build_display_results which returns a large list of results
            long_list = list(range(100))
            with patch('openlp.plugins.bibles.lib.BibleMediaItem.build_display_results', **{'return_value': long_list})\
                    as mocked_build_display_results:
                mocked_list_view = MagicMock()
                self.media_item.search_results = 'results'
                self.media_item.list_view = mocked_list_view

                # WHEN: Calling display_results
                self.media_item.display_results('NIV', 'GNB')

                # THEN: addItem should have been called 100 times, and the lsit items should not be selected.
                mocked_build_display_results.assert_called_once_with('NIV', 'GNB', 'results')
                self.assertEqual(mocked_list_view.addItem.call_count, 100)
                mocked_list_view.selectAll.assert_called_once_with()
                self.assertEqual(self.media_item.search_results, {})
                self.assertEqual(self.media_item.second_search_results, {})
