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
This module contains tests for the EasyWorship song importer.
"""

import os
from unittest import TestCase

from tests.functional import MagicMock, patch

from openlp.core.common import Registry
from openlp.plugins.songs.lib.importers.easyworship import EasyWorshipSongImport, FieldDescEntry, FieldType

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'easyworshipsongs'))
SONG_TEST_DATA = [
    {'title': 'Amazing Grace',
     'authors': ['John Newton'],
     'copyright': 'Public Domain',
     'ccli_number': 0,
     'verses':
        [('Amazing grace how sweet the sound,\nThat saved a wretch like me;\n'
          'I once was lost, but now am found\nWas blind, but now I see.', 'v1'),
         ('T\'was grace that taught my heart to fear,\nAnd grace my fears relieved;\n'
          'How precious did that grace appear\nThe hour I first believed.', 'v2'),
         ('Through many dangers, toil and snares,\nI have already come;\n'
          '\'Tis grace has brought me safe thus far,\nAnd grace will lead me home.', 'v3'),
         ('When we\'ve been there ten thousand years\nBright shining as the sun,\n'
          'We\'ve no less days to sing God\'s praise\nThan when we\'ve first begun.', 'v4')],
     'verse_order_list': []},
    {'title': 'Beautiful Garden Of Prayer',
     'authors': ['Eleanor Allen Schroll James H. Fillmore'],
     'copyright': 'Public Domain',
     'ccli_number': 0,
     'verses':
     [('O the beautiful garden, the garden of prayer,\nO the beautiful garden of prayer.\n'
       'There my Savior awaits, and He opens the gates\nTo the beautiful garden of prayer.', 'c1'),
      ('There\'s a garden where Jesus is waiting,\nThere\'s a place that is wondrously fair.\n'
       'For it glows with the light of His presence,\n\'Tis the beautiful garden of prayer.', 'v1'),
      ('There\'s a garden where Jesus is waiting,\nAnd I go with my burden and care.\n'
       'Just to learn from His lips, words of comfort,\nIn the beautiful garden of prayer.', 'v2'),
      ('There\'s a garden where Jesus is waiting,\nAnd He bids you to come meet Him there,\n'
       'Just to bow and receive a new blessing,\nIn the beautiful garden of prayer.', 'v3')],
     'verse_order_list': []},
    {'title': 'Vi pløjed og vi så\'de',
     'authors': ['Matthias Claudius'],
     'copyright': 'Public Domain',
     'ccli_number': 0,
     'verses':
        [('Vi pløjed og vi så\'de\nvor sæd i sorten jord,\nså bad vi ham os hjælpe,\nsom højt i Himlen bor,\n'
          'og han lod snefald hegne\nmod frosten barsk og hård,\nhan lod det tø og regne\nog varme mildt i vår.',
          'v1'),
         ('Alle gode gaver\nde kommer ovenned,\nså tak da Gud, ja, pris dog Gud\nfor al hans kærlighed!', 'c1'),
         ('Han er jo den, hvis vilje\nopholder alle ting,\nhan klæder markens lilje\nog runder himlens ring,\n'
          'ham lyder vind og vove,\nham rører ravnes nød,\nhvi skulle ej hans småbørn\nda og få dagligt brød?', 'v2'),
         ('Ja, tak, du kære Fader,\nså mild, så rig, så rund,\nfor korn i hæs og lader,\nfor godt i allen stund!\n'
          'Vi kan jo intet give,\nsom nogen ting er værd,\nmen tag vort stakkels hjerte,\nså ringe som det er!', 'v3')],
        'verse_order_list': []}]

EWS_SONG_TEST_DATA =\
    {'title': 'Vi pløjed og vi så\'de',
     'authors': ['Matthias Claudius'],
     'verses':
        [('Vi pløjed og vi så\'de\nvor sæd i sorten jord,\nså bad vi ham os hjælpe,\nsom højt i Himlen bor,\n'
          'og han lod snefald hegne\nmod frosten barsk og hård,\nhan lod det tø og regne\nog varme mildt i vår.',
          'v1'),
         ('Alle gode gaver\nde kommer ovenned,\nså tak da Gud, ja, pris dog Gud\nfor al hans kærlighed!', 'c1'),
         ('Han er jo den, hvis vilje\nopholder alle ting,\nhan klæder markens lilje\nog runder himlens ring,\n'
          'ham lyder vind og vove,\nham rører ravnes nød,\nhvi skulle ej hans småbørn\nda og få dagligt brød?', 'v2'),
         ('Ja, tak, du kære Fader,\nså mild, så rig, så rund,\nfor korn i hæs og lader,\nfor godt i allen stund!\n'
          'Vi kan jo intet give,\nsom nogen ting er værd,\nmen tag vort stakkels hjerte,\nså ringe som det er!',
          'v3')]}


class EasyWorshipSongImportLogger(EasyWorshipSongImport):
    """
    This class logs changes in the title instance variable
    """
    _title_assignment_list = []

    def __init__(self, manager):
        EasyWorshipSongImport.__init__(self, manager, filenames=[])

    @property
    def title(self):
        return self._title_assignment_list[-1]

    @title.setter
    def title(self, title):
        self._title_assignment_list.append(title)


class TestFieldDesc:
    def __init__(self, name, field_type, size):
        self.name = name
        self.field_type = field_type
        self.size = size

TEST_DATA_ENCODING = 'cp1252'
CODE_PAGE_MAPPINGS = [
    (852, 'cp1250'), (737, 'cp1253'), (775, 'cp1257'), (855, 'cp1251'), (857, 'cp1254'),
    (866,  'cp1251'), (869, 'cp1253'), (862, 'cp1255'), (874, 'cp874')]
TEST_FIELD_DESCS = [
    TestFieldDesc('Title', FieldType.String, 50),
    TestFieldDesc('Text Percentage Bottom', FieldType.Int16, 2), TestFieldDesc('RecID', FieldType.Int32, 4),
    TestFieldDesc('Default Background', FieldType.Logical, 1), TestFieldDesc('Words', FieldType.Memo, 250),
    TestFieldDesc('Words', FieldType.Memo, 250), TestFieldDesc('BK Bitmap', FieldType.Blob, 10),
    TestFieldDesc('Last Modified', FieldType.Timestamp, 10)]
TEST_FIELDS = [
    b'A Heart Like Thine\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0', 32868, 2147483750,
    129, b'{\\rtf1\\ansi\\deff0\\deftab254{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}{\\f1\\fnil\\fcharset0 Verdana;}}'
         b'{\\colortbl\\red0\\green0\\blue0;\\red255\\green0\\blue0;\\red0\\green128\\blue0;\\red0\\green0\\blue255;'
         b'\\red255\\green255\\blue0;\\red255\\green0\\blue255;\\red128\\g\xBF\xBD\7\0f\r\0\0\1\0',
         b'{\\rtf1\\ansi\\deff0\\deftab254{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}{\\f1\\fnil\\fcharset0 Verdana;}}'
         b'{\\colortbl\\red0\\green0\\blue0;\\red255\\green0\\blue0;\\red0\\green128\\blue0;\\red0\\green0'
         b'\\blue255;\\red255'
         b'\\green255\\blue0;\\red255\\green0\\blue255;\\red128\\g\6\0\xEF\xBF\xBD\6\0\0\1\0',
         b'\0\0\0\0\0\0\0\0\0\0', 0]
GET_MEMO_FIELD_TEST_RESULTS = [
    (4, b'\2', {'return': b'\2', 'read': (1, 3430), 'seek': (507136, (8, os.SEEK_CUR))}),
    (4, b'\3', {'return': b'', 'read': (1, ), 'seek': (507136, )}),
    (5, b'\3', {'return': b'\3', 'read': (1, 1725), 'seek': (3220111360, (41, os.SEEK_CUR), 3220111408)}),
    (5, b'\4', {'return': b'', 'read': (), 'seek': ()})]


class TestEasyWorshipSongImport(TestCase):
    """
    Test the functions in the :mod:`ewimport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    def create_field_desc_entry_test(self):
        """
        Test creating an instance of the :class`FieldDescEntry` class.
        """
        # GIVEN: Set arguments
        name = 'Title'
        field_type = FieldType.String
        size = 50

        # WHEN: A FieldDescEntry object is created.
        field_desc_entry = FieldDescEntry(name, field_type, size)

        # THEN:
        self.assertIsNotNone(field_desc_entry, 'Import should not be none')
        self.assertEqual(field_desc_entry.name, name, 'FieldDescEntry.name should be the same as the name argument')
        self.assertEqual(field_desc_entry.field_type, field_type,
                         'FieldDescEntry.type should be the same as the type argument')
        self.assertEqual(field_desc_entry.size, size, 'FieldDescEntry.size should be the same as the size argument')

    def create_importer_test(self):
        """
        Test creating an instance of the EasyWorship file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])

            # THEN: The importer object should not be None
            self.assertIsNotNone(importer, 'Import should not be none')

    def find_field_exists_test(self):
        """
        Test finding an existing field in a given list using the :mod:`find_field`
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager" and a list of field descriptions.
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            importer.field_descriptions = TEST_FIELD_DESCS

            # WHEN: Called with a field name that exists
            existing_fields = ['Title', 'Text Percentage Bottom', 'RecID', 'Default Background', 'Words',
                               'BK Bitmap', 'Last Modified']
            for field_name in existing_fields:

                # THEN: The item corresponding the index returned should have the same name attribute
                self.assertEqual(importer.field_descriptions[importer.find_field(field_name)].name, field_name)

    def find_non_existing_field_test(self):
        """
        Test finding an non-existing field in a given list using the :mod:`find_field`
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager" and a list of field descriptions
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            importer.field_descriptions = TEST_FIELD_DESCS

            # WHEN: Called with a field name that does not exist
            non_existing_fields = ['BK Gradient Shading', 'BK Gradient Variant', 'Favorite', 'Copyright']
            for field_name in non_existing_fields:

                # THEN: The importer object should not be None
                self.assertRaises(IndexError, importer.find_field, field_name)

    def set_record_struct_test(self):
        """
        Test the :mod:`set_record_struct` module
        """
        # GIVEN: A mocked out SongImport class, a mocked out struct class, and a mocked out "manager" and a list of
        #       field descriptions
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.struct') as mocked_struct:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])

            # WHEN: set_record_struct is called with a list of field descriptions
            return_value = importer.set_record_struct(TEST_FIELD_DESCS)

            # THEN: set_record_struct should return None and Struct should be called with a value representing
            #       the list of field descriptions
            self.assertIsNone(return_value, 'set_record_struct should return None')
            mocked_struct.Struct.assert_called_with('>50sHIB250s250s10sQ')

    def get_field_test(self):
        """
        Test the :mod:`get_field` module
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager", an encoding and some test data and known results
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            importer.encoding = TEST_DATA_ENCODING
            importer.fields = TEST_FIELDS
            importer.field_descriptions = TEST_FIELD_DESCS
            field_results = [(0, b'A Heart Like Thine'), (1, 100), (2, 102), (3, True), (6, None), (7, None)]

            # WHEN: Called with test data
            for field_index, result in field_results:
                return_value = importer.get_field(field_index)

                # THEN: get_field should return the known results
                self.assertEqual(return_value, result,
                                 'get_field should return "%s" when called with "%s"' %
                                 (result, TEST_FIELDS[field_index]))

    def get_memo_field_test(self):
        """
        Test the :mod:`get_field` module
        """
        for test_results in GET_MEMO_FIELD_TEST_RESULTS:
            # GIVEN: A mocked out SongImport class, a mocked out "manager", a mocked out memo_file and an encoding
            with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
                mocked_manager = MagicMock()
                mocked_memo_file = MagicMock()
                importer = EasyWorshipSongImport(mocked_manager, filenames=[])
                importer.memo_file = mocked_memo_file
                importer.encoding = TEST_DATA_ENCODING

                # WHEN: Supplied with test fields and test field descriptions
                importer.fields = TEST_FIELDS
                importer.field_descriptions = TEST_FIELD_DESCS
                field_index = test_results[0]
                mocked_memo_file.read.return_value = test_results[1]
                get_field_result = test_results[2]['return']
                get_field_read_calls = test_results[2]['read']
                get_field_seek_calls = test_results[2]['seek']

                # THEN: get_field should return the appropriate value with the appropriate mocked objects being called
                self.assertEqual(importer.get_field(field_index), get_field_result)
                for call in get_field_read_calls:
                    mocked_memo_file.read.assert_any_call(call)
                for call in get_field_seek_calls:
                    if isinstance(call, int):
                        mocked_memo_file.seek.assert_any_call(call)
                    else:
                        mocked_memo_file.seek.assert_any_call(call[0], call[1])

    def do_import_source_test(self):
        """
        Test the :mod:`do_import` module opens the correct files
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.os.path') as mocked_os_path:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            mocked_os_path.isfile.side_effect = [True, False]

            # WHEN: Supplied with an import source
            importer.import_source = 'Songs.DB'

            # THEN: do_import should return None having called os.path.isfile
            self.assertIsNone(importer.do_import(), 'do_import should return None')
            mocked_os_path.isfile.assert_any_call('Songs.DB')
            mocked_os_path.isfile.assert_any_call('Songs.MB')

    def do_import_source_invalid_test(self):
        """
        Test the :mod:`do_import` module produces an error when Songs.MB not found.
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.os.path') as mocked_os_path:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            importer.log_error = MagicMock()
            mocked_os_path.isfile.side_effect = [True, False]

            # WHEN: do_import is supplied with an import source (Songs.MB missing)
            importer.import_source = 'Songs.DB'
            importer.do_import()

            # THEN: do_import should have logged an error that the Songs.MB file could not be found.
            importer.log_error.assert_any_call(importer.import_source, 'Could not find the "Songs.MB" file. It must be '
                                                                       'in the same folder as the "Songs.DB" file.')

    def do_import_database_validity_test(self):
        """
        Test the :mod:`do_import` module handles invalid database files correctly
        """
        # GIVEN: A mocked out SongImport class, os.path and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.os.path') as mocked_os_path:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            mocked_os_path.isfile.return_value = True
            importer.import_source = 'Songs.DB'

            # WHEN: DB file size is less than 0x800
            mocked_os_path.getsize.return_value = 0x7FF

            # THEN: do_import should return None having called os.path.isfile
            self.assertIsNone(importer.do_import(), 'do_import should return None when db_size is less than 0x800')
            mocked_os_path.getsize.assert_any_call('Songs.DB')

    def do_import_memo_validty_test(self):
        """
        Test the :mod:`do_import` module handles invalid memo files correctly
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
            patch('openlp.plugins.songs.lib.importers.easyworship.os.path') as mocked_os_path, \
            patch('builtins.open') as mocked_open, \
                patch('openlp.plugins.songs.lib.importers.easyworship.struct') as mocked_struct:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            mocked_os_path.isfile.return_value = True
            mocked_os_path.getsize.return_value = 0x800
            importer.import_source = 'Songs.DB'

            # WHEN: Unpacking first 35 bytes of Memo file
            struct_unpack_return_values = [(0, 0x700, 2, 0, 0), (0, 0x800, 0, 0, 0), (0, 0x800, 5, 0, 0)]
            mocked_struct.unpack.side_effect = struct_unpack_return_values

            # THEN: do_import should return None having called closed the open files db and memo files.
            for effect in struct_unpack_return_values:
                self.assertIsNone(importer.do_import(), 'do_import should return None when db_size is less than 0x800')
                self.assertEqual(mocked_open().close.call_count, 2,
                                 'The open db and memo files should have been closed')
                mocked_open().close.reset_mock()
                self.assertIs(mocked_open().seek.called, False, 'db_file.seek should not have been called.')

    def code_page_to_encoding_test(self):
        """
        Test the :mod:`do_import` converts the code page to the encoding correctly
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
            patch('openlp.plugins.songs.lib.importers.easyworship.os.path') as mocked_os_path, \
            patch('builtins.open'), patch('openlp.plugins.songs.lib.importers.easyworship.struct') as mocked_struct, \
                patch('openlp.plugins.songs.lib.importers.easyworship.retrieve_windows_encoding') as \
                mocked_retrieve_windows_encoding:
            mocked_manager = MagicMock()
            importer = EasyWorshipSongImport(mocked_manager, filenames=[])
            mocked_os_path.isfile.return_value = True
            mocked_os_path.getsize.return_value = 0x800
            importer.import_source = 'Songs.DB'

            # WHEN: Unpacking the code page
            for code_page, encoding in CODE_PAGE_MAPPINGS:
                struct_unpack_return_values = [(0, 0x800, 2, 0, 0), (code_page, )]
                mocked_struct.unpack.side_effect = struct_unpack_return_values
                mocked_retrieve_windows_encoding.return_value = False

                # THEN: do_import should return None having called retrieve_windows_encoding with the correct encoding.
                self.assertIsNone(importer.do_import(), 'do_import should return None when db_size is less than 0x800')
                mocked_retrieve_windows_encoding.assert_call(encoding)

    def db_file_import_test(self):
        """
        Test the actual import of real song database files and check that the imported data is correct.
        """

        # GIVEN: Test files with a mocked out SongImport class, a mocked out "manager", a mocked out "import_wizard",
        #       and mocked out "author", "add_copyright", "add_verse", "finish" methods.
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.retrieve_windows_encoding') as \
                mocked_retrieve_windows_encoding:
            mocked_retrieve_windows_encoding.return_value = 'cp1252'
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            mocked_add_author = MagicMock()
            mocked_add_verse = MagicMock()
            mocked_finish = MagicMock()
            mocked_title = MagicMock()
            mocked_finish.return_value = True
            importer = EasyWorshipSongImportLogger(mocked_manager)
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = False
            importer.add_author = mocked_add_author
            importer.add_verse = mocked_add_verse
            importer.title = mocked_title
            importer.finish = mocked_finish
            importer.topics = []

            # WHEN: Importing each file
            importer.import_source = os.path.join(TEST_PATH, 'Songs.DB')
            import_result = importer.do_import()

            # THEN: do_import should return none, the song data should be as expected, and finish should have been
            #       called.
            self.assertIsNone(import_result, 'do_import should return None when it has completed')
            for song_data in SONG_TEST_DATA:
                title = song_data['title']
                author_calls = song_data['authors']
                song_copyright = song_data['copyright']
                ccli_number = song_data['ccli_number']
                add_verse_calls = song_data['verses']
                verse_order_list = song_data['verse_order_list']
                self.assertIn(title, importer._title_assignment_list, 'title for %s should be "%s"' % (title, title))
                for author in author_calls:
                    mocked_add_author.assert_any_call(author)
                if song_copyright:
                    self.assertEqual(importer.copyright, song_copyright)
                if ccli_number:
                    self.assertEqual(importer.ccli_number, ccli_number,
                                     'ccli_number for %s should be %s' % (title, ccli_number))
                for verse_text, verse_tag in add_verse_calls:
                    mocked_add_verse.assert_any_call(verse_text, verse_tag)
                if verse_order_list:
                    self.assertEqual(importer.verse_order_list, verse_order_list,
                                     'verse_order_list for %s should be %s' % (title, verse_order_list))
                mocked_finish.assert_called_with()

    def ews_file_import_test(self):
        """
        Test the actual import of song from ews file and check that the imported data is correct.
        """

        # GIVEN: Test files with a mocked out SongImport class, a mocked out "manager", a mocked out "import_wizard",
        #       and mocked out "author", "add_copyright", "add_verse", "finish" methods.
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'), \
                patch('openlp.plugins.songs.lib.importers.easyworship.retrieve_windows_encoding') \
                as mocked_retrieve_windows_encoding:
            mocked_retrieve_windows_encoding.return_value = 'cp1252'
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            mocked_add_author = MagicMock()
            mocked_add_verse = MagicMock()
            mocked_finish = MagicMock()
            mocked_title = MagicMock()
            mocked_finish.return_value = True
            importer = EasyWorshipSongImportLogger(mocked_manager)
            importer.import_wizard = mocked_import_wizard
            importer.stop_import_flag = False
            importer.add_author = mocked_add_author
            importer.add_verse = mocked_add_verse
            importer.title = mocked_title
            importer.finish = mocked_finish
            importer.topics = []

            # WHEN: Importing ews file
            importer.import_source = os.path.join(TEST_PATH, 'test1.ews')
            import_result = importer.do_import()

            # THEN: do_import should return none, the song data should be as expected, and finish should have been
            #       called.
            title = EWS_SONG_TEST_DATA['title']
            self.assertIsNone(import_result, 'do_import should return None when it has completed')
            self.assertIn(title, importer._title_assignment_list, 'title for should be "%s"' % title)
            mocked_add_author.assert_any_call(EWS_SONG_TEST_DATA['authors'][0])
            for verse_text, verse_tag in EWS_SONG_TEST_DATA['verses']:
                mocked_add_verse.assert_any_call(verse_text, verse_tag)
            mocked_finish.assert_called_with()

    def import_rtf_unescaped_unicode_test(self):
        """
        Test import of rtf without the expected escaping of unicode
        """

        # GIVEN: A mocked out SongImport class, a mocked out "manager" and mocked out "author" method.
        with patch('openlp.plugins.songs.lib.importers.easyworship.SongImport'):
            mocked_manager = MagicMock()
            mocked_add_author = MagicMock()
            importer = EasyWorshipSongImportLogger(mocked_manager)
            importer.add_author = mocked_add_author
            importer.encoding = 'cp1252'

            # WHEN: running set_song_import_object on a verse string without the needed escaping
            importer.set_song_import_object('Test Author', b'Det som var fr\x86n begynnelsen')

            # THEN: The import should fail
            self.assertEquals(importer.entry_error_log, 'Unexpected data formatting.', 'Import should fail')
