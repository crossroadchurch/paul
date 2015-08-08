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
Package to test the openlp.core.ui.slidecontroller package.
"""
from unittest import TestCase

from PyQt4 import QtCore

from openlp.core.common import Registry
from openlp.core.lib import ScreenList
from openlp.core.ui import MainDisplay
from openlp.core.ui.maindisplay import TRANSPARENT_STYLESHEET, OPAQUE_STYLESHEET

from tests.helpers.testmixin import TestMixin
from tests.functional import MagicMock, patch


class TestMainDisplay(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = 0
        self.desktop.screenCount.return_value = 2
        self.desktop.screenGeometry.side_effect = lambda x: {0: QtCore.QRect(0, 0, 1024, 768),
                                                             1: QtCore.QRect(0, 0, 1024, 768)}[x]
        self.screens = ScreenList.create(self.desktop)
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        Registry().register('application', self.app)
        self.mocked_audio_player = patch('openlp.core.ui.maindisplay.AudioPlayer')
        self.mocked_audio_player.start()

    def tearDown(self):
        """
        Delete QApplication.
        """
        self.mocked_audio_player.stop()
        del self.screens

    def initial_main_display_test(self):
        """
        Test the initial Main Display state
        """
        # GIVEN: A new SlideController instance.
        display = MagicMock()
        display.is_live = True

        # WHEN: The default controller is built.
        main_display = MainDisplay(display)

        # THEN: The controller should be a live controller.
        self.assertEqual(main_display.is_live, True, 'The main display should be a live controller')

    def set_transparency_enabled_test(self):
        """
        Test setting the display to be transparent
        """
        # GIVEN: An instance of MainDisplay
        display = MagicMock()
        main_display = MainDisplay(display)

        # WHEN: Transparency is enabled
        main_display.set_transparency(True)

        # THEN: The transparent stylesheet should be used
        self.assertEqual(TRANSPARENT_STYLESHEET, main_display.styleSheet(),
                         'The MainDisplay should use the transparent stylesheet')
        self.assertFalse(main_display.autoFillBackground(),
                         'The MainDisplay should not have autoFillBackground set')
        self.assertTrue(main_display.testAttribute(QtCore.Qt.WA_TranslucentBackground),
                        'The MainDisplay should have a translucent background')

    def set_transparency_disabled_test(self):
        """
        Test setting the display to be opaque
        """
        # GIVEN: An instance of MainDisplay
        display = MagicMock()
        main_display = MainDisplay(display)

        # WHEN: Transparency is disabled
        main_display.set_transparency(False)

        # THEN: The opaque stylesheet should be used
        self.assertEqual(OPAQUE_STYLESHEET, main_display.styleSheet(),
                         'The MainDisplay should use the opaque stylesheet')
        self.assertFalse(main_display.testAttribute(QtCore.Qt.WA_TranslucentBackground),
                         'The MainDisplay should not have a translucent background')

    def css_changed_test(self):
        """
        Test that when the CSS changes, the plugins are looped over and given an opportunity to update the CSS
        """
        # GIVEN: A mocked list of plugins, a mocked display and a MainDisplay
        mocked_songs_plugin = MagicMock()
        mocked_bibles_plugin = MagicMock()
        mocked_plugin_manager = MagicMock()
        mocked_plugin_manager.plugins = [mocked_songs_plugin, mocked_bibles_plugin]
        Registry().register('plugin_manager', mocked_plugin_manager)
        display = MagicMock()
        main_display = MainDisplay(display)
        # This is set up dynamically, so we need to mock it out for now
        main_display.frame = MagicMock()

        # WHEN: The css_changed() method is triggered
        main_display.css_changed()

        # THEN: The plugins should have each been given an opportunity to add their bit to the CSS
        mocked_songs_plugin.refresh_css.assert_called_with(main_display.frame)
        mocked_bibles_plugin.refresh_css.assert_called_with(main_display.frame)

    @patch('openlp.core.ui.maindisplay.is_macosx')
    def macosx_non_primary_screen_window_flags_state_test(self, is_macosx):
        """
        Test that on Mac OS X when the current screen isn't primary we set the proper window flags and window state
        """
        # GIVEN: A new SlideController instance on Mac OS X with the current display not being primary.
        is_macosx.return_value = True
        self.screens.set_current_display(1)
        display = MagicMock()

        # WHEN: The default controller is built.
        main_display = MainDisplay(display)

        # THEN: The window flags and state should be the same as those needed on Mac OS X for the non primary display.
        self.assertEqual(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint,
                         main_display.windowFlags(),
                         'The window flags should be Qt.WindowStaysOnTop, Qt.Window, and Qt.FramelessWindowHint.')
        self.assertNotEqual(QtCore.Qt.WindowFullScreen, main_display.windowState(),
                            'The window state should not be full screen.')

    @patch('openlp.core.ui.maindisplay.is_macosx')
    def macosx_primary_screen_window_flags_state_test(self, is_macosx):
        """
        Test that on Mac OS X when the current screen is primary we set the proper window flags and window state
        """
        # GIVEN: A new SlideController instance on Mac OS X with the current display being primary.
        is_macosx.return_value = True
        self.screens.set_current_display(0)
        display = MagicMock()

        # WHEN: The default controller is built.
        main_display = MainDisplay(display)

        # THEN: The window flags and state should be the same as those needed on Mac OS X for the primary display.
        self.assertEqual(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint, main_display.windowFlags(),
                         'The window flags should be Qt.Window and Qt.FramelessWindowHint.')
        self.assertEqual(QtCore.Qt.WindowFullScreen, main_display.windowState(),
                         'The window state should be full screen.')
