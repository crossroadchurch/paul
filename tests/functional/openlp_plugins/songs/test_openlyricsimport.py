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
This module contains tests for the OpenLyrics song importer.
"""

import os
import json
from unittest import TestCase
from lxml import etree, objectify

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin
from openlp.plugins.songs.lib.importers.openlyrics import OpenLyricsImport
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics
from openlp.core.common import Registry, Settings


TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..', 'resources', 'openlyricssongs'))
SONG_TEST_DATA = {
    'What a friend we have in Jesus.xml': {
        'title': 'What A Friend We Have In Jesus',
        'verses': [
            ('What a friend we have in Jesus, All ours sins and griefs to bear;\n\
             What a privilege to carry, Everything to God in prayer!\n\
             O what peace we often forfeit, O what needless pain we bear;\n\
             All because we do not carry, Everything to God in prayer!', 'v1'),
            ('Have we trials and temptations? Is there trouble anywhere?\n\
             We should never be discouraged, Take it to the Lord in prayer.\n\
             Can we find a friend so faithful? Who will all our sorrows share?\n\
             Jesus knows our every weakness; Take it to the Lord in prayer.', 'v2'),
            ('Are we weak and heavy laden, Cumbered with a load of care?\n\
             Precious Saviour still our refuge; Take it to the Lord in prayer.\n\
             Do thy friends despise forsake thee? Take it to the Lord in prayer!\n\
             In His arms He’ll take and shield thee; Thou wilt find a solace there.', 'v3')
        ]
    }
}

start_tags = [{"protected": False, "desc": "z", "start tag": "{z}", "end html": "</strong>", "temporary": False,
               "end tag": "{/z}", "start html": "strong>"}]
result_tags = [{"temporary": False, "protected": False, "desc": "z", "start tag": "{z}", "start html": "strong>",
                "end html": "</strong>", "end tag": "{/z}"},
               {"temporary": False, "end tag": "{/c}", "desc": "c", "start tag": "{c}",
                "start html": "<span class=\"chord\" style=\"display:none\"><strong>", "end html": "</strong></span>",
                "protected": False}]

author_xml = '<properties>\
                  <authors>\
                      <author type="words">Test Author1</author>\
                      <author type="music">Test Author1</author>\
                      <author type="words">Test Author2</author>\
                  </authors>\
            </properties>'


class TestOpenLyricsImport(TestCase, TestMixin):
    """
    Test the functions in the :mod:`openlyricsimport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        self.setup_application()
        Registry.create()
        self.build_settings()

    def tearDown(self):
        """
        Cleanup
        """
        self.destroy_settings()

    def create_importer_test(self):
        """
        Test creating an instance of the OpenLyrics file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.openlyrics.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = OpenLyricsImport(mocked_manager, filenames=[])

            # THEN: The importer should be an instance of SongImport
            self.assertIsInstance(importer, SongImport)

    def file_import_test(self):
        """
        Test the actual import of real song files
        """
        # GIVEN: Test files with a mocked out "manager" and a mocked out "import_wizard"
        for song_file in SONG_TEST_DATA:
            mocked_manager = MagicMock()
            mocked_import_wizard = MagicMock()
            importer = OpenLyricsImport(mocked_manager, filenames=[])
            importer.import_wizard = mocked_import_wizard
            importer.open_lyrics = MagicMock()
            importer.open_lyrics.xml_to_song = MagicMock()

            # WHEN: Importing each file
            importer.import_source = [os.path.join(TEST_PATH, song_file)]
            importer.do_import()

            # THEN: The xml_to_song() method should have been called
            self.assertTrue(importer.open_lyrics.xml_to_song.called)

    def process_formatting_tags_test(self):
        """
        Test that _process_formatting_tags works
        """
        # GIVEN: A OpenLyric XML with formatting tags and a mocked out manager
        mocked_manager = MagicMock()
        Settings().setValue('formattingTags/html_tags', json.dumps(start_tags))
        ol = OpenLyrics(mocked_manager)
        parser = etree.XMLParser(remove_blank_text=True)
        parsed_file = etree.parse(open(os.path.join(TEST_PATH, 'duchu-tags.xml'), 'rb'), parser)
        xml = etree.tostring(parsed_file).decode()
        song_xml = objectify.fromstring(xml)

        # WHEN: processing the formatting tags
        ol._process_formatting_tags(song_xml, False)

        # THEN: New tags should have been saved
        self.assertListEqual(json.loads(json.dumps(result_tags)),
                             json.loads(str(Settings().value('formattingTags/html_tags'))),
                             'The formatting tags should contain both the old and the new')

    def process_author_test(self):
        """
        Test that _process_authors works
        """
        # GIVEN: A OpenLyric XML with authors and a mocked out manager
        with patch('openlp.plugins.songs.lib.openlyricsxml.Author') as mocked_author:
            mocked_manager = MagicMock()
            mocked_manager.get_object_filtered.return_value = None
            ol = OpenLyrics(mocked_manager)
            properties_xml = objectify.fromstring(author_xml)
            mocked_song = MagicMock()

            # WHEN: processing the author xml
            ol._process_authors(properties_xml, mocked_song)

            # THEN: add_author should have been called twice
            self.assertEquals(mocked_song.method_calls[0][1][1], 'words+music')
            self.assertEquals(mocked_song.method_calls[1][1][1], 'words')
