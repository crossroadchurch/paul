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
This module contains tests for the OpenSong Bible importer.
"""

import os
import json
from unittest import TestCase

from tests.functional import MagicMock, patch
from openlp.plugins.bibles.lib.opensong import OpenSongBible
from openlp.plugins.bibles.lib.db import BibleDB

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..', 'resources', 'bibles'))


class TestOpenSongImport(TestCase):
    """
    Test the functions in the :mod:`opensongimport` module.
    """

    def setUp(self):
        self.registry_patcher = patch('openlp.plugins.bibles.lib.db.Registry')
        self.registry_patcher.start()
        self.manager_patcher = patch('openlp.plugins.bibles.lib.db.Manager')
        self.manager_patcher.start()

    def tearDown(self):
        self.registry_patcher.stop()
        self.manager_patcher.stop()

    def create_importer_test(self):
        """
        Test creating an instance of the OpenSong file importer
        """
        # GIVEN: A mocked out "manager"
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = OpenSongBible(mocked_manager, path='.', name='.', filename='')

        # THEN: The importer should be an instance of BibleDB
        self.assertIsInstance(importer, BibleDB)

    def file_import_test(self):
        """
        Test the actual import of OpenSong Bible file
        """
        # GIVEN: Test files with a mocked out "manager", "import_wizard", and mocked functions
        #       get_book_ref_id_by_name, create_verse, create_book, session and get_language.
        result_file = open(os.path.join(TEST_PATH, 'dk1933.json'), 'rb')
        test_data = json.loads(result_file.read().decode())
        bible_file = 'opensong-dk1933.xml'
        with patch('openlp.plugins.bibles.lib.opensong.OpenSongBible.application'):
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = OpenSongBible(mocked_manager, path='.', name='.', filename='')
            importer.wizard = mocked_import_wizard
            importer.get_book_ref_id_by_name = MagicMock()
            importer.create_verse = MagicMock()
            importer.create_book = MagicMock()
            importer.session = MagicMock()
            importer.get_language = MagicMock()
            importer.get_language.return_value = 'Danish'

            # WHEN: Importing bible file
            importer.filename = os.path.join(TEST_PATH, bible_file)
            importer.do_import()

            # THEN: The create_verse() method should have been called with each verse in the file.
            self.assertTrue(importer.create_verse.called)
            for verse_tag, verse_text in test_data['verses']:
                importer.create_verse.assert_any_call(importer.create_book().id, 1, int(verse_tag), verse_text)

    def zefania_import_error_test(self):
        """
        Test that we give an error message if trying to import a zefania bible
        """
        # GIVEN: A mocked out "manager" and mocked out critical_error_message_box and an import
        with patch('openlp.plugins.bibles.lib.opensong.critical_error_message_box') as \
                mocked_critical_error_message_box:
            mocked_manager = MagicMock()
            importer = OpenSongBible(mocked_manager, path='.', name='.', filename='')

            # WHEN: An trying to import a zefania bible
            importer.filename = os.path.join(TEST_PATH, 'zefania-dk1933.xml')
            importer.do_import()

            # THEN: The importer should have "shown" an error message
            mocked_critical_error_message_box.assert_called_with(message='Incorrect Bible file type supplied. '
                                                                 'This looks like a Zefania XML bible, '
                                                                 'please use the Zefania import option.')
