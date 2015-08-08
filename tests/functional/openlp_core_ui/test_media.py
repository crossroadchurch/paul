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
Package to test the openlp.core.ui package.
"""
from PyQt4 import QtCore
from unittest import TestCase

from openlp.core.ui.media import get_media_players, parse_optical_path

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMedia(TestCase, TestMixin):

    def test_get_media_players_no_config(self):
        """
        Test that when there's no config, get_media_players() returns an empty list of players (not a string)
        """
        def value_results(key):
            if key == 'media/players':
                return ''
            else:
                return False

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = get_media_players()

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            self.assertEqual([], used_players, 'Used players should be an empty list')
            self.assertEqual('', overridden_player, 'Overridden player should be an empty string')

    def test_get_media_players_no_players(self):
        """
        Test that when there's no players but overridden player is set, get_media_players() returns 'auto'
        """
        def value_results(key):
            if key == 'media/override player':
                return QtCore.Qt.Checked
            else:
                return ''

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = get_media_players()

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            self.assertEqual([], used_players, 'Used players should be an empty list')
            self.assertEqual('auto', overridden_player, 'Overridden player should be "auto"')

    def test_get_media_players_with_valid_list(self):
        """
        Test that when get_media_players() is called the string list is interpreted correctly
        """
        def value_results(key):
            if key == 'media/players':
                return '[vlc,webkit,phonon]'
            else:
                return False

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = get_media_players()

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            self.assertEqual(['vlc', 'webkit', 'phonon'], used_players, 'Used players should be correct')
            self.assertEqual('', overridden_player, 'Overridden player should be an empty string')

    def test_get_media_players_with_overridden_player(self):
        """
        Test that when get_media_players() is called the overridden player is correctly set
        """
        def value_results(key):
            if key == 'media/players':
                return '[vlc,webkit,phonon]'
            else:
                return QtCore.Qt.Checked

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = get_media_players()

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            self.assertEqual(['vlc', 'webkit', 'phonon'], used_players, 'Used players should be correct')
            self.assertEqual('vlc,webkit,phonon', overridden_player, 'Overridden player should be a string of players')

    def test_parse_optical_path_linux(self):
        """
        Test that test_parse_optical_path() parses a optical path with linux device path correctly
        """

        # GIVEN: An optical formatted path
        org_title_track = 1
        org_audio_track = 2
        org_subtitle_track = -1
        org_start = 1234
        org_end = 4321
        org_name = 'test name'
        org_device_path = '/dev/dvd'
        path = 'optical:%d:%d:%d:%d:%d:%s:%s' % (org_title_track, org_audio_track, org_subtitle_track,
                                                 org_start, org_end, org_name, org_device_path)

        # WHEN: parsing the path
        (device_path, title_track, audio_track, subtitle_track, start, end, name) = parse_optical_path(path)

        # THEN: The return values should match the original values
        self.assertEqual(org_title_track, title_track, 'Returned title_track should match the original')
        self.assertEqual(org_audio_track, audio_track, 'Returned audio_track should match the original')
        self.assertEqual(org_subtitle_track, subtitle_track, 'Returned subtitle_track should match the original')
        self.assertEqual(org_start, start, 'Returned start should match the original')
        self.assertEqual(org_end, end, 'Returned end should match the original')
        self.assertEqual(org_name, name, 'Returned end should match the original')
        self.assertEqual(org_device_path, device_path, 'Returned device_path should match the original')

    def test_parse_optical_path_win(self):
        """
        Test that test_parse_optical_path() parses a optical path with windows device path correctly
        """

        # GIVEN: An optical formatted path
        org_title_track = 1
        org_audio_track = 2
        org_subtitle_track = -1
        org_start = 1234
        org_end = 4321
        org_name = 'test name'
        org_device_path = 'D:'
        path = 'optical:%d:%d:%d:%d:%d:%s:%s' % (org_title_track, org_audio_track, org_subtitle_track,
                                                 org_start, org_end, org_name, org_device_path)

        # WHEN: parsing the path
        (device_path, title_track, audio_track, subtitle_track, start, end, name) = parse_optical_path(path)

        # THEN: The return values should match the original values
        self.assertEqual(org_title_track, title_track, 'Returned title_track should match the original')
        self.assertEqual(org_audio_track, audio_track, 'Returned audio_track should match the original')
        self.assertEqual(org_subtitle_track, subtitle_track, 'Returned subtitle_track should match the original')
        self.assertEqual(org_start, start, 'Returned start should match the original')
        self.assertEqual(org_end, end, 'Returned end should match the original')
        self.assertEqual(org_name, name, 'Returned end should match the original')
        self.assertEqual(org_device_path, device_path, 'Returned device_path should match the original')
