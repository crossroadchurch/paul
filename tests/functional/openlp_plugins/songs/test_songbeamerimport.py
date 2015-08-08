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
This module contains tests for the Songbeamer song importer.
"""

import os
from unittest import TestCase

from tests.functional import MagicMock, patch
from openlp.plugins.songs.lib.importers.songbeamer import SongBeamerImport
from openlp.plugins.songs.lib import VerseType
from openlp.core.common import Registry

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..', 'resources', 'songbeamersongs'))
SONG_TEST_DATA = {
    'Lobsinget dem Herrn.sng': {
        'title': 'GL 1 - Lobsinget dem Herrn',
        'verses': [
            ('1. Lobsinget dem Herrn,\no preiset Ihn gern!\nAnbetung und Lob Ihm gebühret.\n', 'v'),
            ('2. Lobsingt Seiner Lieb´,\ndie einzig ihn trieb,\nzu sterben für unsere Sünden!\n', 'v'),
            ('3. Lobsingt Seiner Macht!\nSein Werk ist vollbracht:\nEr sitzet zur Rechten des Vaters.\n', 'v'),
            ('4. Lobsingt seiner Treu´,\ndie immerdar neu,\nbis Er uns zur Herrlichket führet!\n\n', 'v')
        ],
        'song_book_name': 'Glaubenslieder I',
        'song_number': "1",
        'authors': ['Carl Brockhaus', 'Johann Jakob Vetter']
    }
}


class TestSongBeamerImport(TestCase):
    """
    Test the functions in the :mod:`songbeamerimport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    def create_importer_test(self):
        """
        Test creating an instance of the SongBeamer file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songbeamer.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = SongBeamerImport(mocked_manager, filenames=[])

            # THEN: The importer object should not be None
            self.assertIsNotNone(importer, 'Import should not be none')

    def invalid_import_source_test(self):
        """
        Test SongBeamerImport.do_import handles different invalid import_source values
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songbeamer.SongImport'):
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = SongBeamerImport(mocked_manager, filenames=[])
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = True

            # WHEN: Import source is not a list
            for source in ['not a list', 0]:
                importer.import_source = source

                # THEN: do_import should return none and the progress bar maximum should not be set.
                self.assertIsNone(importer.do_import(), 'do_import should return None when import_source is not a list')
                self.assertEqual(mocked_import_wizard.progress_bar.setMaximum.called, False,
                                 'setMaxium on import_wizard.progress_bar should not have been called')

    def valid_import_source_test(self):
        """
        Test SongBeamerImport.do_import handles different invalid import_source values
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.songbeamer.SongImport'):
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = SongBeamerImport(mocked_manager, filenames=[])
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = True

            # WHEN: Import source is a list
            importer.import_source = ['List', 'of', 'files']

            # THEN: do_import should return none and the progress bar setMaximum should be called with the length of
            #       import_source.
            self.assertIsNone(importer.do_import(),
                              'do_import should return None when import_source is a list and stop_import_flag is True')
            mocked_import_wizard.progress_bar.setMaximum.assert_called_with(len(importer.import_source))

    def file_import_test(self):
        """
        Test the actual import of real song files and check that the imported data is correct.
        """

        # GIVEN: Test files with a mocked out SongImport class, a mocked out "manager", a mocked out "import_wizard",
        #       and mocked out "author", "add_copyright", "add_verse", "finish" methods.
        with patch('openlp.plugins.songs.lib.importers.songbeamer.SongImport'):
            for song_file in SONG_TEST_DATA:
                mocked_manager = MagicMock()
                mocked_import_wizard = MagicMock()
                mocked_add_verse = MagicMock()
                mocked_finish = MagicMock()
                mocked_finish.return_value = True
                importer = SongBeamerImport(mocked_manager, filenames=[])
                importer.import_wizard = mocked_import_wizard
                importer.stop_import_flag = False
                importer.add_verse = mocked_add_verse
                importer.finish = mocked_finish

                # WHEN: Importing each file
                importer.import_source = [os.path.join(TEST_PATH, song_file)]
                title = SONG_TEST_DATA[song_file]['title']
                add_verse_calls = SONG_TEST_DATA[song_file]['verses']
                song_book_name = SONG_TEST_DATA[song_file]['song_book_name']
                song_number = SONG_TEST_DATA[song_file]['song_number']
                song_authors = SONG_TEST_DATA[song_file]['authors']

                # THEN: do_import should return none, the song data should be as expected, and finish should have been
                #       called.
                self.assertIsNone(importer.do_import(), 'do_import should return None when it has completed')
                self.assertEqual(importer.title, title, 'title for %s should be "%s"' % (song_file, title))
                for verse_text, verse_tag in add_verse_calls:
                    mocked_add_verse.assert_any_call(verse_text, verse_tag)
                if song_book_name:
                    self.assertEqual(importer.song_book_name, song_book_name,
                                     'song_book_name for %s should be "%s"' % (song_file, song_book_name))
                if song_number:
                    self.assertEqual(importer.song_number, song_number,
                                     'song_number for %s should be %s' % (song_file, song_number))
                if song_authors:
                    for author in importer.authors:
                        self.assertIn(author, song_authors)
                mocked_finish.assert_called_with()

    def check_verse_marks_test(self):
        """
        Tests different lines to see if a verse mark is detected or not
        """

        # GIVEN: line with unnumbered verse-type
        line = 'Refrain'
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back true and c as self.current_verse_type
        self.assertTrue(result, 'Versemark for <Refrain> should be found, value true')
        self.assertEqual(self.current_verse_type, 'c', '<Refrain> should be interpreted as <c>')

        # GIVEN: line with unnumbered verse-type and trailing space
        line = 'Refrain '
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back true and c as self.current_verse_type
        self.assertTrue(result, 'Versemark for <Refrain > should be found, value true')
        self.assertEqual(self.current_verse_type, 'c', '<Refrain > should be interpreted as <c>')

        # GIVEN: line with numbered verse-type
        line = 'Verse 1'
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back true and v1 as self.current_verse_type
        self.assertTrue(result, 'Versemark for <Verse 1> should be found, value true')
        self.assertEqual(self.current_verse_type, 'v1', u'<Verse 1> should be interpreted as <v1>')

        # GIVEN: line with special unnumbered verse-mark (used in Songbeamer to allow usage of non-supported tags)
        line = '$$M=special'
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back true and o as self.current_verse_type
        self.assertTrue(result, 'Versemark for <$$M=special> should be found, value true')
        self.assertEqual(self.current_verse_type, 'o', u'<$$M=special> should be interpreted as <o>')

        # GIVEN: line with song-text with 3 words
        line = 'Jesus my saviour'
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back false and none as self.current_verse_type
        self.assertFalse(result, 'No versemark for <Jesus my saviour> should be found, value false')
        self.assertIsNone(self.current_verse_type, '<Jesus my saviour> should be interpreted as none versemark')

        # GIVEN: line with song-text with 2 words
        line = 'Praise him'
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back false and none as self.current_verse_type
        self.assertFalse(result, 'No versemark for <Praise him> should be found, value false')
        self.assertIsNone(self.current_verse_type, '<Praise him> should be interpreted as none versemark')

        # GIVEN: line with only a space (could occur, nothing regular)
        line = ' '
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back false and none as self.current_verse_type
        self.assertFalse(result, 'No versemark for < > should be found, value false')
        self.assertIsNone(self.current_verse_type, '< > should be interpreted as none versemark')

        # GIVEN: blank line (could occur, nothing regular)
        line = ''
        self.current_verse_type = None
        # WHEN: line is being checked for verse marks
        result = SongBeamerImport.check_verse_marks(self, line)
        # THEN: we should get back false and none as self.current_verse_type
        self.assertFalse(result, 'No versemark for <> should be found, value false')
        self.assertIsNone(self.current_verse_type, '<> should be interpreted as none versemark')
