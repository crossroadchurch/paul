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
Functional tests to test the Bible Manager class and related methods.
"""
from unittest import TestCase

from openlp.core.common import Registry, Settings
from openlp.plugins.bibles.lib import BibleManager, LanguageSelection
from tests.interfaces import MagicMock, patch

from tests.utils.constants import TEST_RESOURCES_PATH
from tests.helpers.testmixin import TestMixin


class TestBibleManager(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the environment for testing bible queries with 1 Timothy 3
        """
        self.build_settings()
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('application', MagicMock())
        bible_settings = {
            'bibles/proxy name': '',
            'bibles/db type': 'sqlite',
            'bibles/book name language': LanguageSelection.Bible,
            'bibles/verse separator': '',
            'bibles/range separator': '',
            'bibles/list separator': '',
            'bibles/end separator': '',
        }
        Settings().extend_default_settings(bible_settings)
        with patch('openlp.core.common.applocation.Settings') as mocked_class, \
                patch('openlp.core.common.AppLocation.get_section_data_path') as mocked_get_section_data_path, \
                patch('openlp.core.common.AppLocation.get_files') as mocked_get_files:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_files()
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_files.return_value = ["tests.sqlite"]
            mocked_get_section_data_path.return_value = TEST_RESOURCES_PATH + "/bibles"
            self.manager = BibleManager(MagicMock())

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.manager
        self.destroy_settings()

    def get_books_test(self):
        """
        Test the get_books method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the books of the bible
        books = self.manager.get_books('tests')
        # THEN a list of books should be returned
        self.assertEqual(66, len(books), 'There should be 66 books in the bible')

    def get_book_by_id_test(self):
        """
        Test the get_book_by_id method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the book of the bible
        book = self.manager.get_book_by_id('tests', 54)
        # THEN a book should be returned
        self.assertEqual('1 Timothy', book.name, '1 Timothy should have been returned from the bible')

    def get_chapter_count_test(self):
        """
        Test the get_chapter_count method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the chapters in a book of the bible
        book = self.manager.get_book_by_id('tests', 54)
        chapter = self.manager.get_chapter_count('tests', book)
        # THEN the chapter count should be returned
        self.assertEqual(6, chapter, '1 Timothy should have 6 chapters returned from the bible')

    def get_verse_count_by_book_ref_id_test(self):
        """
        Test the get_verse_count_by_book_ref_id method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the number of verses in a book of the bible
        verses = self.manager.get_verse_count_by_book_ref_id('tests', 54, 3)
        # THEN the chapter count should be returned
        self.assertEqual(16, verses, '1 Timothy v3 should have 16 verses returned from the bible')
