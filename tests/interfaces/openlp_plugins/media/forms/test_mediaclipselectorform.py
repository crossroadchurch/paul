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
Module to test the MediaClipSelectorForm.
"""

import os
from unittest import TestCase, SkipTest
from openlp.core.ui.media.vlcplayer import get_vlc

if os.name == 'nt' and not get_vlc():
    raise SkipTest('Windows without VLC, skipping this test since it cannot run without vlc')

from PyQt4 import QtGui, QtTest, QtCore

from openlp.core.common import Registry
from openlp.plugins.media.forms.mediaclipselectorform import MediaClipSelectorForm
from tests.interfaces import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMediaClipSelectorForm(TestCase, TestMixin):
    """
    Test the EditCustomSlideForm.
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        # Mock VLC so we don't actually use it
        self.vlc_patcher = patch('openlp.plugins.media.forms.mediaclipselectorform.vlc')
        self.vlc_patcher.start()
        Registry().register('application', self.app)
        # Mock the media item
        self.mock_media_item = MagicMock()
        # create form to test
        self.form = MediaClipSelectorForm(self.mock_media_item, self.main_window, None)
        mock_media_state_wait = MagicMock()
        mock_media_state_wait.return_value = True
        self.form.media_state_wait = mock_media_state_wait
        self.form.application.set_busy_cursor = MagicMock()
        self.form.application.set_normal_cursor = MagicMock()
        self.form.find_optical_devices = MagicMock()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        self.vlc_patcher.stop()
        del self.main_window

    def basic_test(self):
        """
        Test if the dialog is correctly set up.
        """
        # GIVEN: A mocked QDialog.exec_() method
        with patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            # WHEN: Show the dialog.
            self.form.exec_()

            # THEN: The media path should be empty.
            assert self.form.media_path_combobox.currentText() == '', 'There should not be any text in the media path.'

    def click_load_button_test(self):
        """
        Test that the correct function is called when load is clicked, and that it behaves as expected.
        """
        # GIVEN: Mocked methods.
        with patch('openlp.plugins.media.forms.mediaclipselectorform.critical_error_message_box') as \
                mocked_critical_error_message_box,\
                patch('openlp.plugins.media.forms.mediaclipselectorform.os.path.exists') as mocked_os_path_exists,\
                patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            self.form.exec_()

            # WHEN: The load button is clicked with no path set
            QtTest.QTest.mouseClick(self.form.load_disc_button, QtCore.Qt.LeftButton)

            # THEN: we should get an error
            mocked_critical_error_message_box.assert_called_with(message='No path was given')

            # WHEN: The load button is clicked with a non-existing path
            mocked_os_path_exists.return_value = False
            self.form.media_path_combobox.insertItem(0, '/non-existing/test-path.test')
            self.form.media_path_combobox.setCurrentIndex(0)
            QtTest.QTest.mouseClick(self.form.load_disc_button, QtCore.Qt.LeftButton)

            # THEN: we should get an error
            assert self.form.media_path_combobox.currentText() == '/non-existing/test-path.test',\
                'The media path should be the given one.'
            mocked_critical_error_message_box.assert_called_with(message='Given path does not exists')

            # WHEN: The load button is clicked with a mocked existing path
            mocked_os_path_exists.return_value = True
            self.form.vlc_media_player = MagicMock()
            self.form.vlc_media_player.play.return_value = -1
            self.form.media_path_combobox.insertItem(0, '/existing/test-path.test')
            self.form.media_path_combobox.setCurrentIndex(0)
            QtTest.QTest.mouseClick(self.form.load_disc_button, QtCore.Qt.LeftButton)

            # THEN: we should get an error
            assert self.form.media_path_combobox.currentText() == '/existing/test-path.test',\
                'The media path should be the given one.'
            mocked_critical_error_message_box.assert_called_with(message='VLC player failed playing the media')

    def title_combobox_test(self):
        """
        Test the behavior when the title combobox is updated
        """
        # GIVEN: Mocked methods and some entries in the title combobox.
        with patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            self.form.exec_()
            self.form.vlc_media_player.get_length.return_value = 1000
            self.form.audio_tracks_combobox.itemData = MagicMock()
            self.form.subtitle_tracks_combobox.itemData = MagicMock()
            self.form.audio_tracks_combobox.itemData.return_value = None
            self.form.subtitle_tracks_combobox.itemData.return_value = None
            self.form.titles_combo_box.insertItem(0, 'Test Title 0')
            self.form.titles_combo_box.insertItem(1, 'Test Title 1')

            # WHEN: There exists audio and subtitle tracks and the index is updated.
            self.form.vlc_media_player.audio_get_track_description.return_value = [(-1, b'Disabled'),
                                                                                   (0, b'Audio Track 1')]
            self.form.vlc_media_player.video_get_spu_description.return_value = [(-1, b'Disabled'),
                                                                                 (0, b'Subtitle Track 1')]
            self.form.titles_combo_box.setCurrentIndex(1)

            # THEN: The subtitle and audio track comboboxes should be updated and get signals and call itemData.
            self.form.audio_tracks_combobox.itemData.assert_any_call(0)
            self.form.audio_tracks_combobox.itemData.assert_any_call(1)
            self.form.subtitle_tracks_combobox.itemData.assert_any_call(0)

    def click_save_button_test(self):
        """
        Test that the correct function is called when save is clicked, and that it behaves as expected.
        """
        # GIVEN: Mocked methods.
        with patch('openlp.plugins.media.forms.mediaclipselectorform.critical_error_message_box') as \
                mocked_critical_error_message_box,\
                patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            self.form.exec_()

            # WHEN: The save button is clicked with a NoneType in start_time_ms or end_time_ms
            self.form.accept()

            # THEN: we should get an error message
            mocked_critical_error_message_box.assert_called_with('DVD not loaded correctly',
                                                                 'The DVD was not loaded correctly, '
                                                                 'please re-load and try again.')
