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
The :mod:`~openlp.core.ui.media.webkit` module contains our WebKit video player
"""
from PyQt4 import QtGui, QtWebKit

import logging

from openlp.core.common import Settings
from openlp.core.lib import translate
from openlp.core.ui.media import MediaState
from openlp.core.ui.media.mediaplayer import MediaPlayer

log = logging.getLogger(__name__)

VIDEO_CSS = """
#videobackboard {
    z-index:3;
    background-color: %(bgcolor)s;
}
#video {
    background-color: %(bgcolor)s;
    z-index:4;
}
"""

VIDEO_JS = """
    function show_video(state, path, volume, loop, variable_value){
        // Sometimes  video.currentTime stops slightly short of video.duration and video.ended is intermittent!

        var video = document.getElementById('video');
        if(volume != null){
            video.volume = volume;
        }
        switch(state){
            case 'load':
                video.src = 'file:///' + path;
                if(loop == true) {
                    video.loop = true;
                }
                video.load();
                break;
            case 'play':
                video.play();
                break;
            case 'pause':
                video.pause();
                break;
            case 'stop':
                show_video('pause');
                video.currentTime = 0;
                break;
            case 'close':
                show_video('stop');
                video.src = '';
                break;
            case 'length':
                return video.duration;
            case 'current_time':
                return video.currentTime;
            case 'seek':
                video.currentTime = variable_value;
                break;
            case 'isEnded':
                return video.ended;
            case 'setVisible':
                video.style.visibility = variable_value;
                break;
            case 'setBackBoard':
                var back = document.getElementById('videobackboard');
                back.style.visibility = variable_value;
                break;
       }
    }
"""

VIDEO_HTML = """
<div id="videobackboard" class="size" style="visibility:hidden"></div>
<video id="video" class="size" style="visibility:hidden" autobuffer preload></video>
"""

FLASH_CSS = """
#flash {
    z-index:5;
}
"""

FLASH_JS = """
    function getFlashMovieObject(movieName)
    {
        if (window.document[movieName]){
            return window.document[movieName];
        }
        if (document.embeds && document.embeds[movieName]){
            return document.embeds[movieName];
        }
    }

    function show_flash(state, path, volume, variable_value){
        var text = document.getElementById('flash');
        var flashMovie = getFlashMovieObject("OpenLPFlashMovie");
        var src = "src = 'file:///" + path + "'";
        var view_parm = " wmode='opaque'" + " width='100%%'" + " height='100%%'";
        var swf_parm = " name='OpenLPFlashMovie'" + " autostart='true' loop='false' play='true'" +
            " hidden='false' swliveconnect='true' allowscriptaccess='always'" + " volume='" + volume + "'";

        switch(state){
            case 'load':
                text.innerHTML = "<embed " + src + view_parm + swf_parm + "/>";
                flashMovie = getFlashMovieObject("OpenLPFlashMovie");
                flashMovie.Play();
                break;
            case 'play':
                flashMovie.Play();
                break;
            case 'pause':
                flashMovie.StopPlay();
                break;
            case 'stop':
                flashMovie.StopPlay();
                tempHtml = text.innerHTML;
                text.innerHTML = '';
                text.innerHTML = tempHtml;
                break;
            case 'close':
                flashMovie.StopPlay();
                text.innerHTML = '';
                break;
            case 'length':
                return flashMovie.TotalFrames();
            case 'current_time':
                return flashMovie.CurrentFrame();
            case 'seek':
//                flashMovie.GotoFrame(variable_value);
                break;
            case 'isEnded':
                //TODO check flash end
                return false;
            case 'setVisible':
                text.style.visibility = variable_value;
                break;
        }
    }
"""

FLASH_HTML = """
<div id="flash" class="size" style="visibility:hidden"></div>
"""

VIDEO_EXT = ['*.3gp', '*.3gpp', '*.3g2', '*.3gpp2', '*.aac', '*.flv', '*.f4a', '*.f4b', '*.f4p', '*.f4v', '*.mov',
             '*.m4a', '*.m4b', '*.m4p', '*.m4v', '*.mkv', '*.mp4', '*.ogv', '*.webm', '*.mpg', '*.wmv', '*.mpeg',
             '*.avi', '*.swf']

AUDIO_EXT = ['*.mp3', '*.ogg']


class WebkitPlayer(MediaPlayer):
    """
    A specialised version of the MediaPlayer class, which provides a QtWebKit
    display.
    """

    def __init__(self, parent):
        """
        Constructor
        """
        super(WebkitPlayer, self).__init__(parent, 'webkit')
        self.original_name = 'WebKit'
        self.display_name = '&WebKit'
        self.parent = parent
        self.can_background = True
        self.audio_extensions_list = AUDIO_EXT
        self.video_extensions_list = VIDEO_EXT

    def get_media_display_css(self):
        """
        Add css style sheets to htmlbuilder
        """
        background = QtGui.QColor(Settings().value('players/background color')).name()
        css = VIDEO_CSS % {'bgcolor': background}
        return css + FLASH_CSS

    def get_media_display_javascript(self):
        """
        Add javascript functions to htmlbuilder
        """
        return VIDEO_JS + FLASH_JS

    def get_media_display_html(self):
        """
        Add html code to htmlbuilder
        """
        return VIDEO_HTML + FLASH_HTML

    def setup(self, display):
        """
        Set up the player
        """
        display.web_view.resize(display.size())
        display.web_view.raise_()
        self.has_own_widget = False

    def check_available(self):
        """
        Check the availability of the media player.

        :return: boolean. True if available
        """
        web = QtWebKit.QWebPage()
        # This script should return '[object HTMLVideoElement]' if the html5 video is available in webkit. Otherwise it
        # should return '[object HTMLUnknownElement]'
        return web.mainFrame().evaluateJavaScript(
            "Object.prototype.toString.call(document.createElement('video'));") == '[object HTMLVideoElement]'

    def load(self, display):
        """
        Load a video
        """
        log.debug('load vid in Webkit Controller')
        controller = display.controller
        if display.has_audio and not controller.media_info.is_background:
            volume = controller.media_info.volume
            vol = float(volume) / float(100)
        else:
            vol = 0
        path = controller.media_info.file_info.absoluteFilePath()
        if controller.media_info.is_background:
            loop = 'true'
        else:
            loop = 'false'
        display.web_view.setVisible(True)
        if controller.media_info.file_info.suffix() == 'swf':
            controller.media_info.is_flash = True
            js = 'show_flash("load","%s");' % (path.replace('\\', '\\\\'))
        else:
            js = 'show_video("load", "%s", %s, %s);' % (path.replace('\\', '\\\\'), str(vol), loop)
        display.frame.evaluateJavaScript(js)
        return True

    def resize(self, display):
        """
        Resize the player
        """
        display.web_view.resize(display.size())

    def play(self, display):
        """
        Play a video
        """
        controller = display.controller
        display.web_loaded = True
        length = 0
        start_time = 0
        if self.state != MediaState.Paused and controller.media_info.start_time > 0:
            start_time = controller.media_info.start_time
        self.set_visible(display, True)
        if controller.media_info.is_flash:
            display.frame.evaluateJavaScript('show_flash("play");')
        else:
            display.frame.evaluateJavaScript('show_video("play");')
        if start_time > 0:
            self.seek(display, controller.media_info.start_time * 1000)
        # TODO add playing check and get the correct media length
        controller.media_info.length = length
        self.state = MediaState.Playing
        display.web_view.raise_()
        return True

    def pause(self, display):
        """
        Pause a video
        """
        controller = display.controller
        if controller.media_info.is_flash:
            display.frame.evaluateJavaScript('show_flash("pause");')
        else:
            display.frame.evaluateJavaScript('show_video("pause");')
        self.state = MediaState.Paused

    def stop(self, display):
        """
        Stop a video
        """
        controller = display.controller
        if controller.media_info.is_flash:
            display.frame.evaluateJavaScript('show_flash("stop");')
        else:
            display.frame.evaluateJavaScript('show_video("stop");')
        self.state = MediaState.Stopped

    def volume(self, display, volume):
        """
        Set the volume
        """
        controller = display.controller
        # 1.0 is the highest value
        if display.has_audio:
            vol = float(volume) / float(100)
            if not controller.media_info.is_flash:
                display.frame.evaluateJavaScript('show_video(null, null, %s);' % str(vol))

    def seek(self, display, seek_value):
        """
        Go to a position in the video
        """
        controller = display.controller
        if controller.media_info.is_flash:
            seek = seek_value
            display.frame.evaluateJavaScript('show_flash("seek", null, null, "%s");' % (seek))
        else:
            seek = float(seek_value) / 1000
            display.frame.evaluateJavaScript('show_video("seek", null, null, null, "%f");' % (seek))

    def reset(self, display):
        """
        Reset the player
        """
        controller = display.controller
        if controller.media_info.is_flash:
            display.frame.evaluateJavaScript('show_flash("close");')
        else:
            display.frame.evaluateJavaScript('show_video("close");')
        self.state = MediaState.Off

    def set_visible(self, display, status):
        """
        Set the visibility
        """
        controller = display.controller
        if status:
            is_visible = "visible"
        else:
            is_visible = "hidden"
        if controller.media_info.is_flash:
            display.frame.evaluateJavaScript('show_flash("setVisible", null, null, "%s");' % is_visible)
        else:
            display.frame.evaluateJavaScript('show_video("setVisible", null, null, null, "%s");' % is_visible)

    def update_ui(self, display):
        """
        Update the UI
        """
        controller = display.controller
        if controller.media_info.is_flash:
            current_time = display.frame.evaluateJavaScript('show_flash("current_time");')
            length = display.frame.evaluateJavaScript('show_flash("length");')
        else:
            if display.frame.evaluateJavaScript('show_video("isEnded");'):
                self.stop(display)
            current_time = display.frame.evaluateJavaScript('show_video("current_time");')
            # check if conversion was ok and value is not 'NaN'
            if current_time and current_time != float('inf'):
                current_time = int(current_time * 1000)
            length = display.frame.evaluateJavaScript('show_video("length");')
            # check if conversion was ok and value is not 'NaN'
            if length and length != float('inf'):
                length = int(length * 1000)
        if current_time and length:
            controller.media_info.length = length
            controller.seek_slider.setMaximum(length)
            if not controller.seek_slider.isSliderDown():
                controller.seek_slider.blockSignals(True)
                controller.seek_slider.setSliderPosition(current_time)
                controller.seek_slider.blockSignals(False)

    def get_info(self):
        """
        Return some information about this player
        """
        part1 = translate('Media.player', 'Webkit is a media player which runs inside a web browser. This player '
                                          'allows text over video to be rendered.')
        part2 = translate('Media.player', 'Audio')
        part3 = translate('Media.player', 'Video')
        return part1 + '<br/> <strong>' + part2 + '</strong><br/>' + str(AUDIO_EXT) + '<br/><strong>' + part3 + \
            '</strong><br/>' + str(VIDEO_EXT) + '<br/>'
