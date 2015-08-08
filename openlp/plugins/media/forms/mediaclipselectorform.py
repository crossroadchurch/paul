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

import os
import logging
import re
from time import sleep
from datetime import datetime

from PyQt4 import QtCore, QtGui

from openlp.core.common import translate, is_win, is_linux, is_macosx, RegistryProperties
from openlp.plugins.media.forms.mediaclipselectordialog import Ui_MediaClipSelector
from openlp.core.lib.ui import critical_error_message_box

if is_win():
    from win32com.client import Dispatch

if is_linux():
    import dbus

try:
    from openlp.core.ui.media.vendor import vlc
except (ImportError, NameError, NotImplementedError):
    pass
except OSError as e:
    if is_win():
        if not isinstance(e, WindowsError) and e.winerror != 126:
            raise
    else:
        raise

log = logging.getLogger(__name__)


class MediaClipSelectorForm(QtGui.QDialog, Ui_MediaClipSelector, RegistryProperties):
    """
    Class to manage the clip selection
    """
    log.info('%s MediaClipSelectorForm loaded', __name__)

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(MediaClipSelectorForm, self).__init__(parent)
        self.vlc_instance = None
        self.vlc_media_player = None
        self.vlc_media = None
        self.timer = None
        self.audio_cd_tracks = None
        self.audio_cd = False
        self.playback_length = 0
        self.media_item = media_item
        self.setupUi(self)
        # setup play/pause icon
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(QtGui.QPixmap(":/slides/media_playback_start.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(":/slides/media_playback_pause.png"), QtGui.QIcon.Normal,
                                  QtGui.QIcon.Off)

    def reject(self):
        """
        Exit Dialog and do not save
        """
        log.debug('MediaClipSelectorForm.reject')
        # Tear down vlc
        if self.vlc_media_player:
            self.vlc_media_player.stop()
            self.vlc_media_player.release()
            self.vlc_media_player = None
        if self.vlc_instance:
            self.vlc_instance.release()
            self.vlc_instance = None
        if self.vlc_media:
            self.vlc_media.release()
            self.vlc_media = None
        return QtGui.QDialog.reject(self)

    def exec_(self):
        """
        Start dialog
        """
        self.reset_ui()
        self.setup_vlc()
        return QtGui.QDialog.exec_(self)

    def reset_ui(self):
        """
        Reset the UI to default values
        """
        self.playback_length = 0
        self.position_slider.setMinimum(0)
        self.disable_all()
        self.toggle_disable_load_media(False)
        self.subtitle_tracks_combobox.clear()
        self.audio_tracks_combobox.clear()
        self.titles_combo_box.clear()
        time = QtCore.QTime()
        self.start_position_edit.setTime(time)
        self.end_timeedit.setTime(time)
        self.position_timeedit.setTime(time)

    def setup_vlc(self):
        """
        Setup VLC instance and mediaplayer
        """
        self.vlc_instance = vlc.Instance()
        # creating an empty vlc media player
        self.vlc_media_player = self.vlc_instance.media_player_new()
        # The media player has to be 'connected' to the QFrame.
        # (otherwise a video would be displayed in it's own window)
        # This is platform specific!
        # You have to give the id of the QFrame (or similar object)
        # to vlc, different platforms have different functions for this.
        win_id = int(self.preview_frame.winId())
        if is_win():
            self.vlc_media_player.set_hwnd(win_id)
        elif is_macosx():
            # We have to use 'set_nsobject' since Qt4 on OSX uses Cocoa
            # framework and not the old Carbon.
            self.vlc_media_player.set_nsobject(win_id)
        else:
            # for Linux using the X Server
            self.vlc_media_player.set_xwindow(win_id)
        self.vlc_media = None
        # Setup timer every 100 ms to update position
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)
        self.find_optical_devices()
        self.audio_cd = False
        self.audio_cd_tracks = None

    def detect_audio_cd(self, path):
        """
        Detects is the given path is an audio CD

        :param path: Path to the device to be tested.
        :return: True if it was an audio CD else False.
        """
        # Detect by trying to play it as a CD
        self.vlc_media = self.vlc_instance.media_new_location('cdda://' + path)
        self.vlc_media_player.set_media(self.vlc_media)
        self.vlc_media_player.play()
        # Wait for media to start playing. In this case VLC actually returns an error.
        self.media_state_wait(vlc.State.Playing)
        self.vlc_media_player.set_pause(1)
        # If subitems exists, this is a CD
        self.audio_cd_tracks = self.vlc_media.subitems()
        if not self.audio_cd_tracks or self.audio_cd_tracks.count() < 1:
            return False
        # Insert into titles_combo_box
        self.titles_combo_box.clear()
        for i in range(self.audio_cd_tracks.count()):
            item = self.audio_cd_tracks.item_at_index(i)
            item_title = item.get_meta(vlc.Meta.Title)
            self.titles_combo_box.addItem(item_title, i)
        self.vlc_media_player.set_media(self.audio_cd_tracks.item_at_index(0))
        self.audio_cd = True
        self.titles_combo_box.setDisabled(False)
        self.titles_combo_box.setCurrentIndex(0)
        self.on_titles_combo_box_currentIndexChanged(0)

        return True

    @QtCore.pyqtSlot(bool)
    def on_load_disc_button_clicked(self, clicked):
        """
        Load the media when the load-button has been clicked

        :param clicked: Given from signal, not used.
        """
        log.debug('on_load_disc_button_clicked')
        self.disable_all()
        self.application.set_busy_cursor()
        path = self.media_path_combobox.currentText()
        # Check if given path is non-empty and exists before starting VLC
        if not path:
            log.debug('no given path')
            critical_error_message_box(message=translate('MediaPlugin.MediaClipSelectorForm', 'No path was given'))
            self.toggle_disable_load_media(False)
            self.application.set_normal_cursor()
            return
        if not os.path.exists(path):
            log.debug('Given path does not exists')
            critical_error_message_box(message=translate('MediaPlugin.MediaClipSelectorForm',
                                                         'Given path does not exists'))
            self.toggle_disable_load_media(False)
            self.application.set_normal_cursor()
            return
        # VLC behaves a bit differently on windows and linux when loading, which creates problems when trying to
        # detect if we're dealing with a DVD or CD, so we use different loading approaches depending on the OS.
        if is_win():
            # If the given path is in the format "D:\" or "D:", prefix it with "/" to make VLC happy
            pattern = re.compile('^\w:\\\\*$')
            if pattern.match(path):
                path = '/' + path
            self.vlc_media = self.vlc_instance.media_new_location('dvd://' + path)
        else:
            self.vlc_media = self.vlc_instance.media_new_path(path)
        if not self.vlc_media:
            log.debug('vlc media player is none')
            critical_error_message_box(message=translate('MediaPlugin.MediaClipSelectorForm',
                                                         'An error happened during initialization of VLC player'))
            self.toggle_disable_load_media(False)
            self.application.set_normal_cursor()
            return
        # put the media in the media player
        self.vlc_media_player.set_media(self.vlc_media)
        self.vlc_media_player.audio_set_mute(True)
        # start playback to get vlc to parse the media
        if self.vlc_media_player.play() < 0:
            log.debug('vlc play returned error')
            critical_error_message_box(message=translate('MediaPlugin.MediaClipSelectorForm',
                                                         'VLC player failed playing the media'))
            self.toggle_disable_load_media(False)
            self.application.set_normal_cursor()
            self.vlc_media_player.audio_set_mute(False)
            return
        self.vlc_media_player.audio_set_mute(True)
        if not self.media_state_wait(vlc.State.Playing):
            # Tests if this is an audio CD
            if not self.detect_audio_cd(path):
                critical_error_message_box(message=translate('MediaPlugin.MediaClipSelectorForm',
                                                             'VLC player failed playing the media'))
                self.toggle_disable_load_media(False)
                self.application.set_normal_cursor()
                self.vlc_media_player.audio_set_mute(False)
                return
        # pause
        self.vlc_media_player.set_time(0)
        self.vlc_media_player.set_pause(1)
        self.media_state_wait(vlc.State.Paused)
        self.toggle_disable_load_media(False)
        self.application.set_normal_cursor()
        self.vlc_media_player.audio_set_mute(False)
        if not self.audio_cd:
            # Temporarily disable signals
            self.blockSignals(True)
            # Get titles, insert in combobox
            titles = self.vlc_media_player.video_get_title_description()
            self.titles_combo_box.clear()
            for title in titles:
                self.titles_combo_box.addItem(title[1].decode(), title[0])
            # Re-enable signals
            self.blockSignals(False)
            # Main title is usually title #1
            if len(titles) > 1:
                self.titles_combo_box.setCurrentIndex(1)
            # Enable audio track combobox if anything is in it
            if len(titles) > 0:
                self.titles_combo_box.setDisabled(False)
        log.debug('load_disc_button end - vlc_media_player state: %s' % self.vlc_media_player.get_state())

    @QtCore.pyqtSlot(bool)
    def on_play_button_clicked(self, clicked):
        """
        Toggle the playback

        :param clicked: Given from signal, not used.
        """
        if self.vlc_media_player.get_state() == vlc.State.Playing:
            self.vlc_media_player.pause()
            self.play_button.setIcon(self.play_icon)
        else:
            self.vlc_media_player.play()
            self.media_state_wait(vlc.State.Playing)
            self.play_button.setIcon(self.pause_icon)

    @QtCore.pyqtSlot(bool)
    def on_set_start_button_clicked(self, clicked):
        """
        Copy the current player position to start_position_edit

        :param clicked: Given from signal, not used.
        """
        vlc_ms_pos = self.vlc_media_player.get_time()
        time = QtCore.QTime()
        new_pos_time = time.addMSecs(vlc_ms_pos)
        self.start_position_edit.setTime(new_pos_time)
        # If start time is after end time, update end time.
        end_time = self.end_timeedit.time()
        if end_time < new_pos_time:
            self.end_timeedit.setTime(new_pos_time)

    @QtCore.pyqtSlot(bool)
    def on_set_end_button_clicked(self, clicked):
        """
        Copy the current player position to end_timeedit

        :param clicked: Given from signal, not used.
        """
        vlc_ms_pos = self.vlc_media_player.get_time()
        time = QtCore.QTime()
        new_pos_time = time.addMSecs(vlc_ms_pos)
        self.end_timeedit.setTime(new_pos_time)
        # If start time is after end time, update start time.
        start_time = self.start_position_edit.time()
        if start_time > new_pos_time:
            self.start_position_edit.setTime(new_pos_time)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_start_timeedit_timeChanged(self, new_time):
        """
        Called when start_position_edit is changed manually

        :param new_time: The new time
        """
        # If start time is after end time, update end time.
        end_time = self.end_timeedit.time()
        if end_time < new_time:
            self.end_timeedit.setTime(new_time)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_end_timeedit_timeChanged(self, new_time):
        """
        Called when end_timeedit is changed manually

        :param new_time: The new time
        """
        # If start time is after end time, update start time.
        start_time = self.start_position_edit.time()
        if start_time > new_time:
            self.start_position_edit.setTime(new_time)

    @QtCore.pyqtSlot(bool)
    def on_jump_end_button_clicked(self, clicked):
        """
        Set the player position to the position stored in end_timeedit

        :param clicked: Given from signal, not used.
        """
        end_time = self.end_timeedit.time()
        end_time_ms = end_time.hour() * 60 * 60 * 1000 + \
            end_time.minute() * 60 * 1000 + \
            end_time.second() * 1000 + \
            end_time.msec()
        self.vlc_media_player.set_time(end_time_ms)

    @QtCore.pyqtSlot(bool)
    def on_jump_start_button_clicked(self, clicked):
        """
        Set the player position to the position stored in start_position_edit

        :param clicked: Given from signal, not used.
        """
        start_time = self.start_position_edit.time()
        start_time_ms = start_time.hour() * 60 * 60 * 1000 + \
            start_time.minute() * 60 * 1000 + \
            start_time.second() * 1000 + \
            start_time.msec()
        self.vlc_media_player.set_time(start_time_ms)

    @QtCore.pyqtSlot(int)
    def on_titles_combo_box_currentIndexChanged(self, index):
        """
        When a new title is chosen, it is loaded by VLC and info about audio and subtitle tracks is reloaded

        :param index: The index of the newly chosen title track.
        """
        log.debug('in on_titles_combo_box_changed, index: %d', index)
        if not self.vlc_media_player:
            log.error('vlc_media_player was None')
            return
        self.application.set_busy_cursor()
        if self.audio_cd:
            self.vlc_media = self.audio_cd_tracks.item_at_index(index)
            self.vlc_media_player.set_media(self.vlc_media)
            self.vlc_media_player.set_time(0)
            self.vlc_media_player.play()
            if not self.media_state_wait(vlc.State.Playing):
                log.error('Could not start playing audio cd, needed to get track info')
                self.application.set_normal_cursor()
                return
            self.vlc_media_player.audio_set_mute(True)
            # pause
            self.vlc_media_player.set_time(0)
            self.vlc_media_player.set_pause(1)
            self.vlc_media_player.audio_set_mute(False)
            self.application.set_normal_cursor()
            self.toggle_disable_player(False)
        else:
            self.vlc_media_player.set_title(index)
            self.vlc_media_player.set_time(0)
            self.vlc_media_player.play()
            if not self.media_state_wait(vlc.State.Playing):
                log.error('Could not start playing dvd, needed to get track info')
                self.application.set_normal_cursor()
                return
            self.vlc_media_player.audio_set_mute(True)
            # Get audio tracks
            audio_tracks = self.vlc_media_player.audio_get_track_description()
            log.debug('number of audio tracks: %d' % len(audio_tracks))
            # Clear the audio track combobox, insert new tracks
            self.audio_tracks_combobox.clear()
            for audio_track in audio_tracks:
                self.audio_tracks_combobox.addItem(audio_track[1].decode(), audio_track[0])
            # Enable audio track combobox if anything is in it
            if len(audio_tracks) > 0:
                self.audio_tracks_combobox.setDisabled(False)
                # First track is "deactivated", so set to next if it exists
                if len(audio_tracks) > 1:
                    self.audio_tracks_combobox.setCurrentIndex(1)
            # Get subtitle tracks, insert in combobox
            subtitles_tracks = self.vlc_media_player.video_get_spu_description()
            self.subtitle_tracks_combobox.clear()
            for subtitle_track in subtitles_tracks:
                self.subtitle_tracks_combobox.addItem(subtitle_track[1].decode(), subtitle_track[0])
            # Enable subtitle track combobox is anything in it
            if len(subtitles_tracks) > 0:
                self.subtitle_tracks_combobox.setDisabled(False)
            self.vlc_media_player.audio_set_mute(False)
            self.vlc_media_player.set_pause(1)
            # If a title or audio track is available the player is enabled
            if self.titles_combo_box.count() > 0 or len(audio_tracks) > 0:
                self.toggle_disable_player(False)
        # Set media length info
        self.playback_length = self.vlc_media_player.get_length()
        log.debug('playback_length: %d ms' % self.playback_length)
        # if length is 0, wait a bit, maybe vlc will change its mind...
        loop_count = 0
        while self.playback_length == 0 and loop_count < 20:
            sleep(0.1)
            self.playback_length = self.vlc_media_player.get_length()
            loop_count += 1
            log.debug('in loop, playback_length: %d ms' % self.playback_length)
        self.position_slider.setMaximum(self.playback_length)
        # setup start and end time
        rounded_vlc_ms_length = int(round(self.playback_length / 100.0) * 100.0)
        time = QtCore.QTime()
        playback_length_time = time.addMSecs(rounded_vlc_ms_length)
        self.start_position_edit.setMaximumTime(playback_length_time)
        self.end_timeedit.setMaximumTime(playback_length_time)
        self.end_timeedit.setTime(playback_length_time)
        # Pause once again, just to make sure
        loop_count = 0
        while self.vlc_media_player.get_state() == vlc.State.Playing and loop_count < 20:
            sleep(0.1)
            self.vlc_media_player.set_pause(1)
            loop_count += 1
        log.debug('titles_combo_box end - vlc_media_player state: %s' % self.vlc_media_player.get_state())
        self.application.set_normal_cursor()

    @QtCore.pyqtSlot(int)
    def on_audio_tracks_combobox_currentIndexChanged(self, index):
        """
        When a new audio track is chosen update audio track bing played by VLC

        :param index: The index of the newly chosen audio track.
        """
        if not self.vlc_media_player:
            return
        audio_track = self.audio_tracks_combobox.itemData(index)
        log.debug('in on_audio_tracks_combobox_currentIndexChanged, index: %d  audio_track: %s' % (index, audio_track))
        if audio_track and int(audio_track) > 0:
            self.vlc_media_player.audio_set_track(int(audio_track))

    @QtCore.pyqtSlot(int)
    def on_subtitle_tracks_combobox_currentIndexChanged(self, index):
        """
        When a new subtitle track is chosen update subtitle track bing played by VLC

        :param index: The index of the newly chosen subtitle.
        """
        if not self.vlc_media_player:
            return
        subtitle_track = self.subtitle_tracks_combobox.itemData(index)
        if subtitle_track:
            self.vlc_media_player.video_set_spu(int(subtitle_track))

    def on_position_slider_sliderMoved(self, position):
        """
        Set player position according to new slider position.

        :param position: Position to seek to.
        """
        self.vlc_media_player.set_time(position)

    def update_position(self):
        """
        Update slider position and displayed time according to VLC player position.
        """
        if self.vlc_media_player:
            vlc_ms_pos = self.vlc_media_player.get_time()
            rounded_vlc_ms_pos = int(round(vlc_ms_pos / 100.0) * 100.0)
            time = QtCore.QTime()
            new_pos_time = time.addMSecs(rounded_vlc_ms_pos)
            self.position_timeedit.setTime(new_pos_time)
            self.position_slider.setSliderPosition(vlc_ms_pos)

    def disable_all(self):
        """
        Disable all elements in the dialog
        """
        self.toggle_disable_load_media(True)
        self.titles_combo_box.setDisabled(True)
        self.audio_tracks_combobox.setDisabled(True)
        self.subtitle_tracks_combobox.setDisabled(True)
        self.toggle_disable_player(True)

    def toggle_disable_load_media(self, action):
        """
        Enable/disable load media combobox and button.

        :param action: If True elements are disabled, if False they are enabled.
        """
        self.media_path_combobox.setDisabled(action)
        self.load_disc_button.setDisabled(action)

    def toggle_disable_player(self, action):
        """
        Enable/disable player elements.

        :param action: If True elements are disabled, if False they are enabled.
        """
        self.play_button.setDisabled(action)
        self.position_slider.setDisabled(action)
        self.position_timeedit.setDisabled(action)
        self.start_position_edit.setDisabled(action)
        self.set_start_button.setDisabled(action)
        self.jump_start_button.setDisabled(action)
        self.end_timeedit.setDisabled(action)
        self.set_end_button.setDisabled(action)
        self.jump_end_button.setDisabled(action)
        self.save_button.setDisabled(action)

    def accept(self):
        """
        Saves the current media and trackinfo as a clip to the mediamanager
        """
        log.debug('in MediaClipSelectorForm.accept')
        start_time = self.start_position_edit.time()
        start_time_ms = start_time.hour() * 60 * 60 * 1000 + \
            start_time.minute() * 60 * 1000 + \
            start_time.second() * 1000 + \
            start_time.msec()
        end_time = self.end_timeedit.time()
        end_time_ms = end_time.hour() * 60 * 60 * 1000 + \
            end_time.minute() * 60 * 1000 + \
            end_time.second() * 1000 + \
            end_time.msec()
        title = self.titles_combo_box.itemData(self.titles_combo_box.currentIndex())
        path = self.media_path_combobox.currentText()
        optical = ''
        if self.audio_cd:
            # Check for load problems
            if start_time_ms is None or end_time_ms is None or title is None:
                critical_error_message_box(translate('MediaPlugin.MediaClipSelectorForm', 'CD not loaded correctly'),
                                           translate('MediaPlugin.MediaClipSelectorForm',
                                                     'The CD was not loaded correctly, please re-load and try again.'))
                return
            optical = 'optical:%d:-1:-1:%d:%d:' % (title, start_time_ms, end_time_ms)
        else:
            audio_track = self.audio_tracks_combobox.itemData(self.audio_tracks_combobox.currentIndex())
            subtitle_track = self.subtitle_tracks_combobox.itemData(self.subtitle_tracks_combobox.currentIndex())
            # Check for load problems
            if start_time_ms is None or end_time_ms is None or title is None or audio_track is None\
                    or subtitle_track is None:
                critical_error_message_box(translate('MediaPlugin.MediaClipSelectorForm', 'DVD not loaded correctly'),
                                           translate('MediaPlugin.MediaClipSelectorForm',
                                                     'The DVD was not loaded correctly, please re-load and try again.'))
                return
            optical = 'optical:%d:%d:%d:%d:%d:' % (title, audio_track, subtitle_track, start_time_ms, end_time_ms)
        # Ask for an alternative name for the mediaclip
        while True:
            new_optical_name, ok = QtGui.QInputDialog.getText(self, translate('MediaPlugin.MediaClipSelectorForm',
                                                                              'Set name of mediaclip'),
                                                              translate('MediaPlugin.MediaClipSelectorForm',
                                                                        'Name of mediaclip:'),
                                                              QtGui.QLineEdit.Normal)
            # User pressed cancel, don't save the clip
            if not ok:
                return
            # User pressed ok, but the input text is blank
            if not new_optical_name:
                critical_error_message_box(translate('MediaPlugin.MediaClipSelectorForm',
                                                     'Enter a valid name or cancel'),
                                           translate('MediaPlugin.MediaClipSelectorForm',
                                                     'Enter a valid name or cancel'))
            # The entered new name contains a colon, which we don't allow because colons is used to seperate clip info
            elif new_optical_name.find(':') >= 0:
                critical_error_message_box(translate('MediaPlugin.MediaClipSelectorForm', 'Invalid character'),
                                           translate('MediaPlugin.MediaClipSelectorForm',
                                                     'The name of the mediaclip must not contain the character ":"'))
            # New name entered and we use it
            else:
                break
        # Append the new name to the optical string and the path
        optical += new_optical_name + ':' + path
        self.media_item.add_optical_clip(optical)

    def media_state_wait(self, media_state):
        """
        Wait for the video to change its state
        Wait no longer than 15 seconds. (loading an optical disc takes some time)

        :param media_state: VLC media state to wait for.
        :return: True if state was reached within 15 seconds, False if not or error occurred.
        """
        start = datetime.now()
        while media_state != self.vlc_media_player.get_state():
            if self.vlc_media_player.get_state() == vlc.State.Error:
                return False
            if (datetime.now() - start).seconds > 15:
                return False
        return True

    def find_optical_devices(self):
        """
        Attempt to autodetect optical devices on the computer, and add them to the media-dropdown
        :return:
        """
        # Clear list first
        self.media_path_combobox.clear()
        if is_win():
            # use win api to find optical drives
            fso = Dispatch('scripting.filesystemobject')
            for drive in fso.Drives:
                log.debug('Drive %s has type %d' % (drive.DriveLetter, drive.DriveType))
                # if type is 4, it is a cd-rom drive
                if drive.DriveType == 4:
                    self.media_path_combobox.addItem('%s:\\' % drive.DriveLetter)
        elif is_linux():
            # Get disc devices from dbus and find the ones that are optical
            bus = dbus.SystemBus()
            try:
                udev_manager_obj = bus.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks')
                udev_manager = dbus.Interface(udev_manager_obj, 'org.freedesktop.UDisks')
                for dev in udev_manager.EnumerateDevices():
                    device_obj = bus.get_object("org.freedesktop.UDisks", dev)
                    device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
                    if device_props.Get('org.freedesktop.UDisks.Device', 'DeviceIsDrive'):
                        drive_props = device_props.Get('org.freedesktop.UDisks.Device', 'DriveMediaCompatibility')
                        if any('optical' in prop for prop in drive_props):
                            self.media_path_combobox.addItem(device_props.Get('org.freedesktop.UDisks.Device',
                                                                              'DeviceFile'))
                return
            except dbus.exceptions.DBusException:
                log.debug('could not use udisks, will try udisks2')
            udev_manager_obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
            udev_manager = dbus.Interface(udev_manager_obj, 'org.freedesktop.DBus.ObjectManager')
            for k, v in udev_manager.GetManagedObjects().items():
                drive_info = v.get('org.freedesktop.UDisks2.Drive', {})
                drive_props = drive_info.get('MediaCompatibility')
                if drive_props and any('optical' in prop for prop in drive_props):
                    for device in udev_manager.GetManagedObjects().values():
                        if dbus.String('org.freedesktop.UDisks2.Block') in device:
                            if device[dbus.String('org.freedesktop.UDisks2.Block')][dbus.String('Drive')] == k:
                                block_file = ''
                                for c in device[dbus.String('org.freedesktop.UDisks2.Block')][
                                        dbus.String('PreferredDevice')]:
                                    if chr(c) != '\x00':
                                        block_file += chr(c)
                                self.media_path_combobox.addItem(block_file)
        elif is_macosx():
            # Look for DVD folders in devices to find optical devices
            volumes = os.listdir('/Volumes')
            candidates = list()
            for volume in volumes:
                if volume.startswith('.'):
                    continue
                dirs = os.listdir('/Volumes/' + volume)
                # Detect DVD
                if 'VIDEO_TS' in dirs:
                    self.media_path_combobox.addItem('/Volumes/' + volume)
                # Detect audio cd
                files = [f for f in dirs if os.path.isfile(f)]
                for file in files:
                    if file.endswith('aiff'):
                        self.media_path_combobox.addItem('/Volumes/' + volume)
                        break
