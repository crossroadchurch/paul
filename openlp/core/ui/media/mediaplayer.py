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
The :mod:`~openlp.core.ui.media.mediaplayer` module contains the MediaPlayer class.
"""
from openlp.core.common import RegistryProperties
from openlp.core.ui.media import MediaState


class MediaPlayer(RegistryProperties):
    """
    This is the base class media Player class to provide OpenLP with a pluggable media display framework.
    """

    def __init__(self, parent, name='media_player'):
        """
        Constructor
        """
        self.parent = parent
        self.name = name
        self.available = self.check_available()
        self.is_active = False
        self.can_background = False
        self.can_folder = False
        self.state = MediaState.Off
        self.has_own_widget = False
        self.audio_extensions_list = []
        self.video_extensions_list = []

    def check_available(self):
        """
        Player is available on this machine
        """
        return False

    def setup(self, display):
        """
        Create the related widgets for the current display
        """
        pass

    def load(self, display):
        """
        Load a new media file and check if it is valid
        """
        return True

    def resize(self, display):
        """
        If the main display size or position is changed, the media widgets
        should also resized
        """
        pass

    def play(self, display):
        """
        Starts playing of current Media File
        """
        pass

    def pause(self, display):
        """
        Pause of current Media File
        """
        pass

    def stop(self, display):
        """
        Stop playing of current Media File
        """
        pass

    def volume(self, display, vol):
        """
        Change volume of current Media File
        """
        pass

    def seek(self, display, seek_value):
        """
        Change playing position of current Media File
        """
        pass

    def reset(self, display):
        """
        Remove the current loaded video
        """
        pass

    def set_visible(self, display, status):
        """
        Show/Hide the media widgets
        """
        pass

    def update_ui(self, display):
        """
        Do some ui related stuff (e.g. update the seek slider)
        """
        pass

    def get_media_display_css(self):
        """
        Add css style sheets to htmlbuilder
        """
        return ''

    def get_media_display_javascript(self):
        """
        Add javascript functions to htmlbuilder
        """
        return ''

    def get_media_display_html(self):
        """
        Add html code to htmlbuilder
        """
        return ''

    def get_info(self):
        """
        Returns Information about the player
        """
        return ''
