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
The :mod:`~openlp.core.ui.media.mediacontroller` module contains a base class for media components and other widgets
related to playing media, such as sliders.
"""
import logging
import os
import datetime
from PyQt4 import QtCore, QtGui

from openlp.core.common import OpenLPMixin, Registry, RegistryMixin, RegistryProperties, Settings, UiStrings, translate
from openlp.core.lib import OpenLPToolbar, ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.media import MediaState, MediaInfo, MediaType, get_media_players, set_media_players,\
    parse_optical_path
from openlp.core.ui.media.mediaplayer import MediaPlayer
from openlp.core.common import AppLocation
from openlp.core.ui import DisplayControllerType

log = logging.getLogger(__name__)


class MediaSlider(QtGui.QSlider):
    """
    Allows the mouse events of a slider to be overridden and extra functionality added
    """
    def __init__(self, direction, manager, controller):
        """
        Constructor
        """
        super(MediaSlider, self).__init__(direction)
        self.manager = manager
        self.controller = controller

    def mouseMoveEvent(self, event):
        """
        Override event to allow hover time to be displayed.
        """
        time_value = QtGui.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
        self.setToolTip('%s' % datetime.timedelta(seconds=int(time_value / 1000)))
        QtGui.QSlider.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        """
        Mouse Press event no new functionality
        """
        QtGui.QSlider.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Set the slider position when the mouse is clicked and released on the slider.
        """
        self.setValue(QtGui.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))
        QtGui.QSlider.mouseReleaseEvent(self, event)


class MediaController(RegistryMixin, OpenLPMixin, RegistryProperties):
    """
    The implementation of the Media Controller. The Media Controller adds an own class for every Player.
    Currently these are QtWebkit, Phonon and Vlc. display_controllers are an array of controllers keyed on the
    slidecontroller or plugin which built them.

    ControllerType is the class containing the key values.

    media_players are an array of media players keyed on player name.

    current_media_players is an array of player instances keyed on ControllerType.

    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(MediaController, self).__init__(parent)
        self.media_players = {}
        self.display_controllers = {}
        self.current_media_players = {}
        # Timer for video state
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        # Signals
        self.timer.timeout.connect(self.media_state)
        Registry().register_function('playbackPlay', self.media_play_msg)
        Registry().register_function('playbackPause', self.media_pause_msg)
        Registry().register_function('playbackStop', self.media_stop_msg)
        Registry().register_function('seek_slider', self.media_seek_msg)
        Registry().register_function('volume_slider', self.media_volume_msg)
        Registry().register_function('media_hide', self.media_hide)
        Registry().register_function('media_blank', self.media_blank)
        Registry().register_function('media_unblank', self.media_unblank)
        # Signals for background video
        Registry().register_function('songs_hide', self.media_hide)
        Registry().register_function('songs_unblank', self.media_unblank)
        Registry().register_function('mediaitem_media_rebuild', self._set_active_players)
        Registry().register_function('mediaitem_suffixes', self._generate_extensions_lists)

    def _set_active_players(self):
        """
        Set the active players and available media files
        """
        saved_players = get_media_players()[0]
        for player in list(self.media_players.keys()):
            self.media_players[player].is_active = player in saved_players

    def _generate_extensions_lists(self):
        """
        Set the active players and available media files
        """
        suffix_list = []
        self.audio_extensions_list = []
        for player in list(self.media_players.values()):
            if player.is_active:
                for item in player.audio_extensions_list:
                    if item not in self.audio_extensions_list:
                        self.audio_extensions_list.append(item)
                        suffix_list.append(item[2:])
        self.video_extensions_list = []
        for player in list(self.media_players.values()):
            if player.is_active:
                for item in player.video_extensions_list:
                    if item not in self.video_extensions_list:
                        self.video_extensions_list.append(item)
                        suffix_list.append(item[2:])
        self.service_manager.supported_suffixes(suffix_list)

    def register_players(self, player):
        """
        Register each media Player (Webkit, Phonon, etc) and store
        for later use

        :param player: Individual player class which has been enabled
        """
        self.media_players[player.name] = player

    def bootstrap_initialise(self):
        """
        Check to see if we have any media Player's available.
        """
        log.debug('_check_available_media_players')
        controller_dir = os.path.join(AppLocation.get_directory(AppLocation.AppDir), 'core', 'ui', 'media')
        for filename in os.listdir(controller_dir):
            if filename.endswith('player.py') and not filename == 'mediaplayer.py':
                path = os.path.join(controller_dir, filename)
                if os.path.isfile(path):
                    module_name = 'openlp.core.ui.media.' + os.path.splitext(filename)[0]
                    log.debug('Importing controller %s', module_name)
                    try:
                        __import__(module_name, globals(), locals(), [])
                    # On some platforms importing vlc.py might cause
                    # also OSError exceptions. (e.g. Mac OS X)
                    except (ImportError, OSError):
                        log.warning('Failed to import %s on path %s', module_name, path)
        player_classes = MediaPlayer.__subclasses__()
        for player_class in player_classes:
            player = player_class(self)
            self.register_players(player)
        if not self.media_players:
            return False
        saved_players, overridden_player = get_media_players()
        invalid_media_players = \
            [media_player for media_player in saved_players if media_player not in self.media_players or
                not self.media_players[media_player].check_available()]
        if invalid_media_players:
            for invalidPlayer in invalid_media_players:
                saved_players.remove(invalidPlayer)
            set_media_players(saved_players, overridden_player)
        self._set_active_players()
        self._generate_extensions_lists()
        return True

    def media_state(self):
        """
        Check if there is a running media Player and do updating stuff (e.g. update the UI)
        """
        if not list(self.current_media_players.keys()):
            self.timer.stop()
        else:
            any_active = False
            for source in list(self.current_media_players.keys()):
                display = self._define_display(self.display_controllers[source])
                self.current_media_players[source].resize(display)
                self.current_media_players[source].update_ui(display)
                if self.current_media_players[source].state == MediaState.Playing:
                    any_active = True
        # There are still any active players - no need to stop timer.
            if any_active:
                return
        # no players are active anymore
        for source in list(self.current_media_players.keys()):
            if self.current_media_players[source].state != MediaState.Paused:
                display = self._define_display(self.display_controllers[source])
                display.controller.seek_slider.setSliderPosition(0)
                display.controller.mediabar.actions['playbackPlay'].setVisible(True)
                display.controller.mediabar.actions['playbackPause'].setVisible(False)
        self.timer.stop()

    def get_media_display_css(self):
        """
        Add css style sheets to htmlbuilder
        """
        css = ''
        for player in list(self.media_players.values()):
            if player.is_active:
                css += player.get_media_display_css()
        return css

    def get_media_display_javascript(self):
        """
        Add javascript functions to htmlbuilder
        """
        js = ''
        for player in list(self.media_players.values()):
            if player.is_active:
                js += player.get_media_display_javascript()
        return js

    def get_media_display_html(self):
        """
        Add html code to htmlbuilder
        """
        html = ''
        for player in list(self.media_players.values()):
            if player.is_active:
                html += player.get_media_display_html()
        return html

    def register_controller(self, controller):
        """
        Registers media controls where the players will be placed to run.

        :param controller: The controller where a player will be placed
        """
        self.display_controllers[controller.controller_type] = controller
        self.setup_generic_controls(controller)

    def setup_generic_controls(self, controller):
        """
        Set up controls on the control_panel for a given controller

        :param controller:  First element is the controller which should be used
        """
        controller.media_info = MediaInfo()
        # Build a Media ToolBar
        controller.mediabar = OpenLPToolbar(controller)
        controller.mediabar.add_toolbar_action('playbackPlay', text='media_playback_play',
                                               icon=':/slides/media_playback_start.png',
                                               tooltip=translate('OpenLP.SlideController', 'Start playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.mediabar.add_toolbar_action('playbackPause', text='media_playback_pause',
                                               icon=':/slides/media_playback_pause.png',
                                               tooltip=translate('OpenLP.SlideController', 'Pause playing media.'),
                                               triggers=controller.send_to_plugins)
        controller.mediabar.add_toolbar_action('playbackStop', text='media_playback_stop',
                                               icon=':/slides/media_playback_stop.png',
                                               tooltip=translate('OpenLP.SlideController', 'Stop playing media.'),
                                               triggers=controller.send_to_plugins)
        # Build the seek_slider.
        controller.seek_slider = MediaSlider(QtCore.Qt.Horizontal, self, controller)
        controller.seek_slider.setMaximum(1000)
        controller.seek_slider.setTracking(True)
        controller.seek_slider.setMouseTracking(True)
        controller.seek_slider.setToolTip(translate('OpenLP.SlideController', 'Video position.'))
        controller.seek_slider.setGeometry(QtCore.QRect(90, 260, 221, 24))
        controller.seek_slider.setObjectName('seek_slider')
        controller.mediabar.add_toolbar_widget(controller.seek_slider)
        # Build the volume_slider.
        controller.volume_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        controller.volume_slider.setTickInterval(10)
        controller.volume_slider.setTickPosition(QtGui.QSlider.TicksAbove)
        controller.volume_slider.setMinimum(0)
        controller.volume_slider.setMaximum(100)
        controller.volume_slider.setTracking(True)
        controller.volume_slider.setToolTip(translate('OpenLP.SlideController', 'Audio Volume.'))
        controller.volume_slider.setValue(controller.media_info.volume)
        controller.volume_slider.setGeometry(QtCore.QRect(90, 160, 221, 24))
        controller.volume_slider.setObjectName('volume_slider')
        controller.mediabar.add_toolbar_widget(controller.volume_slider)
        controller.controller_layout.addWidget(controller.mediabar)
        controller.mediabar.setVisible(False)
        # Signals
        controller.seek_slider.valueChanged.connect(controller.send_to_plugins)
        controller.volume_slider.valueChanged.connect(controller.send_to_plugins)

    def setup_display(self, display, preview):
        """
        After a new display is configured, all media related widgets will be created too

        :param display:  Display on which the output is to be played
        :param preview: Whether the display is a main or preview display
        """
        # clean up possible running old media files
        self.finalise()
        # update player status
        self._set_active_players()
        display.has_audio = True
        if display.is_live and preview:
            return
        if preview:
            display.has_audio = False
        for player in list(self.media_players.values()):
            if player.is_active:
                player.setup(display)

    def set_controls_visible(self, controller, value):
        """
        After a new display is configured, all media related widget will be created too

        :param controller: The controller on which controls act.
        :param value: control name to be changed.
        """
        # Generic controls
        controller.mediabar.setVisible(value)
        if controller.is_live and controller.display:
            if self.current_media_players and value:
                if self.current_media_players[controller.controller_type] != self.media_players['webkit']:
                    controller.display.set_transparency(False)

    def resize(self, display, player):
        """
        After Mainwindow changes or Splitter moved all related media widgets have to be resized

        :param display: The display on which output is playing.
        :param player:  The player which is doing the playing.
        """
        player.resize(display)

    def video(self, source, service_item, hidden=False, video_behind_text=False):
        """
        Loads and starts a video to run with the option of sound

        :param source: Where the call originated form
        :param service_item: The player which is doing the playing
        :param hidden: The player which is doing the playing
        :param video_behind_text: Is the video to be played behind text.
        """
        log.debug('video')
        is_valid = False
        controller = self.display_controllers[source]
        # stop running videos
        self.media_reset(controller)
        controller.media_info = MediaInfo()
        controller.media_info.volume = controller.volume_slider.value()
        controller.media_info.is_background = video_behind_text
        controller.media_info.file_info = QtCore.QFileInfo(service_item.get_frame_path())
        display = self._define_display(controller)
        if controller.is_live:
            # if this is an optical device use special handling
            if service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and live')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and live')
                is_valid = self._check_file_type(controller, display, service_item)
            display.override['theme'] = ''
            display.override['video'] = True
            if controller.media_info.is_background:
                # ignore start/end time
                controller.media_info.start_time = 0
                controller.media_info.end_time = 0
            else:
                controller.media_info.start_time = service_item.start_time
                controller.media_info.end_time = service_item.end_time
        elif controller.preview_display:
            if service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and preview')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and preview')
                is_valid = self._check_file_type(controller, display, service_item)
        if not is_valid:
            # Media could not be loaded correctly
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        log.debug('video mediatype: ' + str(controller.media_info.media_type))
        # dont care about actual theme, set a black background
        if controller.is_live and not controller.media_info.is_background:
            display.frame.evaluateJavaScript('show_video( "setBackBoard", null, null, null,"visible");')
        # now start playing - Preview is autoplay!
        autoplay = False
        # Preview requested
        if not controller.is_live:
            autoplay = True
        # Visible or background requested or Service Item wants to autostart
        elif not hidden or controller.media_info.is_background or service_item.will_auto_start:
            autoplay = True
        # Unblank on load set
        elif Settings().value('core/auto unblank'):
            autoplay = True
        if autoplay:
            if not self.media_play(controller):
                critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                           translate('MediaPlugin.MediaItem', 'Unsupported File'))
                return False
        self.set_controls_visible(controller, True)
        log.debug('use %s controller' % self.current_media_players[controller.controller_type])
        return True

    def media_length(self, service_item):
        """
        Loads and starts a media item to obtain the media length

        :param service_item: The ServiceItem containing the details to be played.
        """
        controller = self.display_controllers[DisplayControllerType.Plugin]
        log.debug('media_length')
        # stop running videos
        self.media_reset(controller)
        controller.media_info = MediaInfo()
        controller.media_info.volume = 0
        controller.media_info.file_info = QtCore.QFileInfo(service_item.get_frame_path())
        display = controller.preview_display
        if not self._check_file_type(controller, display, service_item):
            # Media could not be loaded correctly
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        if not self.media_play(controller):
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        service_item.set_media_length(controller.media_info.length)
        self.media_stop(controller)
        log.debug('use %s controller' % self.current_media_players[controller.controller_type])
        return True

    def media_setup_optical(self, filename, title, audio_track, subtitle_track, start, end, display, controller):
        """
        Setup playback of optical media

        :param filename: Path of the optical device/drive.
        :param title: The main/title track to play.
        :param audio_track: The audio track to play.
        :param subtitle_track: The subtitle track to play.
        :param start: Start position in miliseconds.
        :param end: End position in miliseconds.
        :param display: The display to play the media.
        :param controller: The media contraoller.
        :return: True if setup succeded else False.
        """
        log.debug('media_setup_optical')
        if controller is None:
            controller = self.display_controllers[DisplayControllerType.Plugin]
        # stop running videos
        self.media_reset(controller)
        # Setup media info
        controller.media_info = MediaInfo()
        controller.media_info.file_info = QtCore.QFileInfo(filename)
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        controller.media_info.start_time = start/1000
        controller.media_info.end_time = end/1000
        controller.media_info.length = (end - start)/1000
        controller.media_info.title_track = title
        controller.media_info.audio_track = audio_track
        controller.media_info.subtitle_track = subtitle_track
        # When called from mediaitem display is None
        if display is None:
            display = controller.preview_display
        # Find vlc player
        used_players = get_media_players()[0]
        vlc_player = None
        for title in used_players:
            player = self.media_players[title]
            if player.name == 'vlc':
                vlc_player = player
        if vlc_player is None:
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'VLC player required'),
                                       translate('MediaPlugin.MediaItem',
                                                 'VLC player required for playback of optical devices'))
            return False
        vlc_player.load(display)
        self.resize(display, vlc_player)
        self.current_media_players[controller.controller_type] = vlc_player
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        return True

    def _check_file_type(self, controller, display, service_item):
        """
        Select the correct media Player type from the prioritized Player list

        :param controller: First element is the controller which should be used
        :param display: Which display to use
        :param service_item: The ServiceItem containing the details to be played.
        """
        used_players = get_media_players()[0]
        if service_item.processor and service_item.processor != UiStrings().Automatic:
            used_players = [service_item.processor.lower()]
        # If no player, we can't play
        if not used_players:
            return False
        if controller.media_info.file_info.isFile():
            suffix = '*.%s' % controller.media_info.file_info.suffix().lower()
            for title in used_players:
                if not title:
                    continue
                player = self.media_players[title]
                if suffix in player.video_extensions_list:
                    if not controller.media_info.is_background or controller.media_info.is_background and \
                            player.can_background:
                        self.resize(display, player)
                        if player.load(display):
                            self.current_media_players[controller.controller_type] = player
                            controller.media_info.media_type = MediaType.Video
                            return True
                if suffix in player.audio_extensions_list:
                    if player.load(display):
                        self.current_media_players[controller.controller_type] = player
                        controller.media_info.media_type = MediaType.Audio
                        return True
        else:
            for title in used_players:
                player = self.media_players[title]
                if player.can_folder:
                    self.resize(display, player)
                    if player.load(display):
                        self.current_media_players[controller.controller_type] = player
                        controller.media_info.media_type = MediaType.Video
                        return True
        # no valid player found
        return False

    def media_play_msg(self, msg, status=True):
        """
        Responds to the request to play a loaded video

        :param msg: First element is the controller which should be used
        :param status:
        """
        log.debug('media_play_msg')
        self.media_play(msg[0], status)

    def media_play(self, controller, status=True):
        """
        Responds to the request to play a loaded video

        :param controller: The controller to be played
        :param status:
        """
        log.debug('media_play')
        controller.seek_slider.blockSignals(True)
        controller.volume_slider.blockSignals(True)
        display = self._define_display(controller)
        if not self.current_media_players[controller.controller_type].play(display):
            controller.seek_slider.blockSignals(False)
            controller.volume_slider.blockSignals(False)
            return False
        if controller.media_info.is_background:
            self.media_volume(controller, 0)
        else:
            self.media_volume(controller, controller.media_info.volume)
        if status:
            if not controller.media_info.is_background:
                display.frame.evaluateJavaScript('show_blank("desktop");')
            self.current_media_players[controller.controller_type].set_visible(display, True)
            # Flash needs to be played and will not AutoPlay
            if controller.media_info.is_flash:
                controller.mediabar.actions['playbackPlay'].setVisible(True)
                controller.mediabar.actions['playbackPause'].setVisible(False)
            else:
                controller.mediabar.actions['playbackPlay'].setVisible(False)
                controller.mediabar.actions['playbackPause'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(False)
            if controller.is_live:
                if controller.hide_menu.defaultAction().isChecked() and not controller.media_info.is_background:
                    controller.hide_menu.defaultAction().trigger()
        # Start Timer for ui updates
        if not self.timer.isActive():
            self.timer.start()
        controller.seek_slider.blockSignals(False)
        controller.volume_slider.blockSignals(False)
        return True

    def media_pause_msg(self, msg):
        """
        Responds to the request to pause a loaded video

        :param msg: First element is the controller which should be used
        """
        log.debug('media_pause_msg')
        self.media_pause(msg[0])

    def media_pause(self, controller):
        """
        Responds to the request to pause a loaded video

        :param controller: The Controller to be paused
        """
        log.debug('media_pause')
        display = self._define_display(controller)
        self.current_media_players[controller.controller_type].pause(display)
        controller.mediabar.actions['playbackPlay'].setVisible(True)
        controller.mediabar.actions['playbackStop'].setDisabled(False)
        controller.mediabar.actions['playbackPause'].setVisible(False)

    def media_stop_msg(self, msg):
        """
        Responds to the request to stop a loaded video

        :param msg: First element is the controller which should be used
        """
        log.debug('media_stop_msg')
        self.media_stop(msg[0])

    def media_stop(self, controller):
        """
        Responds to the request to stop a loaded video

        :param controller: The controller that needs to be stopped
        """
        log.debug('media_stop')
        display = self._define_display(controller)
        if controller.controller_type in self.current_media_players:
            display.frame.evaluateJavaScript('show_blank("black");')
            self.current_media_players[controller.controller_type].stop(display)
            self.current_media_players[controller.controller_type].set_visible(display, False)
            controller.seek_slider.setSliderPosition(0)
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(True)
            controller.mediabar.actions['playbackPause'].setVisible(False)

    def media_volume_msg(self, msg):
        """
        Changes the volume of a running video

        :param msg: First element is the controller which should be used
        """
        controller = msg[0]
        vol = msg[1][0]
        self.media_volume(controller, vol)

    def media_volume(self, controller, volume):
        """
        Changes the volume of a running video

        :param controller: The Controller to use
        :param volume: The volume to be set
        """
        log.debug('media_volume %d' % volume)
        display = self._define_display(controller)
        self.current_media_players[controller.controller_type].volume(display, volume)
        controller.volume_slider.setValue(volume)

    def media_seek_msg(self, msg):
        """
        Responds to the request to change the seek Slider of a loaded video via a message

        :param msg: First element is the controller which should be used
            Second element is a list with the seek value as first element
        """
        log.debug('media_seek')
        controller = msg[0]
        seek_value = msg[1][0]
        self.media_seek(controller, seek_value)

    def media_seek(self, controller, seek_value):
        """
        Responds to the request to change the seek Slider of a loaded video

        :param controller: The controller to use.
        :param seek_value: The value to set.
        """
        log.debug('media_seek')
        display = self._define_display(controller)
        self.current_media_players[controller.controller_type].seek(display, seek_value)

    def media_reset(self, controller):
        """
        Responds to the request to reset a loaded video
        """
        log.debug('media_reset')
        self.set_controls_visible(controller, False)
        display = self._define_display(controller)
        if controller.controller_type in self.current_media_players:
            display.override = {}
            self.current_media_players[controller.controller_type].reset(display)
            self.current_media_players[controller.controller_type].set_visible(display, False)
            display.frame.evaluateJavaScript('show_video( "setBackBoard", null, null, null,"hidden");')
            del self.current_media_players[controller.controller_type]

    def media_hide(self, msg):
        """
        Hide the related video Widget

        :param msg: First element is the boolean for Live indication
        """
        is_live = msg[1]
        if not is_live:
            return
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].state == MediaState.Playing:
            self.current_media_players[self.live_controller.controller_type].pause(display)
            self.current_media_players[self.live_controller.controller_type].set_visible(display, False)

    def media_blank(self, msg):
        """
        Blank the related video Widget

        :param msg: First element is the boolean for Live indication
            Second element is the hide mode
        """
        is_live = msg[1]
        hide_mode = msg[2]
        if not is_live:
            return
        Registry().execute('live_display_hide', hide_mode)
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].state == MediaState.Playing:
            self.current_media_players[self.live_controller.controller_type].pause(display)
            self.current_media_players[self.live_controller.controller_type].set_visible(display, False)

    def media_unblank(self, msg):
        """
        Unblank the related video Widget

        :param msg: First element is not relevant in this context
            Second element is the boolean for Live indication
        """
        Registry().execute('live_display_show')
        is_live = msg[1]
        if not is_live:
            return
        display = self._define_display(self.live_controller)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].state != MediaState.Playing:
            if self.current_media_players[self.live_controller.controller_type].play(display):
                self.current_media_players[self.live_controller.controller_type].set_visible(display, True)
                # Start Timer for ui updates
                if not self.timer.isActive():
                    self.timer.start()

    def finalise(self):
        """
        Reset all the media controllers when OpenLP shuts down
        """
        self.timer.stop()
        for controller in self.display_controllers:
            self.media_reset(self.display_controllers[controller])

    def _define_display(self, controller):
        """
        Extract the correct display for a given controller

        :param controller:  Controller to be used
        """
        if controller.is_live:
            return controller.display
        return controller.preview_display
