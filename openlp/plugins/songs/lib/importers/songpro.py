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
The :mod:`songpro` module provides the functionality for importing SongPro
songs into the OpenLP database.
"""
import re

from openlp.plugins.songs.lib import strip_rtf
from openlp.plugins.songs.lib.importers.songimport import SongImport


class SongProImport(SongImport):
    """
    The :class:`SongProImport` class provides the ability to import song files
    from SongPro export files.

    **SongPro Song File Format:**

    SongPro has the option to export under its File menu
    This produces files containing single or multiple songs
    The file is text with lines tagged with # followed by an identifier.
    This is documented here: http://creationsoftware.com/ImportIdentifiers.php
    An example here: http://creationsoftware.com/ExampleImportingManySongs.txt

    #A - next line is the Song Author
    #B - the lines following until next tagged line are the "Bridge" words
        (can be in rtf or plain text) which we map as B1
    #C - the lines following until next tagged line are the chorus words
        (can be in rtf or plain text)
        which we map as C1
    #D - the lines following until next tagged line are the "Ending" words
        (can be in rtf or plain text) which we map as E1
    #E - this song ends here, so we process the song -
        and start again at the next line
    #G - next line is the Group
    #M - next line is the Song Number
    #N - next line are Notes
    #R - next line is the SongCopyright
    #O - next line is the Verse Sequence
    #T - next line is the Song Title
    #1 - #7 the lines following until next tagged line are the verse x words
        (can be in rtf or plain text)
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the SongPro importer.
        """
        SongImport.__init__(self, manager, **kwargs)

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        self.encoding = None
        with open(self.import_source, 'r') as songs_file:
            self.import_wizard.progress_bar.setMaximum(0)
            tag = ''
            text = ''
            for file_line in songs_file:
                if self.stop_import_flag:
                    break
                file_line = str(file_line, 'cp1252')
                file_text = file_line.rstrip()
                if file_text and file_text[0] == '#':
                    self.process_section(tag, text.rstrip())
                    tag = file_text[1:]
                    text = ''
                else:
                    text += file_line

    def process_section(self, tag, text):
        """
        Process a section of the song, i.e. title, verse etc.
        """
        if tag == 'T':
            self.set_defaults()
            if text:
                self.title = text
            return
        elif tag == 'E':
            self.finish()
            return
        if 'rtf1' in text:
            result = strip_rtf(text, self.encoding)
            if result is None:
                return
            text, self.encoding = result
            text = text.rstrip()
        if not text:
            return
        if tag == 'A':
            self.parse_author(text)
        elif tag in ['B', 'C']:
            self.add_verse(text, tag)
        elif tag == 'D':
            self.add_verse(text, 'E')
        elif tag == 'G':
            self.topics.append(text)
        elif tag == 'M':
            matches = re.findall(r'\d+', text)
            if matches:
                self.song_number = matches[-1]
                self.song_book_name = text[:text.rfind(self.song_number)]
        elif tag == 'N':
            self.comments = text
        elif tag == 'O':
            for char in text:
                if char == 'C':
                    self.verse_order_list.append('C1')
                elif char == 'B':
                    self.verse_order_list.append('B1')
                elif char == 'D':
                    self.verse_order_list.append('E1')
                elif '1' <= char <= '7':
                    self.verse_order_list.append('V' + char)
        elif tag == 'R':
            self.add_copyright(text)
        elif '1' <= tag <= '7':
            self.add_verse(text, 'V' + tag[1:])
