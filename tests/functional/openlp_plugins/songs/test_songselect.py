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
This module contains tests for the CCLI SongSelect importer.
"""
import os
from unittest import TestCase
from urllib.error import URLError

from PyQt4 import QtGui

from openlp.core import Registry
from openlp.plugins.songs.forms.songselectform import SongSelectForm, SearchWorker
from openlp.plugins.songs.lib import Song
from openlp.plugins.songs.lib.songselect import SongSelectImport, LOGOUT_URL, BASE_URL
from openlp.plugins.songs.lib.importers.cclifile import CCLIFileImport

from tests.functional import MagicMock, patch, call
from tests.helpers.testmixin import TestMixin


class TestSongSelectImport(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.lib.songselect.SongSelectImport` class
    """
    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def constructor_test(self, mocked_build_opener):
        """
        Test that constructing a basic SongSelectImport object works correctly
        """
        # GIVEN: The SongSelectImporter class and a mocked out build_opener
        # WHEN: An object is instantiated
        importer = SongSelectImport(None)

        # THEN: The object should have the correct properties
        self.assertIsNone(importer.db_manager, 'The db_manager should be None')
        self.assertIsNotNone(importer.html_parser, 'There should be a valid html_parser object')
        self.assertIsNotNone(importer.opener, 'There should be a valid opener object')
        self.assertEqual(1, mocked_build_opener.call_count, 'The build_opener method should have been called once')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def login_fails_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when logging in to SongSelect fails, the login method returns False
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_login_page = MagicMock()
        mocked_login_page.find.return_value = {'value': 'blah'}
        MockedBeautifulSoup.return_value = mocked_login_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 3 times, open was called twice, find was called twice, and False was returned
        self.assertEqual(3, mock_callback.call_count, 'callback should have been called 3 times')
        self.assertEqual(2, mocked_login_page.find.call_count, 'find should have been called twice')
        self.assertEqual(2, mocked_opener.open.call_count, 'opener should have been called twice')
        self.assertFalse(result, 'The login method should have returned False')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def login_except_test(self,  mocked_build_opener):
        """
        Test that when logging in to SongSelect fails, the login method raises URLError
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_build_opener.open.side_effect = URLError('Fake URLError')
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 1 time and False was returned
        self.assertEqual(1, mock_callback.call_count, 'callback should have been called 1 times')
        self.assertFalse(result, 'The login method should have returned False')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def login_succeeds_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when logging in to SongSelect succeeds, the login method returns True
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_login_page = MagicMock()
        mocked_login_page.find.side_effect = [{'value': 'blah'}, None]
        MockedBeautifulSoup.return_value = mocked_login_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        result = importer.login('username', 'password', mock_callback)

        # THEN: callback was called 3 times, open was called twice, find was called twice, and True was returned
        self.assertEqual(3, mock_callback.call_count, 'callback should have been called 3 times')
        self.assertEqual(2, mocked_login_page.find.call_count, 'find should have been called twice')
        self.assertEqual(2, mocked_opener.open.call_count, 'opener should have been called twice')
        self.assertTrue(result, 'The login method should have returned True')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def logout_test(self, mocked_build_opener):
        """
        Test that when the logout method is called, it logs the user out of SongSelect
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        importer.logout()

        # THEN: The opener is called once with the logout url
        self.assertEqual(1, mocked_opener.open.call_count, 'opener should have been called once')
        mocked_opener.open.assert_called_with(LOGOUT_URL)

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def search_returns_no_results_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds no results, it simply returns an empty list
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.return_value = []
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        results = importer.search('text', 1000, mock_callback)

        # THEN: callback was never called, open was called once, find_all was called once, an empty list returned
        self.assertEqual(0, mock_callback.call_count, 'callback should not have been called')
        self.assertEqual(1, mocked_opener.open.call_count, 'open should have been called once')
        self.assertEqual(1, mocked_results_page.find_all.call_count, 'find_all should have been called once')
        mocked_results_page.find_all.assert_called_with('li', 'result pane')
        self.assertEqual([], results, 'The search method should have returned an empty list')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def search_returns_two_results_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds 2 results, it simply returns a list with 2 results
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        # first search result
        mocked_result1 = MagicMock()
        mocked_result1.find.side_effect = [MagicMock(string='Title 1'), {'href': '/url1'}]
        mocked_result1.find_all.return_value = [MagicMock(string='Author 1-1'), MagicMock(string='Author 1-2')]
        # second search result
        mocked_result2 = MagicMock()
        mocked_result2.find.side_effect = [MagicMock(string='Title 2'), {'href': '/url2'}]
        mocked_result2.find_all.return_value = [MagicMock(string='Author 2-1'), MagicMock(string='Author 2-2')]
        # rest of the stuff
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.side_effect = [[mocked_result1, mocked_result2], []]
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        results = importer.search('text', 1000, mock_callback)

        # THEN: callback was never called, open was called once, find_all was called once, an empty list returned
        self.assertEqual(2, mock_callback.call_count, 'callback should have been called twice')
        self.assertEqual(2, mocked_opener.open.call_count, 'open should have been called twice')
        self.assertEqual(2, mocked_results_page.find_all.call_count, 'find_all should have been called twice')
        mocked_results_page.find_all.assert_called_with('li', 'result pane')
        expected_list = [
            {'title': 'Title 1', 'authors': ['Author 1-1', 'Author 1-2'], 'link': BASE_URL + '/url1'},
            {'title': 'Title 2', 'authors': ['Author 2-1', 'Author 2-2'], 'link': BASE_URL + '/url2'}
        ]
        self.assertListEqual(expected_list, results, 'The search method should have returned two songs')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def search_reaches_max_results_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when the search finds MAX (2) results, it simply returns a list with those (2)
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        # first search result
        mocked_result1 = MagicMock()
        mocked_result1.find.side_effect = [MagicMock(string='Title 1'), {'href': '/url1'}]
        mocked_result1.find_all.return_value = [MagicMock(string='Author 1-1'), MagicMock(string='Author 1-2')]
        # second search result
        mocked_result2 = MagicMock()
        mocked_result2.find.side_effect = [MagicMock(string='Title 2'), {'href': '/url2'}]
        mocked_result2.find_all.return_value = [MagicMock(string='Author 2-1'), MagicMock(string='Author 2-2')]
        # third search result
        mocked_result3 = MagicMock()
        mocked_result3.find.side_effect = [MagicMock(string='Title 3'), {'href': '/url3'}]
        mocked_result3.find_all.return_value = [MagicMock(string='Author 3-1'), MagicMock(string='Author 3-2')]
        # rest of the stuff
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_results_page = MagicMock()
        mocked_results_page.find_all.side_effect = [[mocked_result1, mocked_result2, mocked_result3], []]
        MockedBeautifulSoup.return_value = mocked_results_page
        mock_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: The login method is called after being rigged to fail
        results = importer.search('text', 2, mock_callback)

        # THEN: callback was never called, open was called once, find_all was called once, an empty list returned
        self.assertEqual(2, mock_callback.call_count, 'callback should have been called twice')
        self.assertEqual(2, mocked_opener.open.call_count, 'open should have been called twice')
        self.assertEqual(2, mocked_results_page.find_all.call_count, 'find_all should have been called twice')
        mocked_results_page.find_all.assert_called_with('li', 'result pane')
        expected_list = [{'title': 'Title 1', 'authors': ['Author 1-1', 'Author 1-2'], 'link': BASE_URL + '/url1'},
                         {'title': 'Title 2', 'authors': ['Author 2-1', 'Author 2-2'], 'link': BASE_URL + '/url2'}]
        self.assertListEqual(expected_list, results, 'The search method should have returned two songs')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    def get_song_page_raises_exception_test(self, mocked_build_opener):
        """
        Test that when BeautifulSoup gets a bad song page the get_song() method returns None
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_opener = MagicMock()
        mocked_build_opener.return_value = mocked_opener
        mocked_opener.open.read.side_effect = URLError('[Errno -2] Name or service not known')
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: get_song is called
        result = importer.get_song({'link': 'link'}, callback=mocked_callback)

        # THEN: The callback should have been called once and None should be returned
        mocked_callback.assert_called_with()
        self.assertIsNone(result, 'The get_song() method should have returned None')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def get_song_lyrics_raise_exception_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that when BeautifulSoup gets a bad lyrics page the get_song() method returns None
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        MockedBeautifulSoup.side_effect = [None, TypeError('Test Error')]
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)

        # WHEN: get_song is called
        result = importer.get_song({'link': 'link'}, callback=mocked_callback)

        # THEN: The callback should have been called twice and None should be returned
        self.assertEqual(2, mocked_callback.call_count, 'The callback should have been called twice')
        self.assertIsNone(result, 'The get_song() method should have returned None')

    @patch('openlp.plugins.songs.lib.songselect.build_opener')
    @patch('openlp.plugins.songs.lib.songselect.BeautifulSoup')
    def get_song_test(self, MockedBeautifulSoup, mocked_build_opener):
        """
        Test that the get_song() method returns the correct song details
        """
        # GIVEN: A bunch of mocked out stuff and an importer object
        mocked_song_page = MagicMock()
        mocked_copyright = MagicMock()
        mocked_copyright.find_all.return_value = [MagicMock(string='Copyright 1'), MagicMock(string='Copyright 2')]
        mocked_song_page.find.side_effect = [
            mocked_copyright,
            MagicMock(find=MagicMock(string='CCLI: 123456'))
        ]
        mocked_lyrics_page = MagicMock()
        mocked_find_all = MagicMock()
        mocked_find_all.side_effect = [
            [
                MagicMock(contents='The Lord told Noah: there\'s gonna be a floody, floody'),
                MagicMock(contents='So, rise and shine, and give God the glory, glory'),
                MagicMock(contents='The Lord told Noah to build him an arky, arky')
            ],
            [MagicMock(string='Verse 1'), MagicMock(string='Chorus'), MagicMock(string='Verse 2')]
        ]
        mocked_lyrics_page.find.return_value = MagicMock(find_all=mocked_find_all)
        MockedBeautifulSoup.side_effect = [mocked_song_page, mocked_lyrics_page]
        mocked_callback = MagicMock()
        importer = SongSelectImport(None)
        fake_song = {'title': 'Title', 'authors': ['Author 1', 'Author 2'], 'link': 'url'}

        # WHEN: get_song is called
        result = importer.get_song(fake_song, callback=mocked_callback)

        # THEN: The callback should have been called three times and the song should be returned
        self.assertEqual(3, mocked_callback.call_count, 'The callback should have been called twice')
        self.assertIsNotNone(result, 'The get_song() method should have returned a song dictionary')
        self.assertEqual(2, mocked_lyrics_page.find.call_count, 'The find() method should have been called twice')
        self.assertEqual(2, mocked_find_all.call_count, 'The find_all() method should have been called twice')
        self.assertEqual([call('section', 'lyrics'), call('section', 'lyrics')],
                         mocked_lyrics_page.find.call_args_list,
                         'The find() method should have been called with the right arguments')
        self.assertEqual([call('p'), call('h3')], mocked_find_all.call_args_list,
                         'The find_all() method should have been called with the right arguments')
        self.assertIn('copyright', result, 'The returned song should have a copyright')
        self.assertIn('ccli_number', result, 'The returned song should have a CCLI number')
        self.assertIn('verses', result, 'The returned song should have verses')
        self.assertEqual(3, len(result['verses']), 'Three verses should have been returned')

    @patch('openlp.plugins.songs.lib.songselect.clean_song')
    @patch('openlp.plugins.songs.lib.songselect.Author')
    def save_song_new_author_test(self, MockedAuthor, mocked_clean_song):
        """
        Test that saving a song with a new author performs the correct actions
        """
        # GIVEN: A song to save, and some mocked out objects
        song_dict = {
            'title': 'Arky Arky',
            'authors': ['Public Domain'],
            'verses': [
                {'label': 'Verse 1', 'lyrics': 'The Lord told Noah: there\'s gonna be a floody, floody'},
                {'label': 'Chorus 1', 'lyrics': 'So, rise and shine, and give God the glory, glory'},
                {'label': 'Verse 2', 'lyrics': 'The Lord told Noah to build him an arky, arky'}
            ],
            'copyright': 'Public Domain',
            'ccli_number': '123456'
        }
        MockedAuthor.display_name.__eq__.return_value = False
        mocked_db_manager = MagicMock()
        mocked_db_manager.get_object_filtered.return_value = None
        importer = SongSelectImport(mocked_db_manager)

        # WHEN: The song is saved to the database
        result = importer.save_song(song_dict)

        # THEN: The return value should be a Song class and the mocked_db_manager should have been called
        self.assertIsInstance(result, Song, 'The returned value should be a Song object')
        mocked_clean_song.assert_called_with(mocked_db_manager, result)
        self.assertEqual(2, mocked_db_manager.save_object.call_count,
                         'The save_object() method should have been called twice')
        mocked_db_manager.get_object_filtered.assert_called_with(MockedAuthor, False)
        MockedAuthor.populate.assert_called_with(first_name='Public', last_name='Domain',
                                                 display_name='Public Domain')
        self.assertEqual(1, len(result.authors_songs), 'There should only be one author')

    @patch('openlp.plugins.songs.lib.songselect.clean_song')
    @patch('openlp.plugins.songs.lib.songselect.Author')
    def save_song_existing_author_test(self, MockedAuthor, mocked_clean_song):
        """
        Test that saving a song with an existing author performs the correct actions
        """
        # GIVEN: A song to save, and some mocked out objects
        song_dict = {
            'title': 'Arky Arky',
            'authors': ['Public Domain'],
            'verses': [
                {'label': 'Verse 1', 'lyrics': 'The Lord told Noah: there\'s gonna be a floody, floody'},
                {'label': 'Chorus 1', 'lyrics': 'So, rise and shine, and give God the glory, glory'},
                {'label': 'Verse 2', 'lyrics': 'The Lord told Noah to build him an arky, arky'}
            ],
            'copyright': 'Public Domain',
            'ccli_number': '123456'
        }
        MockedAuthor.display_name.__eq__.return_value = False
        mocked_db_manager = MagicMock()
        mocked_db_manager.get_object_filtered.return_value = MagicMock()
        importer = SongSelectImport(mocked_db_manager)

        # WHEN: The song is saved to the database
        result = importer.save_song(song_dict)

        # THEN: The return value should be a Song class and the mocked_db_manager should have been called
        self.assertIsInstance(result, Song, 'The returned value should be a Song object')
        mocked_clean_song.assert_called_with(mocked_db_manager, result)
        self.assertEqual(2, mocked_db_manager.save_object.call_count,
                         'The save_object() method should have been called twice')
        mocked_db_manager.get_object_filtered.assert_called_with(MockedAuthor, False)
        self.assertEqual(0, MockedAuthor.populate.call_count, 'A new author should not have been instantiated')
        self.assertEqual(1, len(result.authors_songs), 'There should only be one author')


class TestSongSelectForm(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.forms.songselectform.SongSelectForm` class
    """
    def setUp(self):
        """
        Some set up for this test suite
        """
        self.setup_application()
        self.app.setApplicationVersion('0.0')
        self.app.process_events = lambda: None
        Registry.create()
        Registry().register('application', self.app)

    def create_form_test(self):
        """
        Test that we can create the SongSelect form
        """
        # GIVEN: The SongSelectForm class and a mocked db manager
        mocked_plugin = MagicMock()
        mocked_db_manager = MagicMock()

        # WHEN: We create an instance
        ssform = SongSelectForm(None, mocked_plugin, mocked_db_manager)

        # THEN: The correct properties should have been assigned
        self.assertEqual(mocked_plugin, ssform.plugin, 'The correct plugin should have been assigned')
        self.assertEqual(mocked_db_manager, ssform.db_manager, 'The correct db_manager should have been assigned')

    @patch('openlp.plugins.songs.forms.songselectform.SongSelectImport')
    @patch('openlp.plugins.songs.forms.songselectform.QtGui.QMessageBox.critical')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def login_fails_test(self, mocked_translate, mocked_critical, MockedSongSelectImport):
        """
        Test that when the login fails, the form returns to the correct state
        """
        # GIVEN: A valid SongSelectForm with a mocked out SongSelectImport, and a bunch of mocked out controls
        mocked_song_select_import = MagicMock()
        mocked_song_select_import.login.return_value = False
        MockedSongSelectImport.return_value = mocked_song_select_import
        mocked_translate.side_effect = lambda *args: args[1]
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        ssform.initialise()
        with patch.object(ssform, 'username_edit') as mocked_username_edit, \
                patch.object(ssform, 'password_edit') as mocked_password_edit, \
                patch.object(ssform, 'save_password_checkbox') as mocked_save_password_checkbox, \
                patch.object(ssform, 'login_button') as mocked_login_button, \
                patch.object(ssform, 'login_spacer') as mocked_login_spacer, \
                patch.object(ssform, 'login_progress_bar') as mocked_login_progress_bar, \
                patch.object(ssform.application, 'process_events') as mocked_process_events:

            # WHEN: The login button is clicked, and the login is rigged to fail
            ssform.on_login_button_clicked()

            # THEN: The right things should have happened in the right order
            expected_username_calls = [call(False), call(True)]
            expected_password_calls = [call(False), call(True)]
            expected_save_password_calls = [call(False), call(True)]
            expected_login_btn_calls = [call(False), call(True)]
            expected_login_spacer_calls = [call(False), call(True)]
            expected_login_progress_visible_calls = [call(True), call(False)]
            expected_login_progress_value_calls = [call(0), call(0)]
            self.assertEqual(expected_username_calls, mocked_username_edit.setEnabled.call_args_list,
                             'The username edit should be disabled then enabled')
            self.assertEqual(expected_password_calls, mocked_password_edit.setEnabled.call_args_list,
                             'The password edit should be disabled then enabled')
            self.assertEqual(expected_save_password_calls, mocked_save_password_checkbox.setEnabled.call_args_list,
                             'The save password checkbox should be disabled then enabled')
            self.assertEqual(expected_login_btn_calls, mocked_login_button.setEnabled.call_args_list,
                             'The login button should be disabled then enabled')
            self.assertEqual(expected_login_spacer_calls, mocked_login_spacer.setVisible.call_args_list,
                             'Thee login spacer should be make invisible, then visible')
            self.assertEqual(expected_login_progress_visible_calls,
                             mocked_login_progress_bar.setVisible.call_args_list,
                             'Thee login progress bar should be make visible, then invisible')
            self.assertEqual(expected_login_progress_value_calls, mocked_login_progress_bar.setValue.call_args_list,
                             'Thee login progress bar should have the right values set')
            self.assertEqual(2, mocked_process_events.call_count,
                             'The process_events() method should be called twice')
            mocked_critical.assert_called_with(ssform, 'Error Logging In', 'There was a problem logging in, '
                                                                           'perhaps your username or password is '
                                                                           'incorrect?')

    @patch('openlp.plugins.songs.forms.songselectform.QtGui.QMessageBox.question')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def on_import_yes_clicked_test(self, mocked_translate, mocked_question):
        """
        Test that when a song is imported and the user clicks the "yes" button, the UI goes back to the previous page
        """
        # GIVEN: A valid SongSelectForm with a mocked out QMessageBox.question() method
        mocked_translate.side_effect = lambda *args: args[1]
        mocked_question.return_value = QtGui.QMessageBox.Yes
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        mocked_song_select_importer = MagicMock()
        ssform.song_select_importer = mocked_song_select_importer
        ssform.song = None

        # WHEN: The import button is clicked, and the user clicks Yes
        with patch.object(ssform, 'on_back_button_clicked') as mocked_on_back_button_clicked:
            ssform.on_import_button_clicked()

        # THEN: The on_back_button_clicked() method should have been called
        mocked_song_select_importer.save_song.assert_called_with(None)
        mocked_question.assert_called_with(ssform, 'Song Imported',
                                           'Your song has been imported, would you like to import more songs?',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        mocked_on_back_button_clicked.assert_called_with()
        self.assertIsNone(ssform.song)

    @patch('openlp.plugins.songs.forms.songselectform.QtGui.QMessageBox.question')
    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def on_import_no_clicked_test(self, mocked_translate, mocked_question):
        """
        Test that when a song is imported and the user clicks the "no" button, the UI exits
        """
        # GIVEN: A valid SongSelectForm with a mocked out QMessageBox.question() method
        mocked_translate.side_effect = lambda *args: args[1]
        mocked_question.return_value = QtGui.QMessageBox.No
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        mocked_song_select_importer = MagicMock()
        ssform.song_select_importer = mocked_song_select_importer
        ssform.song = None

        # WHEN: The import button is clicked, and the user clicks Yes
        with patch.object(ssform, 'done') as mocked_done:
            ssform.on_import_button_clicked()

        # THEN: The on_back_button_clicked() method should have been called
        mocked_song_select_importer.save_song.assert_called_with(None)
        mocked_question.assert_called_with(ssform, 'Song Imported',
                                           'Your song has been imported, would you like to import more songs?',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        mocked_done.assert_called_with(QtGui.QDialog.Accepted)
        self.assertIsNone(ssform.song)

    def on_back_button_clicked_test(self):
        """
        Test that when the back button is clicked, the stacked widget is set back one page
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: The back button is clicked
        with patch.object(ssform, 'stacked_widget') as mocked_stacked_widget, \
                patch.object(ssform, 'search_combobox') as mocked_search_combobox:
            ssform.on_back_button_clicked()

        # THEN: The stacked widget should be set back one page
        mocked_stacked_widget.setCurrentIndex.assert_called_with(1)
        mocked_search_combobox.setFocus.assert_called_with()

    @patch('openlp.plugins.songs.forms.songselectform.QtGui.QMessageBox.information')
    def on_search_show_info_test(self, mocked_information):
        """
        Test that when the search_show_info signal is emitted, the on_search_show_info() method shows a dialog
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_title = 'Test Title'
        expected_text = 'This is a test'

        # WHEN: on_search_show_info is called
        ssform.on_search_show_info(expected_title, expected_text)

        # THEN: An information dialog should be shown
        mocked_information.assert_called_with(ssform, expected_title, expected_text)

    def update_login_progress_test(self):
        """
        Test the _update_login_progress() method
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: _update_login_progress() is called
        with patch.object(ssform, 'login_progress_bar') as mocked_login_progress_bar:
            mocked_login_progress_bar.value.return_value = 3
            ssform._update_login_progress()

        # THEN: The login progress bar should be updated
        mocked_login_progress_bar.setValue.assert_called_with(4)

    def update_song_progress_test(self):
        """
        Test the _update_song_progress() method
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: _update_song_progress() is called
        with patch.object(ssform, 'song_progress_bar') as mocked_song_progress_bar:
            mocked_song_progress_bar.value.return_value = 2
            ssform._update_song_progress()

        # THEN: The song progress bar should be updated
        mocked_song_progress_bar.setValue.assert_called_with(3)

    def on_search_results_widget_double_clicked_test(self):
        """
        Test that a song is retrieved when a song in the results list is double-clicked
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_song = {'title': 'Amazing Grace'}

        # WHEN: A song result is double-clicked
        with patch.object(ssform, '_view_song') as mocked_view_song:
            ssform.on_search_results_widget_double_clicked(expected_song)

        # THEN: The song is fetched and shown to the user
        mocked_view_song.assert_called_with(expected_song)

    def on_view_button_clicked_test(self):
        """
        Test that a song is retrieved when the view button is clicked
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())
        expected_song = {'title': 'Amazing Grace'}

        # WHEN: A song result is double-clicked
        with patch.object(ssform, '_view_song') as mocked_view_song, \
                patch.object(ssform, 'search_results_widget') as mocked_search_results_widget:
            mocked_search_results_widget.currentItem.return_value = expected_song
            ssform.on_view_button_clicked()

        # THEN: The song is fetched and shown to the user
        mocked_view_song.assert_called_with(expected_song)

    def on_search_results_widget_selection_changed_test(self):
        """
        Test that the view button is updated when the search results list is changed
        """
        # GIVEN: A SongSelect form
        ssform = SongSelectForm(None, MagicMock(), MagicMock())

        # WHEN: There is at least 1 item selected
        with patch.object(ssform, 'search_results_widget') as mocked_search_results_widget, \
                patch.object(ssform, 'view_button') as mocked_view_button:
            mocked_search_results_widget.selectedItems.return_value = [1]
            ssform.on_search_results_widget_selection_changed()

        # THEN: The view button should be enabled
        mocked_view_button.setEnabled.assert_called_with(True)


class TestSongSelectFileImport(TestCase, TestMixin):
    """
    Test SongSelect file import
    """
    def setUp(self):
        """
        Initial setups
        """
        Registry.create()
        test_song_name = 'TestSong'
        self.file_name = os.path.join('tests', 'resources', 'songselect', test_song_name)
        self.title = 'Test Song'
        self.ccli_number = '0000000'
        self.authors = ['Author One', 'Author Two']
        self.topics = ['Adoration', 'Praise']

    def songselect_import_bin_file_test(self):
        """
        Verify import SongSelect BIN file parses file properly
        """
        # GIVEN: Text file to import and mocks
        copyright_bin = '2011 OpenLP Programmer One (Admin. by OpenLP One) | ' \
                        'Openlp Programmer Two (Admin. by OpenLP Two)'
        verses_bin = [
            ['v1', 'Line One Verse One\nLine Two Verse One\nLine Three Verse One\nLine Four Verse One', None],
            ['v2', 'Line One Verse Two\nLine Two Verse Two\nLine Three Verse Two\nLine Four Verse Two', None]
        ]
        song_import = CCLIFileImport(manager=None, filename=['{}.bin'.format(self.file_name)])

        with patch.object(song_import, 'import_wizard'), patch.object(song_import, 'finish'):
            # WHEN: We call the song importer
            song_import.do_import()
            # THEN: Song values should be equal to test values in setUp
            self.assertEquals(song_import.title, self.title, 'Song title should match')
            self.assertEquals(song_import.ccli_number, self.ccli_number, 'CCLI Song Number should match')
            self.assertEquals(song_import.authors, self.authors, 'Author(s) should match')
            self.assertEquals(song_import.copyright, copyright_bin, 'Copyright should match')
            self.assertEquals(song_import.topics, self.topics, 'Theme(s) should match')
            self.assertEquals(song_import.verses, verses_bin, 'Verses should match with test verses')

    def songselect_import_text_file_test(self):
        """
        Verify import SongSelect TEXT file parses file properly
        """
        # GIVEN: Text file to import and mocks
        copyright_txt = '© 2011 OpenLP Programmer One (Admin. by OpenLP One)'
        verses_txt = [
            ['v1', 'Line One Verse One\r\nLine Two Verse One\r\nLine Three Verse One\r\nLine Four Verse One', None],
            ['v2', 'Line One Verse Two\r\nLine Two Verse Two\r\nLine Three Verse Two\r\nLine Four Verse Two', None]
        ]
        song_import = CCLIFileImport(manager=None, filename=['{}.txt'.format(self.file_name)])

        with patch.object(song_import, 'import_wizard'), patch.object(song_import, 'finish'):
            # WHEN: We call the song importer
            song_import.do_import()

            # THEN: Song values should be equal to test values in setUp
            self.assertEquals(song_import.title, self.title, 'Song title should match')
            self.assertEquals(song_import.ccli_number, self.ccli_number, 'CCLI Song Number should match')
            self.assertEquals(song_import.authors, self.authors, 'Author(s) should match')
            self.assertEquals(song_import.copyright, copyright_txt, 'Copyright should match')
            self.assertEquals(song_import.verses, verses_txt, 'Verses should match with test verses')


class TestSearchWorker(TestCase, TestMixin):
    """
    Test the SearchWorker class
    """
    def constructor_test(self):
        """
        Test the SearchWorker constructor
        """
        # GIVEN: An importer mock object and some search text
        importer = MagicMock()
        search_text = 'Jesus'

        # WHEN: The search worker is created
        worker = SearchWorker(importer, search_text)

        # THEN: The correct values should be set
        self.assertIs(importer, worker.importer, 'The importer should be the right object')
        self.assertEqual(search_text, worker.search_text, 'The search text should be correct')

    def start_test(self):
        """
        Test the start() method of the SearchWorker class
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        importer = MagicMock()
        importer.search.return_value = ['song1', 'song2']
        search_text = 'Jesus'
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'finished') as mocked_finished, patch.object(worker, 'quit') as mocked_quit:
            worker.start()

        # THEN: The "finished" and "quit" signals should be emitted
        importer.search.assert_called_with(search_text, 1000, worker._found_song_callback)
        mocked_finished.emit.assert_called_with()
        mocked_quit.emit.assert_called_with()

    @patch('openlp.plugins.songs.forms.songselectform.translate')
    def start_over_1000_songs_test(self, mocked_translate):
        """
        Test the start() method of the SearchWorker class when it finds over 1000 songs
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        mocked_translate.side_effect = lambda x, y: y
        importer = MagicMock()
        importer.search.return_value = ['song%s' % num for num in range(1050)]
        search_text = 'Jesus'
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'finished') as mocked_finished, patch.object(worker, 'quit') as mocked_quit, \
                patch.object(worker, 'show_info') as mocked_show_info:
            worker.start()

        # THEN: The "finished" and "quit" signals should be emitted
        importer.search.assert_called_with(search_text, 1000, worker._found_song_callback)
        mocked_show_info.emit.assert_called_with('More than 1000 results', 'Your search has returned more than 1000 '
                                                                           'results, it has been stopped. Please '
                                                                           'refine your search to fetch better '
                                                                           'results.')
        mocked_finished.emit.assert_called_with()
        mocked_quit.emit.assert_called_with()

    def found_song_callback_test(self):
        """
        Test that when the _found_song_callback() function is called, the "found_song" signal is emitted
        """
        # GIVEN: An importer mock object, some search text and an initialised SearchWorker
        importer = MagicMock()
        search_text = 'Jesus'
        song = {'title': 'Amazing Grace'}
        worker = SearchWorker(importer, search_text)

        # WHEN: The start() method is called
        with patch.object(worker, 'found_song') as mocked_found_song:
            worker._found_song_callback(song)

        # THEN: The "found_song" signal should have been emitted
        mocked_found_song.emit.assert_called_with(song)
