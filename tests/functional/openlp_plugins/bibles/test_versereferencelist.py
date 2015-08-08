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
This module contains tests for the versereferencelist submodule of the Bibles plugin.
"""
from unittest import TestCase

from openlp.plugins.bibles.lib.versereferencelist import VerseReferenceList


class TestVerseReferenceList(TestCase):
    """
    Test the VerseReferenceList class
    """
    def add_first_verse_test(self):
        """
        Test the addition of a verse to the empty list
        """
        # GIVEN: an empty list
        reference_list = VerseReferenceList()
        book = 'testBook'
        chapter = 1
        verse = 1
        version = 'testVersion'
        copyright_ = 'testCopyright'
        permission = 'testPermission'

        # WHEN: We add it to the verse list
        reference_list.add(book, chapter, verse, version, copyright_, permission)

        # THEN: The entries should be in the first entry of the list
        self.assertEqual(reference_list.current_index, 0, 'The current index should be 0')
        self.assertEqual(reference_list.verse_list[0]['book'], book, 'The book in first entry should be %s' % book)
        self.assertEqual(reference_list.verse_list[0]['chapter'], chapter, 'The chapter in first entry should be %u' %
                                                                           chapter)
        self.assertEqual(reference_list.verse_list[0]['start'], verse, 'The start in first entry should be %u' % verse)
        self.assertEqual(reference_list.verse_list[0]['version'], version, 'The version in first entry should be %s' %
                                                                           version)
        self.assertEqual(reference_list.verse_list[0]['end'], verse, 'The end in first entry should be %u' % verse)

    def add_next_verse_test(self):
        """
        Test the addition of the following verse
        """
        # GIVEN: 1 line in the list of verses
        book = 'testBook'
        chapter = 1
        verse = 1
        next_verse = 2
        version = 'testVersion'
        copyright_ = 'testCopyright'
        permission = 'testPermission'
        reference_list = VerseReferenceList()
        reference_list.add(book, chapter, verse, version, copyright_, permission)

        # WHEN: We add the following verse to the verse list
        reference_list.add(book, chapter, next_verse, version, copyright_, permission)

        # THEN: The current index should be 0 and the end pointer of the entry should be '2'
        self.assertEqual(reference_list.current_index, 0, 'The current index should be 0')
        self.assertEqual(reference_list.verse_list[0]['end'], next_verse,
                         'The end in first entry should be %u' % next_verse)

    def add_another_verse_test(self):
        """
        Test the addition of a verse in another book
        """
        # GIVEN: 1 line in the list of verses
        book = 'testBook'
        chapter = 1
        verse = 1
        another_book = 'testBook2'
        another_chapter = 2
        another_verse = 5
        version = 'testVersion'
        copyright_ = 'testCopyright'
        permission = 'testPermission'
        reference_list = VerseReferenceList()
        reference_list.add(book, chapter, verse, version, copyright_, permission)

        # WHEN: We add a verse of another book to the verse list
        reference_list.add(another_book, another_chapter, another_verse, version, copyright_, permission)

        # THEN: the current index should be 1
        self.assertEqual(reference_list.current_index, 1, 'The current index should be 1')

    def add_version_test(self):
        """
        Test the addition of a version to the list
        """
        # GIVEN: version, copyright and permission
        reference_list = VerseReferenceList()
        version = 'testVersion'
        copyright_ = 'testCopyright'
        permission = 'testPermission'

        # WHEN: a not existing version will be added
        reference_list.add_version(version, copyright_, permission)

        # THEN: the data will be appended to the list
        self.assertEqual(len(reference_list.version_list), 1, 'The version data should be appended')
        self.assertEqual(reference_list.version_list[0],
                         {'version': version, 'copyright': copyright_, 'permission': permission},
                         'The version data should be appended')

    def add_existing_version_test(self):
        """
        Test the addition of an existing version to the list
        """
        # GIVEN: version, copyright and permission, added to the version list
        reference_list = VerseReferenceList()
        version = 'testVersion'
        copyright_ = 'testCopyright'
        permission = 'testPermission'
        reference_list.add_version(version, copyright_, permission)

        # WHEN: an existing version will be added
        reference_list.add_version(version, copyright_, permission)

        # THEN: the data will not be appended to the list
        self.assertEqual(len(reference_list.version_list), 1, 'The version data should not be appended')
