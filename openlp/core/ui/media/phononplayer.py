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
The :mod:`~openlp.core.ui.media.phononplayer` contains the Phonon player component.
"""
import logging
import mimetypes
from datetime import datetime

from PyQt4.phonon import Phonon

from openlp.core.lib import translate

from openlp.core.ui.media import MediaState
from openlp.core.ui.media.mediaplayer import MediaPlayer
from openlp.core.common import is_macosx


log = logging.getLogger(__name__)

ADDITIONAL_EXT = {
    'audio/ac3': ['.ac3'],
    'audio/flac': ['.flac'],
    'audio/x-m4a': ['.m4a'],
    'audio/midi': ['.mid', '.midi'],
    'audio/x-mp3': ['.mp3'],
    'audio/mpeg': ['.mp3', '.mp2', '.mpga', '.mpega', '.m4a'],
    'audio/qcelp': ['.qcp'],
    'audio/x-wma': ['.wma'],
    'audio/x-ms-wma': ['.wma'],
    'video/x-flv': ['.flv'],
    'video/x-matroska': ['.mpv', '.mkv'],
    'video/x-wmv': ['.wmv'],
    'video/x-mpg': ['.mpg'],
    'video/mpeg': ['.mp4', '.mts', '.mov'],
    'video/x-ms-wmv': ['.wmv']
}


class PhononPlayer(MediaPlayer):
    """
    A specialised version of the MediaPlayer class, which provides a Phonon display.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(PhononPlayer, self).__init__(parent, 'phonon')
        self.original_name = 'Phonon'
        self.display_name = '&Phonon'
        self.parent = parent
        self.additional_extensions = ADDITIONAL_EXT
        mimetypes.init()
        for mime_type in Phonon.BackendCapabilities.availableMimeTypes():
            mime_type = str(mime_type)
            if mime_type.startswith('audio/'):
                self._add_to_list(self.audio_extensions_list, mime_type)
            elif mime_type.startswith('video/'):
                self._add_to_list(self.video_extensions_list, mime_type)

    def _add_to_list(self, mime_type_list, mimetype):
        """
        Add mimetypes to the provided list
        """
        # Add all extensions which mimetypes provides us for supported types.
        extensions = mimetypes.guess_all_extensions(str(mimetype))
        for extension in extensions:
            ext = '*%s' % extension
            if ext not in mime_type_list:
                mime_type_list.append(ext)
        log.info('MediaPlugin: %s extensions: %s' % (mimetype, ' '.join(extensions)))
        # Add extensions for this mimetype from self.additional_extensions.
        # This hack clears mimetypes' and operating system's shortcomings
        # by providing possibly missing extensions.
        if mimetype in list(self.additional_extensions.keys()):
            for extension in self.additional_extensions[mimetype]:
                ext = '*%s' % extension
                if ext not in mime_type_list:
                    mime_type_list.append(ext)
            log.info('MediaPlugin: %s additional extensions: %s' %
                     (mimetype, ' '.join(self.additional_extensions[mimetype])))

    def setup(self, display):
        """
        Set up the player widgets
        """
        display.phonon_widget = Phonon.VideoWidget(display)
        display.phonon_widget.resize(display.size())
        display.media_object = Phonon.MediaObject(display)
        Phonon.createPath(display.media_object, display.phonon_widget)
        if display.has_audio:
            display.audio = Phonon.AudioOutput(Phonon.VideoCategory, display.media_object)
            Phonon.createPath(display.media_object, display.audio)
        display.phonon_widget.raise_()
        display.phonon_widget.hide()
        self.has_own_widget = True

    def check_available(self):
        """
        Check if the player is available
        """
        # At the moment we don't have support for phononplayer on Mac OS X
        if is_macosx():
            return False
        else:
            return True

    def load(self, display):
        """
        Load a video into the display
        """
        log.debug('load vid in Phonon Controller')
        controller = display.controller
        volume = controller.media_info.volume
        path = controller.media_info.file_info.absoluteFilePath()
        display.media_object.setCurrentSource(Phonon.MediaSource(path))
        if not self.media_state_wait(display, Phonon.StoppedState):
            return False
        self.volume(display, volume)
        return True

    def media_state_wait(self, display, media_state):
        """
        Wait for the video to change its state
        Wait no longer than 5 seconds.
        """
        start = datetime.now()
        current_state = display.media_object.state()
        while current_state != media_state:
            current_state = display.media_object.state()
            if current_state == Phonon.ErrorState:
                return False
            self.application.process_events()
            if (datetime.now() - start).seconds > 5:
                return False
        return True

    def resize(self, display):
        """
        Resize the display
        """
        display.phonon_widget.resize(display.size())

    def play(self, display):
        """
        Play the current media item
        """
        controller = display.controller
        start_time = 0
        if display.media_object.state() != Phonon.PausedState and controller.media_info.start_time > 0:
            start_time = controller.media_info.start_time
        display.media_object.play()
        if not self.media_state_wait(display, Phonon.PlayingState):
            return False
        if start_time > 0:
            self.seek(display, controller.media_info.start_time * 1000)
        self.volume(display, controller.media_info.volume)
        controller.media_info.length = int(display.media_object.totalTime() / 1000)
        controller.seek_slider.setMaximum(controller.media_info.length * 1000)
        self.state = MediaState.Playing
        display.phonon_widget.raise_()
        return True

    def pause(self, display):
        """
        Pause the current media item
        """
        display.media_object.pause()
        if self.media_state_wait(display, Phonon.PausedState):
            self.state = MediaState.Paused

    def stop(self, display):
        """
        Stop the current media item
        """
        display.media_object.stop()
        self.set_visible(display, False)
        self.state = MediaState.Stopped

    def volume(self, display, vol):
        """
        Set the volume
        """
        # 1.0 is the highest value
        if display.has_audio:
            vol = float(vol) / float(100)
            display.audio.setVolume(vol)

    def seek(self, display, seek_value):
        """
        Go to a particular point in the current media item
        """
        display.media_object.seek(seek_value)

    def reset(self, display):
        """
        Reset the media player
        """
        display.media_object.stop()
        display.media_object.clearQueue()
        self.set_visible(display, False)
        display.phonon_widget.setVisible(False)
        self.state = MediaState.Off

    def set_visible(self, display, status):
        """
        Set the visibility of the widget
        """
        if self.has_own_widget:
            display.phonon_widget.setVisible(status)

    def update_ui(self, display):
        """
        Update the UI
        """
        if display.media_object.state() == Phonon.PausedState and self.state != MediaState.Paused:
            self.stop(display)
        controller = display.controller
        if controller.media_info.end_time > 0:
            if display.media_object.currentTime() > controller.media_info.end_time * 1000:
                self.stop(display)
                self.set_visible(display, False)
        if not controller.seek_slider.isSliderDown():
            controller.seek_slider.blockSignals(True)
            controller.seek_slider.setSliderPosition(display.media_object.currentTime())
            controller.seek_slider.blockSignals(False)

    def get_media_display_css(self):
        """
        Add css style sheets to htmlbuilder
        """
        return ''

    def get_info(self):
        """
        Return some info about this player
        """
        return(translate('Media.player', 'Phonon is a media player which '
               'interacts with the operating system to provide media capabilities.') +
               '<br/> <strong>' + translate('Media.player', 'Audio') +
               '</strong><br/>' + str(self.audio_extensions_list) +
               '<br/><strong>' + translate('Media.player', 'Video') +
               '</strong><br/>' + str(self.video_extensions_list) + '<br/>')
