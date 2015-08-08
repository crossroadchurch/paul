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
The :mod:`openlyricsexport` module provides the functionality for exporting songs from the database to the OpenLyrics
format.
"""
import logging
import os

from lxml import etree

from openlp.core.common import RegistryProperties, check_directory_exists, translate
from openlp.core.utils import clean_filename
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics

log = logging.getLogger(__name__)


class OpenLyricsExport(RegistryProperties):
    """
    This provides the Openlyrics export.
    """
    def __init__(self, parent, songs, save_path):
        """
        Initialise the export.
        """
        log.debug('initialise OpenLyricsExport')
        self.parent = parent
        self.manager = parent.plugin.manager
        self.songs = songs
        self.save_path = save_path
        check_directory_exists(self.save_path)

    def do_export(self):
        """
        Export the songs.
        """
        log.debug('started OpenLyricsExport')
        open_lyrics = OpenLyrics(self.manager)
        self.parent.progress_bar.setMaximum(len(self.songs))
        for song in self.songs:
            self.application.process_events()
            if self.parent.stop_export_flag:
                return False
            self.parent.increment_progress_bar(
                translate('SongsPlugin.OpenLyricsExport', 'Exporting "%s"...') % song.title)
            xml = open_lyrics.song_to_xml(song)
            tree = etree.ElementTree(etree.fromstring(xml.encode()))
            filename = '%s (%s)' % (song.title, ', '.join([author.display_name for author in song.authors]))
            filename = clean_filename(filename)
            # Ensure the filename isn't too long for some filesystems
            filename_with_ext = '%s.xml' % filename[0:250 - len(self.save_path)]
            # Make sure we're not overwriting an existing file
            conflicts = 0
            while os.path.exists(os.path.join(self.save_path, filename_with_ext)):
                conflicts += 1
                filename_with_ext = '%s-%d.xml' % (filename[0:247 - len(self.save_path)], conflicts)
            # Pass a file object, because lxml does not cope with some special
            # characters in the path (see lp:757673 and lp:744337).
            tree.write(open(os.path.join(self.save_path, filename_with_ext), 'wb'), encoding='utf-8',
                       xml_declaration=True, pretty_print=True)
        return True
