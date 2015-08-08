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
The :mod:`songbeamer` module provides the functionality for importing SongBeamer songs into the OpenLP database.
"""
import chardet
import codecs
import logging
import os
import re

from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)


class SongBeamerTypes(object):
    MarkTypes = {
        'Refrain': VerseType.tags[VerseType.Chorus],
        'Chorus': VerseType.tags[VerseType.Chorus],
        'Vers': VerseType.tags[VerseType.Verse],
        'Verse': VerseType.tags[VerseType.Verse],
        'Strophe': VerseType.tags[VerseType.Verse],
        'Intro': VerseType.tags[VerseType.Intro],
        'Coda': VerseType.tags[VerseType.Ending],
        'Ending': VerseType.tags[VerseType.Ending],
        'Bridge': VerseType.tags[VerseType.Bridge],
        'Interlude': VerseType.tags[VerseType.Bridge],
        'Zwischenspiel': VerseType.tags[VerseType.Bridge],
        'Pre-Chorus': VerseType.tags[VerseType.PreChorus],
        'Pre-Refrain': VerseType.tags[VerseType.PreChorus],
        'Misc': VerseType.tags[VerseType.Other],
        'Pre-Bridge': VerseType.tags[VerseType.Other],
        'Pre-Coda': VerseType.tags[VerseType.Other],
        'Part': VerseType.tags[VerseType.Other],
        'Teil': VerseType.tags[VerseType.Other],
        'Unbekannt': VerseType.tags[VerseType.Other],
        'Unknown': VerseType.tags[VerseType.Other],
        'Unbenannt': VerseType.tags[VerseType.Other],
        '$$M=': VerseType.tags[VerseType.Other]
    }


class SongBeamerImport(SongImport):
    """
    Import Song Beamer files(s). Song Beamer file format is text based in the beginning are one or more control tags
    written.
    """
    HTML_TAG_PAIRS = [
        (re.compile('<b>'), '{st}'),
        (re.compile('</b>'), '{/st}'),
        (re.compile('<i>'), '{it}'),
        (re.compile('</i>'), '{/it}'),
        (re.compile('<u>'), '{u}'),
        (re.compile('</u>'), '{/u}'),
        (re.compile('<p>'), '{p}'),
        (re.compile('</p>'), '{/p}'),
        (re.compile('<super>'), '{su}'),
        (re.compile('</super>'), '{/su}'),
        (re.compile('<sub>'), '{sb}'),
        (re.compile('</sub>'), '{/sb}'),
        (re.compile('<br.*?>'), '{br}'),
        (re.compile('<[/]?wordwrap>'), ''),
        (re.compile('<[/]?strike>'), ''),
        (re.compile('<[/]?h.*?>'), ''),
        (re.compile('<[/]?s.*?>'), ''),
        (re.compile('<[/]?linespacing.*?>'), ''),
        (re.compile('<[/]?c.*?>'), ''),
        (re.compile('<align.*?>'), ''),
        (re.compile('<valign.*?>'), '')
    ]

    def __init__(self, manager, **kwargs):
        """
        Initialise the Song Beamer importer.
        """
        super(SongBeamerImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if not isinstance(self.import_source, list):
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for import_file in self.import_source:
            # TODO: check that it is a valid SongBeamer file
            if self.stop_import_flag:
                return
            self.set_defaults()
            self.current_verse = ''
            self.current_verse_type = VerseType.tags[VerseType.Verse]
            read_verses = False
            file_name = os.path.split(import_file)[1]
            if os.path.isfile(import_file):
                # First open in binary mode to detect the encoding
                detect_file = open(import_file, 'rb')
                details = chardet.detect(detect_file.read())
                detect_file.close()
                infile = codecs.open(import_file, 'r', details['encoding'])
                song_data = infile.readlines()
                infile.close()
            else:
                continue
            self.title = file_name.split('.sng')[0]
            read_verses = False
            for line in song_data:
                # Just make sure that the line is of the type 'Unicode'.
                line = str(line).strip()
                if line.startswith('#') and not read_verses:
                    self.parseTags(line)
                elif line.startswith('--'):
                    # --- and -- allowed for page-breaks (difference in Songbeamer only in printout)
                    if self.current_verse:
                        self.replace_html_tags()
                        self.add_verse(self.current_verse, self.current_verse_type)
                        self.current_verse = ''
                        self.current_verse_type = VerseType.tags[VerseType.Verse]
                    read_verses = True
                    verse_start = True
                elif read_verses:
                    if verse_start:
                        verse_start = False
                        if not self.check_verse_marks(line):
                            self.current_verse = line + '\n'
                    else:
                        self.current_verse += line + '\n'
            if self.current_verse:
                self.replace_html_tags()
                self.add_verse(self.current_verse, self.current_verse_type)
            if not self.finish():
                self.log_error(import_file)

    def replace_html_tags(self):
        """
        This can be called to replace SongBeamer's specific (html) tags with OpenLP's specific (html) tags.
        """
        for pair in SongBeamerImport.HTML_TAG_PAIRS:
            self.current_verse = pair[0].sub(pair[1], self.current_verse)

    def parseTags(self, line):
        """
        Parses a meta data line.

        :param line: The line in the file. It should consist of a tag and a value for this tag (unicode)::

                '#Title=Nearer my God to Thee'
        """
        tag_val = line.split('=', 1)
        if len(tag_val) == 1:
            return
        if not tag_val[0] or not tag_val[1]:
            return
        if tag_val[0] == '#(c)':
            self.add_copyright(tag_val[1])
        elif tag_val[0] == '#AddCopyrightInfo':
            pass
        elif tag_val[0] == '#Author':
            self.parse_author(tag_val[1])
        elif tag_val[0] == '#BackgroundImage':
            pass
        elif tag_val[0] == '#Bible':
            pass
        elif tag_val[0] == '#Categories':
            self.topics = tag_val[1].split(',')
        elif tag_val[0] == '#CCLI':
            self.ccli_number = tag_val[1]
        elif tag_val[0] == '#Chords':
            pass
        elif tag_val[0] == '#ChurchSongID':
            pass
        elif tag_val[0] == '#ColorChords':
            pass
        elif tag_val[0] == '#Comments':
            self.comments = tag_val[1]
        elif tag_val[0] == '#Editor':
            pass
        elif tag_val[0] == '#Font':
            pass
        elif tag_val[0] == '#FontLang2':
            pass
        elif tag_val[0] == '#FontSize':
            pass
        elif tag_val[0] == '#Format':
            pass
        elif tag_val[0] == '#Format_PreLine':
            pass
        elif tag_val[0] == '#Format_PrePage':
            pass
        elif tag_val[0] == '#ID':
            pass
        elif tag_val[0] == '#Key':
            pass
        elif tag_val[0] == '#Keywords':
            pass
        elif tag_val[0] == '#LangCount':
            pass
        elif tag_val[0] == '#Melody':
            self.parse_author(tag_val[1])
        elif tag_val[0] == '#NatCopyright':
            pass
        elif tag_val[0] == '#OTitle':
            pass
        elif tag_val[0] == '#OutlineColor':
            pass
        elif tag_val[0] == '#OutlinedFont':
            pass
        elif tag_val[0] == '#QuickFind':
            pass
        elif tag_val[0] == '#Rights':
            song_book_pub = tag_val[1]
        elif tag_val[0] == '#Songbook' or tag_val[0] == '#SongBook':
            book_data = tag_val[1].split('/')
            self.song_book_name = book_data[0].strip()
            if len(book_data) == 2:
                number = book_data[1].strip()
                self.song_number = number if number.isdigit() else ''
        elif tag_val[0] == '#Speed':
            pass
        elif tag_val[0] == 'Tempo':
            pass
        elif tag_val[0] == '#TextAlign':
            pass
        elif tag_val[0] == '#Title':
            self.title = str(tag_val[1])
        elif tag_val[0] == '#TitleAlign':
            pass
        elif tag_val[0] == '#TitleFontSize':
            pass
        elif tag_val[0] == '#TitleLang2':
            pass
        elif tag_val[0] == '#TitleLang3':
            pass
        elif tag_val[0] == '#TitleLang4':
            pass
        elif tag_val[0] == '#Translation':
            pass
        elif tag_val[0] == '#Transpose':
            pass
        elif tag_val[0] == '#TransposeAccidental':
            pass
        elif tag_val[0] == '#Version':
            pass
        elif tag_val[0] == '#VerseOrder':
            # TODO: add the verse order.
            pass

    def check_verse_marks(self, line):
        """
        Check and add the verse's MarkType. Returns ``True`` if the given linE contains a correct verse mark otherwise
        ``False``.

        :param line: The line to check for marks (unicode).
        """
        marks = line.split(' ')
        if len(marks) <= 2 and marks[0] in SongBeamerTypes.MarkTypes:
            self.current_verse_type = SongBeamerTypes.MarkTypes[marks[0]]
            if len(marks) == 2:
                # If we have a digit, we append it to current_verse_type.
                if marks[1].isdigit():
                    self.current_verse_type += marks[1]
            return True
        elif marks[0].startswith('$$M='):  # this verse-mark cannot be numbered
            self.current_verse_type = SongBeamerTypes.MarkTypes['$$M=']
            return True
        return False
