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
Package to test the openlp.core.ui.media package.
"""
from unittest import TestCase

from openlp.core.ui.media.mediacontroller import MediaController
from openlp.core.ui.media.mediaplayer import MediaPlayer
from openlp.core.common import Registry

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMediaController(TestCase, TestMixin):

    def setUp(self):
        Registry.create()
        Registry().register('service_manager', MagicMock())

    def generate_extensions_lists_test(self):
        """
        Test that the extensions are create correctly
        """
        # GIVEN: A MediaController and an active player with audio and video extensions
        media_controller = MediaController()
        media_player = MediaPlayer(None)
        media_player.is_active = True
        media_player.audio_extensions_list = ['*.mp3', '*.wav', '*.wma', '*.ogg']
        media_player.video_extensions_list = ['*.mp4', '*.mov', '*.avi', '*.ogm']
        media_controller.register_players(media_player)

        # WHEN: calling _generate_extensions_lists
        media_controller._generate_extensions_lists()

        # THEN: extensions list should have been copied from the player to the mediacontroller
        self.assertListEqual(media_player.video_extensions_list, media_controller.video_extensions_list,
                             'Video extensions should be the same')
        self.assertListEqual(media_player.audio_extensions_list, media_controller.audio_extensions_list,
                             'Audio extensions should be the same')

    def resize_test(self):
        """
        Test that the resize method is called correctly
        """
        # GIVEN: A media controller, a player and a display
        media_controller = MediaController()
        mocked_player = MagicMock()
        mocked_display = MagicMock()

        # WHEN: resize() is called
        media_controller.resize(mocked_display, mocked_player)

        # THEN: The player's resize method should be called correctly
        mocked_player.resize.assert_called_with(mocked_display)

    def check_file_type_no_players_test(self):
        """
        Test that we don't try to play media when no players available
        """
        # GIVEN: A mocked UiStrings, get_media_players, controller, display and service_item
        with patch('openlp.core.ui.media.mediacontroller.get_media_players') as mocked_get_media_players,\
                patch('openlp.core.ui.media.mediacontroller.UiStrings') as mocked_uistrings:
            mocked_get_media_players.return_value = ([], '')
            mocked_ret_uistrings = MagicMock()
            mocked_ret_uistrings.Automatic = 1
            mocked_uistrings.return_value = mocked_ret_uistrings
            media_controller = MediaController()
            mocked_controller = MagicMock()
            mocked_display = MagicMock()
            mocked_service_item = MagicMock()
            mocked_service_item.processor = 1

            # WHEN: calling _check_file_type when no players exists
            ret = media_controller._check_file_type(mocked_controller, mocked_display, mocked_service_item)

            # THEN: it should return False
            self.assertFalse(ret, '_check_file_type should return False when no mediaplayers are available.')

    @patch('openlp.core.ui.media.mediacontroller.get_media_players')
    @patch('openlp.core.ui.media.mediacontroller.UiStrings')
    def check_file_type_no_processor_test(self, mocked_uistrings, mocked_get_media_players):
        """
        Test that we don't try to play media when the processor for the service item is None
        """
        # GIVEN: A mocked UiStrings, get_media_players, controller, display and service_item
        mocked_get_media_players.return_value = ([], '')
        mocked_ret_uistrings = MagicMock()
        mocked_ret_uistrings.Automatic = 1
        mocked_uistrings.return_value = mocked_ret_uistrings
        media_controller = MediaController()
        mocked_controller = MagicMock()
        mocked_display = MagicMock()
        mocked_service_item = MagicMock()
        mocked_service_item.processor = None

        # WHEN: calling _check_file_type when the processor for the service item is None
        ret = media_controller._check_file_type(mocked_controller, mocked_display, mocked_service_item)

        # THEN: it should return False
        self.assertFalse(ret, '_check_file_type should return False when the processor for service_item is None.')

    def media_play_msg_test(self):
        """
        Test that the media controller responds to the request to play a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_play') as mocked_media_play:
            media_controller.media_play_msg(message, False)

        # THEN: The underlying method is called
        mocked_media_play.assert_called_with(1, False)

    def media_pause_msg_test(self):
        """
        Test that the media controller responds to the request to pause a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_pause') as mocked_media_pause:
            media_controller.media_pause_msg(message)

        # THEN: The underlying method is called
        mocked_media_pause.assert_called_with(1)

    def media_stop_msg_test(self):
        """
        Test that the media controller responds to the request to stop a loaded video
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, 2)

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_stop') as mocked_media_stop:
            media_controller.media_stop_msg(message)

        # THEN: The underlying method is called
        mocked_media_stop.assert_called_with(1)

    def media_volume_msg_test(self):
        """
        Test that the media controller responds to the request to change the volume
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, [50])

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_volume') as mocked_media_volume:
            media_controller.media_volume_msg(message)

        # THEN: The underlying method is called
        mocked_media_volume.assert_called_with(1, 50)

    def media_seek_msg_test(self):
        """
        Test that the media controller responds to the request to seek to a particular position
        """
        # GIVEN: A media controller and a message with two elements
        media_controller = MediaController()
        message = (1, [800])

        # WHEN: media_play_msg() is called
        with patch.object(media_controller, u'media_seek') as mocked_media_seek:
            media_controller.media_seek_msg(message)

        # THEN: The underlying method is called
        mocked_media_seek.assert_called_with(1, 800)
