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
This module contains tests for the db submodule of the Songs plugin.
"""
import os
import shutil
from unittest import TestCase
from tempfile import mkdtemp

from openlp.plugins.songs.lib.db import Song, Author, AuthorType
from openlp.plugins.songs.lib import upgrade
from openlp.core.lib.db import upgrade_db
from tests.utils.constants import TEST_RESOURCES_PATH


class TestDB(TestCase):
    """
    Test the functions in the :mod:`db` module.
    """

    def setUp(self):
        """
        Setup for tests
        """
        self.tmp_folder = mkdtemp()

    def tearDown(self):
        """
        Clean up after tests
        """
        shutil.rmtree(self.tmp_folder)

    def test_add_author(self):
        """
        Test adding an author to a song
        """
        # GIVEN: A song and an author
        song = Song()
        song.authors_songs = []
        author = Author()
        author.first_name = "Max"
        author.last_name = "Mustermann"

        # WHEN: We add an author to the song
        song.add_author(author)

        # THEN: The author should have been added with author_type=None
        self.assertEqual(1, len(song.authors_songs))
        self.assertEqual("Max", song.authors_songs[0].author.first_name)
        self.assertEqual("Mustermann", song.authors_songs[0].author.last_name)
        self.assertIsNone(song.authors_songs[0].author_type)

    def test_add_author_with_type(self):
        """
        Test adding an author with a type specified to a song
        """
        # GIVEN: A song and an author
        song = Song()
        song.authors_songs = []
        author = Author()
        author.first_name = "Max"
        author.last_name = "Mustermann"

        # WHEN: We add an author to the song
        song.add_author(author, AuthorType.Words)

        # THEN: The author should have been added with author_type=None
        self.assertEqual(1, len(song.authors_songs))
        self.assertEqual("Max", song.authors_songs[0].author.first_name)
        self.assertEqual("Mustermann", song.authors_songs[0].author.last_name)
        self.assertEqual(AuthorType.Words, song.authors_songs[0].author_type)

    def test_remove_author(self):
        """
        Test removing an author from a song
        """
        # GIVEN: A song with an author
        song = Song()
        song.authors_songs = []
        author = Author()
        song.add_author(author)

        # WHEN: We remove the author
        song.remove_author(author)

        # THEN: It should have been removed
        self.assertEqual(0, len(song.authors_songs))

    def test_remove_author_with_type(self):
        """
        Test removing an author with a type specified from a song
        """
        # GIVEN: A song with two authors
        song = Song()
        song.authors_songs = []
        author = Author()
        song.add_author(author)
        song.add_author(author, AuthorType.Translation)

        # WHEN: We remove the author with a certain type
        song.remove_author(author, AuthorType.Translation)

        # THEN: It should have been removed and the other author should still be there
        self.assertEqual(1, len(song.authors_songs))
        self.assertEqual(None, song.authors_songs[0].author_type)

    def test_get_author_type_from_translated_text(self):
        """
        Test getting an author type from translated text
        """
        # GIVEN: A string with an author type
        author_type_name = AuthorType.Types[AuthorType.Words]

        # WHEN: We call the method
        author_type = AuthorType.from_translated_text(author_type_name)

        # THEN: The type should be correct
        self.assertEqual(author_type, AuthorType.Words)

    def test_author_get_display_name(self):
        """
        Test that the display name of an author is correct
        """
        # GIVEN: An author
        author = Author()
        author.display_name = "John Doe"

        # WHEN: We call the get_display_name() function
        display_name = author.get_display_name()

        # THEN: It should return only the name
        self.assertEqual("John Doe", display_name)

    def test_author_get_display_name_with_type_words(self):
        """
        Test that the display name of an author with a type is correct (Words)
        """
        # GIVEN: An author
        author = Author()
        author.display_name = "John Doe"

        # WHEN: We call the get_display_name() function
        display_name = author.get_display_name(AuthorType.Words)

        # THEN: It should return the name with the type in brackets
        self.assertEqual("John Doe (Words)", display_name)

    def test_author_get_display_name_with_type_translation(self):
        """
        Test that the display name of an author with a type is correct (Translation)
        """
        # GIVEN: An author
        author = Author()
        author.display_name = "John Doe"

        # WHEN: We call the get_display_name() function
        display_name = author.get_display_name(AuthorType.Translation)

        # THEN: It should return the name with the type in brackets
        self.assertEqual("John Doe (Translation)", display_name)

    def test_upgrade_old_song_db(self):
        """
        Test that we can upgrade an old song db to the current schema
        """
        # GIVEN: An old song db
        old_db_path = os.path.join(TEST_RESOURCES_PATH, "songs", 'songs-1.9.7.sqlite')
        old_db_tmp_path = os.path.join(self.tmp_folder, 'songs-1.9.7.sqlite')
        shutil.copyfile(old_db_path, old_db_tmp_path)
        db_url = 'sqlite:///' + old_db_tmp_path

        # WHEN: upgrading the db
        updated_to_version, latest_version = upgrade_db(db_url, upgrade)

        # Then the song db should have been upgraded to the latest version
        self.assertEqual(updated_to_version, latest_version,
                         'The song DB should have been upgrade to the latest version')

    def test_upgrade_invalid_song_db(self):
        """
        Test that we can upgrade an invalid song db to the current schema
        """
        # GIVEN: A song db with invalid version
        invalid_db_path = os.path.join(TEST_RESOURCES_PATH, "songs", 'songs-2.2-invalid.sqlite')
        invalid_db_tmp_path = os.path.join(self.tmp_folder, 'songs-2.2-invalid.sqlite')
        shutil.copyfile(invalid_db_path, invalid_db_tmp_path)
        db_url = 'sqlite:///' + invalid_db_tmp_path

        # WHEN: upgrading the db
        updated_to_version, latest_version = upgrade_db(db_url, upgrade)

        # Then the song db should have been upgraded to the latest version without errors
        self.assertEqual(updated_to_version, latest_version,
                         'The song DB should have been upgrade to the latest version')
