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
This module contains tests for the SongShow Plus song importer.
"""

import os
from unittest import TestCase
from tests.functional import patch, MagicMock

from openlp.plugins.songs.lib.importers.foilpresenter import FoilPresenter

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '/resources/foilpresentersongs'))


class TestFoilPresenter(TestCase):
    """
    Test the functions in the :mod:`foilpresenterimport` module.
    """
    # TODO: The following modules still need tests written for
    #   xml_to_song
    #   _child
    #   _process_authors
    #   _process_cclinumber
    #   _process_comments
    #   _process_copyright
    #   _process_lyrics
    #   _process_songbooks
    #   _process_titles
    #   _process_topics

    def setUp(self):
        self.child_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._child')
        self.clean_song_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.clean_song')
        self.objectify_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.objectify')
        self.process_authors_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_authors')
        self.process_cclinumber_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_cclinumber')
        self.process_comments_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_comments')
        self.process_lyrics_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_lyrics')
        self.process_songbooks_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_songbooks')
        self.process_titles_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_titles')
        self.process_topics_patcher = \
            patch('openlp.plugins.songs.lib.importers.foilpresenter.FoilPresenter._process_topics')
        self.re_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.re')
        self.song_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.Song')
        self.song_xml_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.SongXML')
        self.translate_patcher = patch('openlp.plugins.songs.lib.importers.foilpresenter.translate')

        self.mocked_child = self.child_patcher.start()
        self.mocked_clean_song = self.clean_song_patcher.start()
        self.mocked_objectify = self.objectify_patcher.start()
        self.mocked_process_authors = self.process_authors_patcher.start()
        self.mocked_process_cclinumber = self.process_cclinumber_patcher.start()
        self.mocked_process_comments = self.process_comments_patcher.start()
        self.mocked_process_lyrics = self.process_lyrics_patcher.start()
        self.mocked_process_songbooks = self.process_songbooks_patcher.start()
        self.mocked_process_titles = self.process_titles_patcher.start()
        self.mocked_process_topics = self.process_topics_patcher.start()
        self.mocked_re = self.re_patcher.start()
        self.mocked_song = self.song_patcher.start()
        self.mocked_song_xml = self.song_xml_patcher.start()
        self.mocked_translate = self.translate_patcher.start()
        self.mocked_child.return_value = 'Element Text'
        self.mocked_translate.return_value = 'Translated String'
        self.mocked_manager = MagicMock()
        self.mocked_song_import = MagicMock()

    def tearDown(self):
        self.child_patcher.stop()
        self.clean_song_patcher.stop()
        self.objectify_patcher.stop()
        self.process_authors_patcher.stop()
        self.process_cclinumber_patcher.stop()
        self.process_comments_patcher.stop()
        self.process_lyrics_patcher.stop()
        self.process_songbooks_patcher.stop()
        self.process_titles_patcher.stop()
        self.process_topics_patcher.stop()
        self.re_patcher.stop()
        self.song_patcher.stop()
        self.song_xml_patcher.stop()
        self.translate_patcher.stop()

    def create_foil_presenter_test(self):
        """
        Test creating an instance of the foil_presenter class
        """
        # GIVEN: A mocked out "manager" and "SongImport" instance
        mocked_manager = MagicMock()
        mocked_song_import = MagicMock()

        # WHEN: An foil_presenter instance is created
        foil_presenter_instance = FoilPresenter(mocked_manager, mocked_song_import)

        # THEN: The instance should not be None
        self.assertIsNotNone(foil_presenter_instance, 'foil_presenter instance should not be none')

    def no_xml_test(self):
        """
        Test calling xml_to_song with out the xml argument
        """
        # GIVEN: A mocked out "manager" and "SongImport" as well as an foil_presenter instance
        mocked_manager = MagicMock()
        mocked_song_import = MagicMock()
        foil_presenter_instance = FoilPresenter(mocked_manager, mocked_song_import)

        # WHEN: xml_to_song is called without valid an argument
        for arg in [None, False, 0, '']:
            result = foil_presenter_instance.xml_to_song(arg)

            # Then: xml_to_song should return False
            self.assertEqual(result, None, 'xml_to_song should return None when called with %s' % arg)

    def encoding_declaration_removal_test(self):
        """
        Test that the encoding declaration is removed
        """
        # GIVEN: A reset mocked out re and an instance of foil_presenter
        self.mocked_re.reset()
        foil_presenter_instance = FoilPresenter(self.mocked_manager, self.mocked_song_import)

        # WHEN: xml_to_song is called with a string with an xml encoding declaration
        foil_presenter_instance.xml_to_song('<?xml version="1.0" encoding="UTF-8"?>\n<foilpresenterfolie>')

        # THEN: the xml encoding declaration should have been stripped
        self.mocked_re.compile.sub.called_with('\n<foilpresenterfolie>')

    def no_encoding_declaration_test(self):
        """
        Check that the xml sting is left intact when no encoding declaration is made
        """
        # GIVEN: A reset mocked out re and an instance of foil_presenter
        self.mocked_re.reset()
        foil_presenter_instance = FoilPresenter(self.mocked_manager, self.mocked_song_import)

        # WHEN: xml_to_song is called with a string without an xml encoding declaration
        foil_presenter_instance.xml_to_song('<foilpresenterfolie>')

        # THEN: the string should have been left intact
        self.mocked_re.compile.sub.called_with('<foilpresenterfolie>')

    def process_lyrics_no_verses_test(self):
        """
        Test that _process_lyrics handles song files that have no verses.
        """
        # GIVEN: A mocked foilpresenterfolie with no attribute strophe, a mocked song and a
        #       foil presenter instance
        self.process_lyrics_patcher.stop()
        self.mocked_song_xml.reset()
        mock_foilpresenterfolie = MagicMock()
        del mock_foilpresenterfolie.strophen.strophe
        mocked_song = MagicMock()
        foil_presenter_instance = FoilPresenter(self.mocked_manager, self.mocked_song_import)

        # WHEN: _process_lyrics is called
        result = foil_presenter_instance._process_lyrics(mock_foilpresenterfolie, mocked_song)

        # THEN: _process_lyrics should return None and the song_import log_error method should have been called once
        self.assertIsNone(result)
        self.mocked_song_import.log_error.assert_called_once_with('Element Text', 'Translated String')
        self.process_lyrics_patcher.start()
