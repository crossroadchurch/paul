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
Package to test the openlp.core.ui.media.vlcplayer package.
"""
import os
import sys
from datetime import datetime, timedelta
from unittest import TestCase

from openlp.core.common import Registry
from openlp.core.ui.media import MediaState, MediaType
from openlp.core.ui.media.vlcplayer import AUDIO_EXT, VIDEO_EXT, VlcPlayer, get_vlc

from tests.functional import MagicMock, patch, call
from tests.helpers import MockDateTime
from tests.helpers.testmixin import TestMixin


class TestVLCPlayer(TestCase, TestMixin):
    """
    Test the functions in the :mod:`vlcplayer` module.
    """
    def setUp(self):
        """
        Common setup for all the tests
        """
        if 'VLC_PLUGIN_PATH' in os.environ:
            del os.environ['VLC_PLUGIN_PATH']
        if 'openlp.core.ui.media.vendor.vlc' in sys.modules:
            del sys.modules['openlp.core.ui.media.vendor.vlc']
        MockDateTime.revert()

    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    def fix_vlc_22_plugin_path_test(self, mocked_is_macosx):
        """
        Test that on OS X we set the VLC plugin path to fix a bug in the VLC module
        """
        # GIVEN: We're on OS X and we don't have the VLC plugin path set
        mocked_is_macosx.return_value = True

        # WHEN: An checking if the player is available
        get_vlc()

        # THEN: The extra environment variable should be there
        self.assertIn('VLC_PLUGIN_PATH', os.environ,
                      'The plugin path should be in the environment variables')
        self.assertEqual('/Applications/VLC.app/Contents/MacOS/plugins', os.environ['VLC_PLUGIN_PATH'])

    @patch.dict(os.environ)
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    def not_osx_fix_vlc_22_plugin_path_test(self, mocked_is_macosx):
        """
        Test that on Linux or some other non-OS X we do not set the VLC plugin path
        """
        # GIVEN: We're not on OS X and we don't have the VLC plugin path set
        mocked_is_macosx.return_value = False
        if 'VLC_PLUGIN_PATH' in os.environ:
            del os.environ['VLC_PLUGIN_PATH']
        if 'openlp.core.ui.media.vendor.vlc' in sys.modules:
            del sys.modules['openlp.core.ui.media.vendor.vlc']

        # WHEN: An checking if the player is available
        get_vlc()

        # THEN: The extra environment variable should NOT be there
        self.assertNotIn('VLC_PLUGIN_PATH', os.environ,
                         'The plugin path should NOT be in the environment variables')

    def init_test(self):
        """
        Test that the VLC player class initialises correctly
        """
        # GIVEN: A mocked out list of extensions
        # TODO: figure out how to mock out the lists of extensions

        # WHEN: The VlcPlayer class is instantiated
        vlc_player = VlcPlayer(None)

        # THEN: The correct variables are set
        self.assertEqual('VLC', vlc_player.original_name)
        self.assertEqual('&VLC', vlc_player.display_name)
        self.assertIsNone(vlc_player.parent)
        self.assertTrue(vlc_player.can_folder)
        self.assertListEqual(AUDIO_EXT, vlc_player.audio_extensions_list)
        self.assertListEqual(VIDEO_EXT, vlc_player.video_extensions_list)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.QtGui')
    @patch('openlp.core.ui.media.vlcplayer.Settings')
    def setup_test(self, MockedSettings, MockedQtGui, mocked_get_vlc, mocked_is_macosx, mocked_is_win):
        """
        Test the setup method
        """
        # GIVEN: A bunch of mocked out stuff and a VlcPlayer object
        mocked_is_macosx.return_value = False
        mocked_is_win.return_value = False
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = True
        MockedSettings.return_value = mocked_settings
        mocked_qframe = MagicMock()
        mocked_qframe.winId.return_value = 2
        MockedQtGui.QFrame.NoFrame = 1
        MockedQtGui.QFrame.return_value = mocked_qframe
        mocked_media_player_new = MagicMock()
        mocked_instance = MagicMock()
        mocked_instance.media_player_new.return_value = mocked_media_player_new
        mocked_vlc = MagicMock()
        mocked_vlc.Instance.return_value = mocked_instance
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.has_audio = False
        mocked_display.controller.is_live = True
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: setup() is run
        vlc_player.setup(mocked_display)

        # THEN: The VLC widget should be set up correctly
        self.assertEqual(mocked_display.vlc_widget, mocked_qframe)
        mocked_qframe.setFrameStyle.assert_called_with(1)
        mocked_settings.value.assert_called_with('advanced/hide mouse')
        mocked_vlc.Instance.assert_called_with('--no-video-title-show --no-audio --no-video-title-show '
                                               '--mouse-hide-timeout=0')
        self.assertEqual(mocked_display.vlc_instance, mocked_instance)
        mocked_instance.media_player_new.assert_called_with()
        self.assertEqual(mocked_display.vlc_media_player, mocked_media_player_new)
        mocked_display.size.assert_called_with()
        mocked_qframe.resize.assert_called_with((10, 10))
        mocked_qframe.raise_.assert_called_with()
        mocked_qframe.hide.assert_called_with()
        mocked_media_player_new.set_xwindow.assert_called_with(2)
        self.assertTrue(vlc_player.has_own_widget)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.QtGui')
    @patch('openlp.core.ui.media.vlcplayer.Settings')
    def setup_has_audio_test(self, MockedSettings, MockedQtGui, mocked_get_vlc, mocked_is_macosx, mocked_is_win):
        """
        Test the setup method when has_audio is True
        """
        # GIVEN: A bunch of mocked out stuff and a VlcPlayer object
        mocked_is_macosx.return_value = False
        mocked_is_win.return_value = False
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = True
        MockedSettings.return_value = mocked_settings
        mocked_qframe = MagicMock()
        mocked_qframe.winId.return_value = 2
        MockedQtGui.QFrame.NoFrame = 1
        MockedQtGui.QFrame.return_value = mocked_qframe
        mocked_media_player_new = MagicMock()
        mocked_instance = MagicMock()
        mocked_instance.media_player_new.return_value = mocked_media_player_new
        mocked_vlc = MagicMock()
        mocked_vlc.Instance.return_value = mocked_instance
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.has_audio = True
        mocked_display.controller.is_live = True
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: setup() is run
        vlc_player.setup(mocked_display)

        # THEN: The VLC instance should be created with the correct options
        mocked_vlc.Instance.assert_called_with('--no-video-title-show --mouse-hide-timeout=0')

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.QtGui')
    @patch('openlp.core.ui.media.vlcplayer.Settings')
    def setup_visible_mouse_test(self, MockedSettings, MockedQtGui, mocked_get_vlc, mocked_is_macosx, mocked_is_win):
        """
        Test the setup method when Settings().value("hide mouse") is False
        """
        # GIVEN: A bunch of mocked out stuff and a VlcPlayer object
        mocked_is_macosx.return_value = False
        mocked_is_win.return_value = False
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        mocked_qframe = MagicMock()
        mocked_qframe.winId.return_value = 2
        MockedQtGui.QFrame.NoFrame = 1
        MockedQtGui.QFrame.return_value = mocked_qframe
        mocked_media_player_new = MagicMock()
        mocked_instance = MagicMock()
        mocked_instance.media_player_new.return_value = mocked_media_player_new
        mocked_vlc = MagicMock()
        mocked_vlc.Instance.return_value = mocked_instance
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.has_audio = False
        mocked_display.controller.is_live = True
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: setup() is run
        vlc_player.setup(mocked_display)

        # THEN: The VLC instance should be created with the correct options
        mocked_vlc.Instance.assert_called_with('--no-video-title-show --no-audio --no-video-title-show')

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.QtGui')
    @patch('openlp.core.ui.media.vlcplayer.Settings')
    def setup_windows_test(self, MockedSettings, MockedQtGui, mocked_get_vlc, mocked_is_macosx, mocked_is_win):
        """
        Test the setup method when running on Windows
        """
        # GIVEN: A bunch of mocked out stuff and a VlcPlayer object
        mocked_is_macosx.return_value = False
        mocked_is_win.return_value = True
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        mocked_qframe = MagicMock()
        mocked_qframe.winId.return_value = 2
        MockedQtGui.QFrame.NoFrame = 1
        MockedQtGui.QFrame.return_value = mocked_qframe
        mocked_media_player_new = MagicMock()
        mocked_instance = MagicMock()
        mocked_instance.media_player_new.return_value = mocked_media_player_new
        mocked_vlc = MagicMock()
        mocked_vlc.Instance.return_value = mocked_instance
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.has_audio = False
        mocked_display.controller.is_live = True
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: setup() is run
        vlc_player.setup(mocked_display)

        # THEN: set_hwnd should be called
        mocked_media_player_new.set_hwnd.assert_called_with(2)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.is_macosx')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.QtGui')
    @patch('openlp.core.ui.media.vlcplayer.Settings')
    def setup_osx_test(self, MockedSettings, MockedQtGui, mocked_get_vlc, mocked_is_macosx, mocked_is_win):
        """
        Test the setup method when running on OS X
        """
        # GIVEN: A bunch of mocked out stuff and a VlcPlayer object
        mocked_is_macosx.return_value = True
        mocked_is_win.return_value = False
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        mocked_qframe = MagicMock()
        mocked_qframe.winId.return_value = 2
        MockedQtGui.QFrame.NoFrame = 1
        MockedQtGui.QFrame.return_value = mocked_qframe
        mocked_media_player_new = MagicMock()
        mocked_instance = MagicMock()
        mocked_instance.media_player_new.return_value = mocked_media_player_new
        mocked_vlc = MagicMock()
        mocked_vlc.Instance.return_value = mocked_instance
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.has_audio = False
        mocked_display.controller.is_live = True
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: setup() is run
        vlc_player.setup(mocked_display)

        # THEN: set_nsobject should be called
        mocked_media_player_new.set_nsobject.assert_called_with(2)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def check_available_test(self, mocked_get_vlc):
        """
        Check that when the "vlc" module is available, then VLC is set as available
        """
        # GIVEN: A mocked out get_vlc() method and a VlcPlayer instance
        mocked_get_vlc.return_value = MagicMock()
        vlc_player = VlcPlayer(None)

        # WHEN: vlc
        is_available = vlc_player.check_available()

        # THEN: VLC should be available
        self.assertTrue(is_available)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def check_not_available_test(self, mocked_get_vlc):
        """
        Check that when the "vlc" module is not available, then VLC is set as unavailable
        """
        # GIVEN: A mocked out get_vlc() method and a VlcPlayer instance
        mocked_get_vlc.return_value = None
        vlc_player = VlcPlayer(None)

        # WHEN: vlc
        is_available = vlc_player.check_available()

        # THEN: VLC should NOT be available
        self.assertFalse(is_available)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.os.path.normcase')
    def load_test(self, mocked_normcase, mocked_get_vlc):
        """
        Test loading a video into VLC
        """
        # GIVEN: A mocked out get_vlc() method
        media_path = '/path/to/media.mp4'
        mocked_normcase.side_effect = lambda x: x
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.volume = 100
        mocked_controller.media_info.media_type = MediaType.Video
        mocked_controller.media_info.file_info.absoluteFilePath.return_value = media_path
        mocked_vlc_media = MagicMock()
        mocked_media = MagicMock()
        mocked_media.get_duration.return_value = 10000
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_instance.media_new_path.return_value = mocked_vlc_media
        mocked_display.vlc_media_player.get_media.return_value = mocked_media
        vlc_player = VlcPlayer(None)

        # WHEN: A video is loaded into VLC
        with patch.object(vlc_player, 'volume') as mocked_volume:
            result = vlc_player.load(mocked_display)

        # THEN: The video should be loaded
        mocked_normcase.assert_called_with(media_path)
        mocked_display.vlc_instance.media_new_path.assert_called_with(media_path)
        self.assertEqual(mocked_vlc_media, mocked_display.vlc_media)
        mocked_display.vlc_media_player.set_media.assert_called_with(mocked_vlc_media)
        mocked_vlc_media.parse.assert_called_with()
        mocked_volume.assert_called_with(mocked_display, 100)
        self.assertEqual(10, mocked_controller.media_info.length)
        self.assertTrue(result)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.os.path.normcase')
    def load_audio_cd_test(self, mocked_normcase, mocked_get_vlc, mocked_is_win):
        """
        Test loading an audio CD into VLC
        """
        # GIVEN: A mocked out get_vlc() method
        mocked_is_win.return_value = False
        media_path = '/dev/sr0'
        mocked_normcase.side_effect = lambda x: x
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.volume = 100
        mocked_controller.media_info.media_type = MediaType.CD
        mocked_controller.media_info.file_info.absoluteFilePath.return_value = media_path
        mocked_controller.media_info.title_track = 1
        mocked_vlc_media = MagicMock()
        mocked_media = MagicMock()
        mocked_media.get_duration.return_value = 10000
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_instance.media_new_location.return_value = mocked_vlc_media
        mocked_display.vlc_media_player.get_media.return_value = mocked_media
        mocked_subitems = MagicMock()
        mocked_subitems.count.return_value = 1
        mocked_subitems.item_at_index.return_value = mocked_vlc_media
        mocked_vlc_media.subitems.return_value = mocked_subitems
        vlc_player = VlcPlayer(None)

        # WHEN: An audio CD is loaded into VLC
        with patch.object(vlc_player, 'volume') as mocked_volume, \
                patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait:
            result = vlc_player.load(mocked_display)

        # THEN: The video should be loaded
        mocked_normcase.assert_called_with(media_path)
        mocked_display.vlc_instance.media_new_location.assert_called_with('cdda://' + media_path)
        self.assertEqual(mocked_vlc_media, mocked_display.vlc_media)
        mocked_display.vlc_media_player.set_media.assert_called_with(mocked_vlc_media)
        mocked_vlc_media.parse.assert_called_with()
        mocked_volume.assert_called_with(mocked_display, 100)
        self.assertEqual(10, mocked_controller.media_info.length)
        self.assertTrue(result)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.os.path.normcase')
    def load_audio_cd_on_windows_test(self, mocked_normcase, mocked_get_vlc, mocked_is_win):
        """
        Test loading an audio CD into VLC on Windows
        """
        # GIVEN: A mocked out get_vlc() method
        mocked_is_win.return_value = True
        media_path = '/dev/sr0'
        mocked_normcase.side_effect = lambda x: x
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.volume = 100
        mocked_controller.media_info.media_type = MediaType.CD
        mocked_controller.media_info.file_info.absoluteFilePath.return_value = media_path
        mocked_controller.media_info.title_track = 1
        mocked_vlc_media = MagicMock()
        mocked_media = MagicMock()
        mocked_media.get_duration.return_value = 10000
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_instance.media_new_location.return_value = mocked_vlc_media
        mocked_display.vlc_media_player.get_media.return_value = mocked_media
        mocked_subitems = MagicMock()
        mocked_subitems.count.return_value = 1
        mocked_subitems.item_at_index.return_value = mocked_vlc_media
        mocked_vlc_media.subitems.return_value = mocked_subitems
        vlc_player = VlcPlayer(None)

        # WHEN: An audio CD is loaded into VLC
        with patch.object(vlc_player, 'volume') as mocked_volume, \
                patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait:
            result = vlc_player.load(mocked_display)

        # THEN: The video should be loaded
        mocked_normcase.assert_called_with(media_path)
        mocked_display.vlc_instance.media_new_location.assert_called_with('cdda:///' + media_path)
        self.assertEqual(mocked_vlc_media, mocked_display.vlc_media)
        mocked_display.vlc_media_player.set_media.assert_called_with(mocked_vlc_media)
        mocked_vlc_media.parse.assert_called_with()
        mocked_volume.assert_called_with(mocked_display, 100)
        self.assertEqual(10, mocked_controller.media_info.length)
        self.assertTrue(result)

    @patch('openlp.core.ui.media.vlcplayer.is_win')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.os.path.normcase')
    def load_audio_cd_no_tracks_test(self, mocked_normcase, mocked_get_vlc, mocked_is_win):
        """
        Test loading an audio CD that has no tracks into VLC
        """
        # GIVEN: A mocked out get_vlc() method
        mocked_is_win.return_value = False
        media_path = '/dev/sr0'
        mocked_normcase.side_effect = lambda x: x
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.volume = 100
        mocked_controller.media_info.media_type = MediaType.CD
        mocked_controller.media_info.file_info.absoluteFilePath.return_value = media_path
        mocked_controller.media_info.title_track = 1
        mocked_vlc_media = MagicMock()
        mocked_media = MagicMock()
        mocked_media.get_duration.return_value = 10000
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_instance.media_new_location.return_value = mocked_vlc_media
        mocked_display.vlc_media_player.get_media.return_value = mocked_media
        mocked_subitems = MagicMock()
        mocked_subitems.count.return_value = 0
        mocked_subitems.item_at_index.return_value = mocked_vlc_media
        mocked_vlc_media.subitems.return_value = mocked_subitems
        vlc_player = VlcPlayer(None)

        # WHEN: An audio CD is loaded into VLC
        with patch.object(vlc_player, 'volume') as mocked_volume, \
                patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait:
            result = vlc_player.load(mocked_display)

        # THEN: The video should be loaded
        mocked_normcase.assert_called_with(media_path)
        mocked_display.vlc_instance.media_new_location.assert_called_with('cdda://' + media_path)
        self.assertEqual(mocked_vlc_media, mocked_display.vlc_media)
        self.assertEqual(0, mocked_subitems.item_at_index.call_count)
        mocked_display.vlc_media_player.set_media.assert_called_with(mocked_vlc_media)
        self.assertEqual(0, mocked_vlc_media.parse.call_count)
        self.assertFalse(result)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.datetime', MockDateTime)
    def media_state_wait_test(self, mocked_get_vlc):
        """
        Check that waiting for a state change works
        """
        # GIVEN: A mocked out get_vlc method
        mocked_vlc = MagicMock()
        mocked_vlc.State.Error = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 2
        Registry.create()
        mocked_application = MagicMock()
        Registry().register('application', mocked_application)
        vlc_player = VlcPlayer(None)

        # WHEN: media_state_wait() is called
        result = vlc_player.media_state_wait(mocked_display, 2)

        # THEN: The results should be True
        self.assertTrue(result)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.datetime', MockDateTime)
    def media_state_wait_error_test(self, mocked_get_vlc):
        """
        Check that getting an error when waiting for a state change returns False
        """
        # GIVEN: A mocked out get_vlc method
        mocked_vlc = MagicMock()
        mocked_vlc.State.Error = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 1
        Registry.create()
        mocked_application = MagicMock()
        Registry().register('application', mocked_application)
        vlc_player = VlcPlayer(None)

        # WHEN: media_state_wait() is called
        result = vlc_player.media_state_wait(mocked_display, 2)

        # THEN: The results should be True
        self.assertFalse(result)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    @patch('openlp.core.ui.media.vlcplayer.datetime', MockDateTime)
    def media_state_wait_times_out_test(self, mocked_get_vlc):
        """
        Check that waiting for a state returns False when it times out after 60 seconds
        """
        # GIVEN: A mocked out get_vlc method
        timeout = MockDateTime.return_values[0] + timedelta(seconds=61)
        MockDateTime.return_values.append(timeout)
        mocked_vlc = MagicMock()
        mocked_vlc.State.Error = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 2
        Registry.create()
        mocked_application = MagicMock()
        Registry().register('application', mocked_application)
        vlc_player = VlcPlayer(None)

        # WHEN: media_state_wait() is called
        result = vlc_player.media_state_wait(mocked_display, 3)

        # THEN: The results should be True
        self.assertFalse(result)

    def resize_test(self):
        """
        Test resizing the player
        """
        # GIVEN: A display object and a VlcPlayer instance
        mocked_display = MagicMock()
        mocked_display.size.return_value = (10, 10)
        vlc_player = VlcPlayer(None)

        # WHEN: resize is called
        vlc_player.resize(mocked_display)

        # THEN: The right methods should have been called
        mocked_display.size.assert_called_with()
        mocked_display.vlc_widget.resize.assert_called_with((10, 10))

    @patch('openlp.core.ui.media.vlcplayer.threading')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def play_test(self, mocked_get_vlc, mocked_threading):
        """
        Test the play() method
        """
        # GIVEN: A bunch of mocked out things
        mocked_thread = MagicMock()
        mocked_threading.Thread.return_value = mocked_thread
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.start_time = 0
        mocked_controller.media_info.media_type = MediaType.Video
        mocked_controller.media_info.volume = 100
        mocked_media = MagicMock()
        mocked_media.get_duration.return_value = 50000
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_media_player.get_media.return_value = mocked_media
        vlc_player = VlcPlayer(None)
        vlc_player.state = MediaState.Paused

        # WHEN: play() is called
        with patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait, \
                patch.object(vlc_player, 'volume') as mocked_volume:
            mocked_media_state_wait.return_value = True
            result = vlc_player.play(mocked_display)

        # THEN: A bunch of things should happen to play the media
        mocked_thread.start.assert_called_with()
        self.assertEqual(50, mocked_controller.media_info.length)
        mocked_volume.assert_called_with(mocked_display, 100)
        mocked_controller.seek_slider.setMaximum.assert_called_with(50000)
        self.assertEqual(MediaState.Playing, vlc_player.state)
        mocked_display.vlc_widget.raise_.assert_called_with()
        self.assertTrue(result, 'The value returned from play() should be True')

    @patch('openlp.core.ui.media.vlcplayer.threading')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def play_media_wait_state_not_playing_test(self, mocked_get_vlc, mocked_threading):
        """
        Test the play() method when media_wait_state() returns False
        """
        # GIVEN: A bunch of mocked out things
        mocked_thread = MagicMock()
        mocked_threading.Thread.return_value = mocked_thread
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.start_time = 0
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        vlc_player = VlcPlayer(None)
        vlc_player.state = MediaState.Paused

        # WHEN: play() is called
        with patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait, \
                patch.object(vlc_player, 'volume') as mocked_volume:
            mocked_media_state_wait.return_value = False
            result = vlc_player.play(mocked_display)

        # THEN: A thread should be started, but the method should return False
        mocked_thread.start.assert_called_with()
        self.assertFalse(result)

    @patch('openlp.core.ui.media.vlcplayer.threading')
    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def play_dvd_test(self, mocked_get_vlc, mocked_threading):
        """
        Test the play() method with a DVD
        """
        # GIVEN: A bunch of mocked out things
        mocked_thread = MagicMock()
        mocked_threading.Thread.return_value = mocked_thread
        mocked_vlc = MagicMock()
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.start_time = 0
        mocked_controller.media_info.end_time = 50
        mocked_controller.media_info.media_type = MediaType.DVD
        mocked_controller.media_info.volume = 100
        mocked_controller.media_info.title_track = 1
        mocked_controller.media_info.audio_track = 1
        mocked_controller.media_info.subtitle_track = 1
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        vlc_player = VlcPlayer(None)
        vlc_player.state = MediaState.Paused

        # WHEN: play() is called
        with patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait, \
                patch.object(vlc_player, 'volume') as mocked_volume:
            mocked_media_state_wait.return_value = True
            result = vlc_player.play(mocked_display)

        # THEN: A bunch of things should happen to play the media
        mocked_thread.start.assert_called_with()
        mocked_display.vlc_media_player.set_title.assert_called_with(1)
        mocked_display.vlc_media_player.play.assert_called_with()
        mocked_display.vlc_media_player.audio_set_track.assert_called_with(1)
        mocked_display.vlc_media_player.video_set_spu.assert_called_with(1)
        self.assertEqual(50, mocked_controller.media_info.length)
        mocked_volume.assert_called_with(mocked_display, 100)
        mocked_controller.seek_slider.setMaximum.assert_called_with(50000)
        self.assertEqual(MediaState.Playing, vlc_player.state)
        mocked_display.vlc_widget.raise_.assert_called_with()
        self.assertTrue(result, 'The value returned from play() should be True')

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def pause_test(self, mocked_get_vlc):
        """
        Test that the pause method works correctly
        """
        # GIVEN: A mocked out get_vlc method
        mocked_vlc = MagicMock()
        mocked_vlc.State.Playing = 1
        mocked_vlc.State.Paused = 2
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 1
        vlc_player = VlcPlayer(None)

        # WHEN: The media is paused
        with patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait:
            mocked_media_state_wait.return_value = True
            vlc_player.pause(mocked_display)

        # THEN: The pause method should exit early
        mocked_display.vlc_media.get_state.assert_called_with()
        mocked_display.vlc_media_player.pause.assert_called_with()
        mocked_media_state_wait.assert_called_with(mocked_display, 2)
        self.assertEqual(MediaState.Paused, vlc_player.state)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def pause_not_playing_test(self, mocked_get_vlc):
        """
        Test the pause method when the player is not playing
        """
        # GIVEN: A mocked out get_vlc method
        mocked_vlc = MagicMock()
        mocked_vlc.State.Playing = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 2
        vlc_player = VlcPlayer(None)

        # WHEN: The media is paused
        vlc_player.pause(mocked_display)

        # THEN: The pause method should exit early
        mocked_display.vlc_media.get_state.assert_called_with()
        self.assertEqual(0, mocked_display.vlc_media_player.pause.call_count)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def pause_fail_test(self, mocked_get_vlc):
        """
        Test the pause method when the player fails to pause the media
        """
        # GIVEN: A mocked out get_vlc method
        mocked_vlc = MagicMock()
        mocked_vlc.State.Playing = 1
        mocked_vlc.State.Paused = 2
        mocked_get_vlc.return_value = mocked_vlc
        mocked_display = MagicMock()
        mocked_display.vlc_media.get_state.return_value = 1
        vlc_player = VlcPlayer(None)

        # WHEN: The media is paused
        with patch.object(vlc_player, 'media_state_wait') as mocked_media_state_wait:
            mocked_media_state_wait.return_value = False
            vlc_player.pause(mocked_display)

        # THEN: The pause method should exit early
        mocked_display.vlc_media.get_state.assert_called_with()
        mocked_display.vlc_media_player.pause.assert_called_with()
        mocked_media_state_wait.assert_called_with(mocked_display, 2)
        self.assertNotEqual(MediaState.Paused, vlc_player.state)

    @patch('openlp.core.ui.media.vlcplayer.threading')
    def stop_test(self, mocked_threading):
        """
        Test stopping the current item
        """
        # GIVEN: A display object and a VlcPlayer instance and some mocked threads
        mocked_thread = MagicMock()
        mocked_threading.Thread.return_value = mocked_thread
        mocked_stop = MagicMock()
        mocked_display = MagicMock()
        mocked_display.vlc_media_player.stop = mocked_stop
        vlc_player = VlcPlayer(None)

        # WHEN: stop is called
        vlc_player.stop(mocked_display)

        # THEN: A thread should have been started to stop VLC
        mocked_threading.Thread.assert_called_with(target=mocked_stop)
        mocked_thread.start.assert_called_with()
        self.assertEqual(MediaState.Stopped, vlc_player.state)

    def volume_test(self):
        """
        Test setting the volume
        """
        # GIVEN: A display object and a VlcPlayer instance
        mocked_display = MagicMock()
        mocked_display.has_audio = True
        vlc_player = VlcPlayer(None)

        # WHEN: The volume is set
        vlc_player.volume(mocked_display, 10)

        # THEN: The volume should have been set
        mocked_display.vlc_media_player.audio_set_volume.assert_called_with(10)

    def volume_no_audio_test(self):
        """
        Test setting the volume when there's no audio
        """
        # GIVEN: A display object and a VlcPlayer instance
        mocked_display = MagicMock()
        mocked_display.has_audio = False
        vlc_player = VlcPlayer(None)

        # WHEN: The volume is set
        vlc_player.volume(mocked_display, 10)

        # THEN: The volume should NOT have been set
        self.assertEqual(0, mocked_display.vlc_media_player.audio_set_volume.call_count)

    def seek_unseekable_media_test(self):
        """
        Test seeking something that can't be seeked
        """
        # GIVEN: Unseekable media
        mocked_display = MagicMock()
        mocked_display.controller.media_info.media_type = MediaType.Audio
        mocked_display.vlc_media_player.is_seekable.return_value = False
        vlc_player = VlcPlayer(None)

        # WHEN: seek() is called
        vlc_player.seek(mocked_display, 100)

        # THEN: nothing should happen
        mocked_display.vlc_media_player.is_seekable.assert_called_with()
        self.assertEqual(0, mocked_display.vlc_media_player.set_time.call_count)

    def seek_seekable_media_test(self):
        """
        Test seeking something that is seekable, but not a DVD
        """
        # GIVEN: Unseekable media
        mocked_display = MagicMock()
        mocked_display.controller.media_info.media_type = MediaType.Audio
        mocked_display.vlc_media_player.is_seekable.return_value = True
        vlc_player = VlcPlayer(None)

        # WHEN: seek() is called
        vlc_player.seek(mocked_display, 100)

        # THEN: nothing should happen
        mocked_display.vlc_media_player.is_seekable.assert_called_with()
        mocked_display.vlc_media_player.set_time.assert_called_with(100)

    def seek_dvd_test(self):
        """
        Test seeking a DVD
        """
        # GIVEN: Unseekable media
        mocked_display = MagicMock()
        mocked_display.controller.media_info.media_type = MediaType.DVD
        mocked_display.vlc_media_player.is_seekable.return_value = True
        mocked_display.controller.media_info.start_time = 3
        vlc_player = VlcPlayer(None)

        # WHEN: seek() is called
        vlc_player.seek(mocked_display, 2000)

        # THEN: nothing should happen
        mocked_display.vlc_media_player.is_seekable.assert_called_with()
        mocked_display.vlc_media_player.set_time.assert_called_with(5000)

    def reset_test(self):
        """
        Test the reset() method
        """
        # GIVEN: Some mocked out stuff
        mocked_display = MagicMock()
        vlc_player = VlcPlayer(None)

        # WHEN: reset() is called
        vlc_player.reset(mocked_display)

        # THEN: The media should be stopped and invsibile
        mocked_display.vlc_media_player.stop.assert_called_with()
        mocked_display.vlc_widget.setVisible.assert_called_with(False)
        self.assertEqual(MediaState.Off, vlc_player.state)

    def set_visible_has_own_widget_test(self):
        """
        Test the set_visible() method when the player has its own widget
        """
        # GIVEN: Some mocked out stuff
        mocked_display = MagicMock()
        vlc_player = VlcPlayer(None)
        vlc_player.has_own_widget = True

        # WHEN: reset() is called
        vlc_player.set_visible(mocked_display, True)

        # THEN: The media should be stopped and invsibile
        mocked_display.vlc_widget.setVisible.assert_called_with(True)

    def set_visible_no_widget_test(self):
        """
        Test the set_visible() method when the player doesn't have a widget
        """
        # GIVEN: Some mocked out stuff
        mocked_display = MagicMock()
        vlc_player = VlcPlayer(None)
        vlc_player.has_own_widget = False

        # WHEN: reset() is called
        vlc_player.set_visible(mocked_display, True)

        # THEN: The media should be stopped and invsibile
        self.assertEqual(0, mocked_display.vlc_widget.setVisible.call_count)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def update_ui_test(self, mocked_get_vlc):
        """
        Test updating the UI
        """
        # GIVEN: A whole bunch of mocks
        mocked_vlc = MagicMock()
        mocked_vlc.State.Ended = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.end_time = 300
        mocked_controller.seek_slider.isSliderDown.return_value = False
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_media.get_state.return_value = 1
        mocked_display.vlc_media_player.get_time.return_value = 400000
        vlc_player = VlcPlayer(None)

        # WHEN: update_ui() is called
        with patch.object(vlc_player, 'stop') as mocked_stop, \
                patch.object(vlc_player, 'set_visible') as mocked_set_visible:
            vlc_player.update_ui(mocked_display)

        # THEN: Certain methods should be called
        mocked_stop.assert_called_with(mocked_display)
        self.assertEqual(2, mocked_stop.call_count)
        mocked_display.vlc_media_player.get_time.assert_called_with()
        mocked_set_visible.assert_called_with(mocked_display, False)
        mocked_controller.seek_slider.setSliderPosition.assert_called_with(400000)
        expected_calls = [call(True), call(False)]
        self.assertEqual(expected_calls, mocked_controller.seek_slider.blockSignals.call_args_list)

    @patch('openlp.core.ui.media.vlcplayer.get_vlc')
    def update_ui_dvd_test(self, mocked_get_vlc):
        """
        Test updating the UI for a CD or DVD
        """
        # GIVEN: A whole bunch of mocks
        mocked_vlc = MagicMock()
        mocked_vlc.State.Ended = 1
        mocked_get_vlc.return_value = mocked_vlc
        mocked_controller = MagicMock()
        mocked_controller.media_info.start_time = 100
        mocked_controller.media_info.end_time = 300
        mocked_controller.seek_slider.isSliderDown.return_value = False
        mocked_display = MagicMock()
        mocked_display.controller = mocked_controller
        mocked_display.vlc_media.get_state.return_value = 1
        mocked_display.vlc_media_player.get_time.return_value = 400000
        mocked_display.controller.media_info.media_type = MediaType.DVD
        vlc_player = VlcPlayer(None)

        # WHEN: update_ui() is called
        with patch.object(vlc_player, 'stop') as mocked_stop, \
                patch.object(vlc_player, 'set_visible') as mocked_set_visible:
            vlc_player.update_ui(mocked_display)

        # THEN: Certain methods should be called
        mocked_stop.assert_called_with(mocked_display)
        self.assertEqual(2, mocked_stop.call_count)
        mocked_display.vlc_media_player.get_time.assert_called_with()
        mocked_set_visible.assert_called_with(mocked_display, False)
        mocked_controller.seek_slider.setSliderPosition.assert_called_with(300000)
        expected_calls = [call(True), call(False)]
        self.assertEqual(expected_calls, mocked_controller.seek_slider.blockSignals.call_args_list)

    @patch('openlp.core.ui.media.vlcplayer.translate')
    def get_info_test(self, mocked_translate):
        """
        Test that get_info() returns some information about the VLC player
        """
        # GIVEN: A VlcPlayer
        mocked_translate.side_effect = lambda *x: x[1]
        vlc_player = VlcPlayer(None)

        # WHEN: get_info() is run
        info = vlc_player.get_info()

        # THEN: The information should be correct
        self.assertEqual('VLC is an external player which supports a number of different formats.<br/> '
                         '<strong>Audio</strong><br/>' + str(AUDIO_EXT) + '<br/><strong>Video</strong><br/>' +
                         str(VIDEO_EXT) + '<br/>', info)
