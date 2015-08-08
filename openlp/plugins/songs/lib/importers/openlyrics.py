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
The :mod:`openlyrics` module provides the functionality for importing
songs which are saved as OpenLyrics files.
"""

import logging
import os

from lxml import etree

from openlp.core.ui.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics, OpenLyricsError

log = logging.getLogger(__name__)


class OpenLyricsImport(SongImport):
    """
    This provides the Openlyrics import.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the Open Lyrics importer.
        """
        log.debug('initialise OpenLyricsImport')
        super(OpenLyricsImport, self).__init__(manager, **kwargs)
        self.open_lyrics = OpenLyrics(self.manager)

    def do_import(self):
        """
        Imports the songs.
        """
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        parser = etree.XMLParser(remove_blank_text=True)
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType % os.path.basename(file_path))
            try:
                # Pass a file object, because lxml does not cope with some
                # special characters in the path (see lp:757673 and lp:744337).
                parsed_file = etree.parse(open(file_path, 'rb'), parser)
                xml = etree.tostring(parsed_file).decode()
                self.open_lyrics.xml_to_song(xml)
            except etree.XMLSyntaxError:
                log.exception('XML syntax error in file %s' % file_path)
                self.log_error(file_path, SongStrings.XMLSyntaxError)
            except OpenLyricsError as exception:
                log.exception('OpenLyricsException %d in file %s: %s' %
                              (exception.type, file_path, exception.log_message))
                self.log_error(file_path, exception.display_message)
