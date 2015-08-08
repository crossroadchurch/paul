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
The :mod:`~openlp.core.ui.media` module contains classes and objects for media player integration.
"""
import logging

from openlp.core.common import Settings

from PyQt4 import QtCore

log = logging.getLogger(__name__ + '.__init__')


class MediaState(object):
    """
    An enumeration for possible States of the Media Player
    """
    Off = 0
    Loaded = 1
    Playing = 2
    Paused = 3
    Stopped = 4


class MediaType(object):
    """
    An enumeration of possible Media Types
    """
    Unused = 0
    Audio = 1
    Video = 2
    CD = 3
    DVD = 4
    Folder = 5


class MediaInfo(object):
    """
    This class hold the media related info
    """
    file_info = None
    volume = 100
    is_flash = False
    is_background = False
    length = 0
    start_time = 0
    end_time = 0
    title_track = 0
    audio_track = 0
    subtitle_track = 0
    media_type = MediaType()


def get_media_players():
    """
    This method extracts the configured media players and overridden player
    from the settings.
    """
    log.debug('get_media_players')
    saved_players = Settings().value('media/players')
    reg_ex = QtCore.QRegExp(".*\[(.*)\].*")
    if Settings().value('media/override player') == QtCore.Qt.Checked:
        if reg_ex.exactMatch(saved_players):
            overridden_player = '%s' % reg_ex.cap(1)
        else:
            overridden_player = 'auto'
    else:
        overridden_player = ''
    saved_players_list = saved_players.replace('[', '').replace(']', '').split(',') if saved_players else []
    return saved_players_list, overridden_player


def set_media_players(players_list, overridden_player='auto'):
    """
    This method saves the configured media players and overridden player to the settings

    :param players_list: A list with all active media players.
    :param overridden_player: Here an special media player is chosen for all media actions.
    """
    log.debug('set_media_players')
    players = ','.join(players_list)
    if Settings().value('media/override player') == QtCore.Qt.Checked and overridden_player != 'auto':
        players = players.replace(overridden_player, '[%s]' % overridden_player)
    Settings().setValue('media/players', players)


def parse_optical_path(input):
    """
    Split the optical path info.

    :param input: The string to parse
    :return: The elements extracted from the string:  filename, title, audio_track, subtitle_track, start, end
    """
    log.debug('parse_optical_path, about to parse: "%s"' % input)
    clip_info = input.split(sep=':')
    title = int(clip_info[1])
    audio_track = int(clip_info[2])
    subtitle_track = int(clip_info[3])
    start = float(clip_info[4])
    end = float(clip_info[5])
    clip_name = clip_info[6]
    filename = clip_info[7]
    # Windows path usually contains a colon after the drive letter
    if len(clip_info) > 8:
        filename += ':' + clip_info[8]
    return filename, title, audio_track, subtitle_track, start, end, clip_name


def format_milliseconds(milliseconds):
    """
    Format milliseconds into a human readable time string.
    :param milliseconds: Milliseconds to format
    :return: Time string in format: hh.mm.ss,ttt
    """
    seconds, millis = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, millis)

from .mediacontroller import MediaController
from .playertab import PlayerTab

__all__ = ['MediaController', 'PlayerTab']
