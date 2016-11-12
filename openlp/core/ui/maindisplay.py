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
The :mod:`maindisplay` module provides the functionality to display screens and play multimedia within OpenLP.

Some of the code for this form is based on the examples at:

* `http://www.steveheffernan.com/html5-video-player/demo-video-player.html`_
* `http://html5demos.com/two-videos`_

"""

import html
import logging

from PyQt4 import QtCore, QtGui, QtWebKit, QtOpenGL

PHONON_AVAILABLE = True
try:
    from PyQt4.phonon import Phonon
except ImportError:
    PHONON_AVAILABLE = False

from openlp.core.common import Registry, RegistryProperties, OpenLPMixin, Settings, translate, is_macosx
from openlp.core.lib import ServiceItem, ImageSource, ScreenList, build_html, expand_tags, image_to_byte
from openlp.core.lib.theme import BackgroundType
from openlp.core.ui import HideMode, AlertLocation

log = logging.getLogger(__name__)

OPAQUE_STYLESHEET = """
QWidget {
    border: 0px;
    margin: 0px;
    padding: 0px;
}
QGraphicsView {}
"""
TRANSPARENT_STYLESHEET = """
QWidget {
    border: 0px;
    margin: 0px;
    padding: 0px;
}
QGraphicsView {
    background: transparent;
    border: 0px;
}
"""


class Display(QtGui.QGraphicsView):
    """
    This is a general display screen class. Here the general display settings will done. It will be used as
    specialized classes by Main Display and Preview display.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.is_live = False
        if hasattr(parent, 'is_live') and parent.is_live:
            self.is_live = True
        if self.is_live:
            self.parent = lambda: parent
        super(Display, self).__init__()
        self.controller = parent
        self.screen = {}
        # FIXME: On Mac OS X (tested on 10.7) the display screen is corrupt with
        # OpenGL. Only white blank screen is shown on the 2nd monitor all the
        # time. We need to investigate more how to use OpenGL properly on Mac OS
        # X.
        if not is_macosx():
            self.setViewport(QtOpenGL.QGLWidget())

    def setup(self):
        """
        Set up and build the screen base
        """
        self.setGeometry(self.screen['size'])
        self.web_view = QtWebKit.QWebView(self)
        self.web_view.setGeometry(0, 0, self.screen['size'].width(), self.screen['size'].height())
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        palette = self.web_view.palette()
        palette.setBrush(QtGui.QPalette.Base, QtCore.Qt.transparent)
        self.web_view.page().setPalette(palette)
        self.web_view.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
        self.page = self.web_view.page()
        self.frame = self.page.mainFrame()
        if self.is_live and log.getEffectiveLevel() == logging.DEBUG:
            self.web_view.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.web_view.loadFinished.connect(self.is_web_loaded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        self.frame.setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        """
        React to resizing of this display

        :param event: The event to be handled
        """
        self.web_view.setGeometry(0, 0, self.width(), self.height())

    def is_web_loaded(self, field=None):
        """
        Called by webView event to show display is fully loaded
        """
        self.web_loaded = True


class MainDisplay(OpenLPMixin, Display, RegistryProperties):
    """
    This is the display screen as a specialized class from the Display class
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(MainDisplay, self).__init__(parent)
        self.screens = ScreenList()
        self.rebuild_css = False
        self.hide_mode = None
        self.override = {}
        self.retranslateUi()
        self.media_object = None
        if self.is_live and PHONON_AVAILABLE:
            self.audio_player = AudioPlayer(self)
        else:
            self.audio_player = None
        self.first_time = True
        self.web_loaded = True
        #self.setStyleSheet(OPAQUE_STYLESHEET)
        self.setStyleSheet(TRANSPARENT_STYLESHEET)
        window_flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint
        if Settings().value('advanced/x11 bypass wm'):
            window_flags |= QtCore.Qt.X11BypassWindowManagerHint
        # TODO: The following combination of window_flags works correctly
        # on Mac OS X. For next OpenLP version we should test it on other
        # platforms. For OpenLP 2.0 keep it only for OS X to not cause any
        # regressions on other platforms.
        if is_macosx():
            window_flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window
            # For primary screen ensure it stays above the OS X dock
            # and menu bar
            if self.screens.current['primary']:
                self.setWindowState(QtCore.Qt.WindowFullScreen)
            else:
                window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.set_transparency(False)
        self.set_transparency(True)
        if self.is_live:
            Registry().register_function('live_display_hide', self.hide_display)
            Registry().register_function('live_display_show', self.show_display)
            Registry().register_function('update_display_css', self.css_changed)

    def close(self):
        """
        Remove registered function on close.
        """
        if self.is_live:
            Registry().remove_function('live_display_hide', self.hide_display)
            Registry().remove_function('live_display_show', self.show_display)
            Registry().remove_function('update_display_css', self.css_changed)
        super().close()

    def set_transparency(self, enabled):
        """
        Set the transparency of the window

        :param enabled: Is transparency enabled
        """
        if enabled:
            self.setAutoFillBackground(False)
            self.setStyleSheet(TRANSPARENT_STYLESHEET)
        else:
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
            self.setStyleSheet(OPAQUE_STYLESHEET)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, enabled)
        self.repaint()

    def css_changed(self):
        """
        We need to rebuild the CSS on the live display.
        """
        for plugin in self.plugin_manager.plugins:
            plugin.refresh_css(self.frame)

    def retranslateUi(self):
        """
        Setup the interface translation strings.
        """
        self.setWindowTitle(translate('OpenLP.MainDisplay', 'OpenLP Display'))

    def setup(self):
        """
        Set up and build the output screen
        """
        self.log_debug('Start MainDisplay setup (live = %s)' % self.is_live)
        self.screen = self.screens.current
        self.setVisible(False)
        Display.setup(self)
        #if self.is_live:
        #    # Build the initial frame.
        #    background_color = QtGui.QColor()
        #    background_color.setNamedColor(Settings().value('advanced/default color'))
        #    if not background_color.isValid():
        #        background_color = QtCore.Qt.white
    #        image_file = Settings().value('advanced/default image')
    #        splash_image = QtGui.QImage(image_file)
    #        self.initial_fame = QtGui.QImage(
    #            self.screen['size'].width(),
    #            self.screen['size'].height(),
    #            QtGui.QImage.Format_ARGB32_Premultiplied)
    #        painter_image = QtGui.QPainter()
    #        painter_image.begin(self.initial_fame)
    #        painter_image.fillRect(self.initial_fame.rect(), background_color)
    #        painter_image.drawImage(
    #            (self.screen['size'].width() - splash_image.width()) // 2,
    #            (self.screen['size'].height() - splash_image.height()) // 2,
    #            splash_image)
    #        service_item = ServiceItem()
    #        service_item.bg_image_bytes = image_to_byte(self.initial_fame)
    #        self.web_view.setHtml(build_html(service_item, self.screen, self.is_live, None,
    #                              plugins=self.plugin_manager.plugins))
    #        self._hide_mouse()
    

    def text(self, slide, animate=True):
        """
        Add the slide text from slideController

        :param slide: The slide text to be displayed
        :param animate: Perform transitions if applicable when setting the text
        """
        # Wait for the webview to update before displaying text.
        while not self.web_loaded:
            self.application.process_events()
        self.setGeometry(self.screen['size'])
        if animate:
            self.frame.evaluateJavaScript('show_text("%s")' % slide.replace('\\', '\\\\').replace('\"', '\\\"'))
        else:
            # This exists for https://bugs.launchpad.net/openlp/+bug/1016843
            # For unknown reasons if evaluateJavaScript is called
            # from the themewizard, then it causes a crash on
            # Windows if there are many items in the service to re-render.
            # Setting the div elements direct seems to solve the issue
            self.frame.findFirstElement("#lyricsmain").setInnerXml(slide)

    def alert(self, text, location):
        """
        Display an alert.

        :param text: The text to be displayed.
        :param location: Where on the screen is the text to be displayed
        """
        # First we convert <>& marks to html variants, then apply
        # formattingtags, finally we double all backslashes for JavaScript.
        text_prepared = expand_tags(html.escape(text)).replace('\\', '\\\\').replace('\"', '\\\"')
        if self.height() != self.screen['size'].height() or not self.isVisible():
            shrink = True
            js = 'show_alert("%s", "%s")' % (text_prepared, 'top')
        else:
            shrink = False
            js = 'show_alert("%s", "")' % text_prepared
        height = self.frame.evaluateJavaScript(js)
        if shrink:
            if text:
                alert_height = int(height)
                self.resize(self.width(), alert_height)
                self.setVisible(True)
                if location == AlertLocation.Middle:
                    self.move(self.screen['size'].left(), (self.screen['size'].height() - alert_height) // 2)
                elif location == AlertLocation.Bottom:
                    self.move(self.screen['size'].left(), self.screen['size'].height() - alert_height)
            else:
                self.setVisible(False)
                self.setGeometry(self.screen['size'])

    def direct_image(self, path, background):
        """
        API for replacement backgrounds so Images are added directly to cache.

        :param path: Path to Image
        :param background: The background color
        """
        self.image_manager.add_image(path, ImageSource.ImagePlugin, background)
        if not hasattr(self, 'service_item'):
            return False
        self.override['image'] = path
        self.override['theme'] = self.service_item.theme_data.background_filename
        self.image(path)
        # Update the preview frame.
        if self.is_live:
            self.live_controller.update_preview()
        return True

    def image(self, path):
        """
        Add an image as the background. The image has already been added to the
        cache.

        :param path: The path to the image to be displayed. **Note**, the path is only passed to identify the image.
        If the image has changed it has to be re-added to the image manager.
        """
        image = self.image_manager.get_image_bytes(path, ImageSource.ImagePlugin)
        self.controller.media_controller.media_reset(self.controller)
        self.display_image(image)

    def display_image(self, image):
        """
        Display an image, as is.

        :param image: The image to be displayed
        """
        self.setGeometry(self.screen['size'])
        if image:
            js = 'show_image("data:image/png;base64,%s");' % image
        else:
            js = 'show_image("");'
        self.frame.evaluateJavaScript(js)

    def reset_image(self):
        """
        Reset the background image to the service item image. Used after the image plugin has changed the background.
        """
        if hasattr(self, 'service_item'):
            self.display_image(self.service_item.bg_image_bytes)
        else:
            self.display_image(None)
        # Update the preview frame.
        if self.is_live:
            self.live_controller.update_preview()
        # clear the cache
        self.override = {}

    def preview(self):
        """
        Generates a preview of the image displayed.
        """
        was_visible = self.isVisible()
        self.application.process_events()
        # We must have a service item to preview.
        if self.is_live and hasattr(self, 'service_item'):
            # Wait for the fade to finish before geting the preview.
            # Important otherwise preview will have incorrect text if at all!
            if self.service_item.theme_data and self.service_item.theme_data.display_slide_transition:
                while not self.frame.evaluateJavaScript('show_text_completed()'):
                    self.application.process_events()
        # Wait for the webview to update before getting the preview.
        # Important otherwise first preview will miss the background !
        while not self.web_loaded:
            self.application.process_events()
        # if was hidden keep it hidden
        if self.is_live:
            if self.hide_mode:
                self.hide_display(self.hide_mode)
            # Only continue if the visibility wasn't changed during method call.
            elif was_visible == self.isVisible():
                # Single screen active
                if self.screens.display_count == 1:
                    # Only make visible if setting enabled.
                    if Settings().value('core/display on monitor'):
                        self.setVisible(True)
                else:
                    self.setVisible(True)
        return QtGui.QPixmap.grabWidget(self)

    def build_html(self, service_item, image_path=''):
        """
        Store the service_item and build the new HTML from it. Add the HTML to the display

        :param service_item: The Service item to be used
        :param image_path: Where the image resides.
        """
        self.web_loaded = False
        self.initial_fame = None
        self.service_item = service_item
        background = None
        # We have an image override so keep the image till the theme changes.
        if self.override:
            # We have an video override so allow it to be stopped.
            if 'video' in self.override:
                Registry().execute('video_background_replaced')
                self.override = {}
            # We have a different theme.
            elif self.override['theme'] != service_item.theme_data.background_filename:
                Registry().execute('live_theme_changed')
                self.override = {}
            else:
                # replace the background
                background = self.image_manager.get_image_bytes(self.override['image'], ImageSource.ImagePlugin)
        self.set_transparency(self.service_item.theme_data.background_type ==
                              BackgroundType.to_string(BackgroundType.Transparent))
        if self.service_item.theme_data.background_filename:
            self.service_item.bg_image_bytes = self.image_manager.get_image_bytes(
                self.service_item.theme_data.background_filename, ImageSource.Theme)
        if image_path:
            image_bytes = self.image_manager.get_image_bytes(image_path, ImageSource.ImagePlugin)
        else:
            image_bytes = None
        html = build_html(self.service_item, self.screen, self.is_live, background, image_bytes,
                          plugins=self.plugin_manager.plugins)
        self.web_view.setHtml(html)
        if service_item.foot_text:
            self.footer(service_item.foot_text)
        # if was hidden keep it hidden
        if self.hide_mode and self.is_live and not service_item.is_media():
            if Settings().value('core/auto unblank'):
                Registry().execute('slidecontroller_live_unblank')
            else:
                self.hide_display(self.hide_mode)
        self._hide_mouse()

    def footer(self, text):
        """
        Display the Footer

        :param text: footer text to be displayed
        """
        js = 'show_footer(\'' + text.replace('\\', '\\\\').replace('\'', '\\\'') + '\')'
        self.frame.evaluateJavaScript(js)

    def hide_display(self, mode=HideMode.Screen):
        """
        Hide the display by making all layers transparent Store the images so they can be replaced when required

        :param mode: How the screen is to be hidden
        """
        self.log_debug('hide_display mode = %d' % mode)
        if self.screens.display_count == 1:
            # Only make visible if setting enabled.
            if not Settings().value('core/display on monitor'):
                return
        if mode == HideMode.Screen:
            self.frame.evaluateJavaScript('show_blank("desktop");')
            self.setVisible(False)
        elif mode == HideMode.Blank or self.initial_fame:
            self.frame.evaluateJavaScript('show_blank("black");')
        else:
            self.frame.evaluateJavaScript('show_blank("theme");')
        if mode != HideMode.Screen:
            if self.isHidden():
                self.setVisible(True)
                self.web_view.setVisible(True)
        self.hide_mode = mode

    def show_display(self):
        """
        Show the stored layers so the screen reappears as it was originally.
        Make the stored images None to release memory.
        """
        if self.screens.display_count == 1:
            # Only make visible if setting enabled.
            if not Settings().value('core/display on monitor'):
                return
        self.frame.evaluateJavaScript('show_blank("show");')
        if self.isHidden():
            self.setVisible(True)
        self.hide_mode = None
        # Trigger actions when display is active again.
        if self.is_live:
            Registry().execute('live_display_active')

    def _hide_mouse(self):
        """
        Hide mouse cursor when moved over display.
        """
        if Settings().value('advanced/hide mouse'):
            self.setCursor(QtCore.Qt.BlankCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "none"')
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.frame.evaluateJavaScript('document.body.style.cursor = "auto"')


class AudioPlayer(OpenLPMixin, QtCore.QObject):
    """
    This Class will play audio only allowing components to work with a soundtrack independent of the user interface.
    """

    def __init__(self, parent):
        """
        The constructor for the display form.

        :param parent:  The parent widget.
        """
        super(AudioPlayer, self).__init__(parent)
        self.current_index = -1
        self.playlist = []
        self.repeat = False
        self.media_object = Phonon.MediaObject()
        self.media_object.setTickInterval(100)
        self.audio_object = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(self.media_object, self.audio_object)
        self.media_object.aboutToFinish.connect(self.on_about_to_finish)
        self.media_object.finished.connect(self.on_finished)

    def __del__(self):
        """
        Shutting down so clean up connections
        """
        self.stop()
        for path in self.media_object.outputPaths():
            path.disconnect()

    def on_about_to_finish(self):
        """
        Just before the audio player finishes the current track, queue the next
        item in the playlist, if there is one.
        """
        self.current_index += 1
        if len(self.playlist) > self.current_index:
            self.media_object.enqueue(self.playlist[self.current_index])

    def on_finished(self):
        """
        When the audio track finishes.
        """
        if self.repeat:
            self.log_debug('Repeat is enabled... here we go again!')
            self.media_object.clearQueue()
            self.media_object.clear()
            self.current_index = -1
            self.play()

    def connectVolumeSlider(self, slider):
        """
        Connect the volume slider to the output channel.
        """
        slider.setAudioOutput(self.audio_object)

    def reset(self):
        """
        Reset the audio player, clearing the playlist and the queue.
        """
        self.current_index = -1
        self.playlist = []
        self.stop()
        self.media_object.clear()

    def play(self):
        """
        We want to play the file so start it
        """
        if self.current_index == -1:
            self.on_about_to_finish()
        self.media_object.play()

    def pause(self):
        """
        Pause the Audio
        """
        self.media_object.pause()

    def stop(self):
        """
        Stop the Audio and clean up
        """
        self.media_object.stop()

    def add_to_playlist(self, file_names):
        """
        Add another file to the playlist.

        :param file_names:  A list with files to be added to the playlist.
        """
        if not isinstance(file_names, list):
            file_names = [file_names]
        self.playlist.extend(list(map(Phonon.MediaSource, file_names)))

    def next(self):
        """
        Skip forward to the next track in the list
        """
        if not self.repeat and self.current_index + 1 >= len(self.playlist):
            return
        is_playing = self.media_object.state() == Phonon.PlayingState
        self.current_index += 1
        if self.repeat and self.current_index == len(self.playlist):
            self.current_index = 0
        self.media_object.clearQueue()
        self.media_object.clear()
        self.media_object.enqueue(self.playlist[self.current_index])
        if is_playing:
            self.media_object.play()

    def go_to(self, index):
        """
        Go to a particular track in the list

        :param index: The track to go to
        """
        is_playing = self.media_object.state() == Phonon.PlayingState
        self.media_object.clearQueue()
        self.media_object.clear()
        self.current_index = index
        self.media_object.enqueue(self.playlist[self.current_index])
        if is_playing:
            self.media_object.play()

    def connectSlot(self, signal, slot):
        """
        Connect a slot to a signal on the media object.  Used by slidecontroller to connect to audio object.

        :param slot: The slot the signal is attached to.
        :param signal: The signal to be fired
        """
        QtCore.QObject.connect(self.media_object, signal, slot)
