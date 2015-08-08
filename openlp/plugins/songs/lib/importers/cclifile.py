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

import logging
import os
import chardet
import codecs

from openlp.core.lib import translate
from openlp.plugins.songs.lib import VerseType
from .songimport import SongImport

log = logging.getLogger(__name__)


class CCLIFileImport(SongImport):
    """
    The :class:`CCLIFileImport` class provides OpenLP with the ability to import CCLI SongSelect song files in
    TEXT and USR formats. See `<http://www.ccli.com/>`_ for more details.

    NOTE: Sometime before 2015, CCLI/SongSelect has changed the USR filename to a .bin extension; however,
     the file format remained the same as the .usr file format.
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the import.

        :param manager: The song manager for the running OpenLP installation.
        :param kwargs:  The files to be imported.
        """
        SongImport.__init__(self, manager, **kwargs)

    def do_import(self):
        """
        Import either a USR or TEXT SongSelect file.
        """
        log.debug('Starting CCLI File Import')
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for filename in self.import_source:
            filename = str(filename)
            log.debug('Importing CCLI File: %s', filename)
            if os.path.isfile(filename):
                detect_file = open(filename, 'rb')
                detect_content = detect_file.read(2048)
                try:
                    str(detect_content, 'utf-8')
                    details = {'confidence': 1, 'encoding': 'utf-8'}
                except UnicodeDecodeError:
                    details = chardet.detect(detect_content)
                detect_file.close()
                infile = codecs.open(filename, 'r', details['encoding'])
                if not infile.read(1) == '\ufeff':
                    # not UTF or no BOM was found
                    infile.seek(0)
                lines = infile.readlines()
                infile.close()
                ext = os.path.splitext(filename)[1]
                if ext.lower() == '.usr' or ext.lower() == '.bin':
                    log.info('SongSelect USR format file found: %s', filename)
                    if not self.do_import_usr_file(lines):
                        self.log_error(filename)
                elif ext.lower() == '.txt':
                    log.info('SongSelect TEXT format file found: %s', filename)
                    if not self.do_import_txt_file(lines):
                        self.log_error(filename)
                else:
                    self.log_error(filename, translate('SongsPlugin.CCLIFileImport', 'The file does not have a valid '
                                                                                     'extension.'))
                    log.info('Extension %s is not valid', filename)
            if self.stop_import_flag:
                return

    def do_import_usr_file(self, text_list):
        """
        The :func:`doImport_usr_file` method provides OpenLP with the ability
        to import CCLI SongSelect songs in *USR* file format.

        **SongSelect USR file format**

        ``[File]``
            USR file format first line

        ``Type=``
            Indicates the file type
            e.g. *Type=SongSelect Import File*

        ``Version=3.0``
            File format version

        ``[S A2672885]``
            Contains the CCLI Song number e.g. *2672885*

        ``Title=``
            Contains the song title (e.g. *Title=Above All*)

        ``Author=``
            Contains a | delimited list of the song authors
            e.g. *Author=LeBlanc, Lenny | Baloche, Paul*

        ``Copyright=``
            Contains a | delimited list of the song copyrights
            e.g. Copyright=1999 Integrity's Hosanna! Music |
            LenSongs Publishing (Verwaltet von Gerth Medien
            Musikverlag)

        ``Admin=``
            Contains the song administrator
            e.g. *Admin=Gerth Medien Musikverlag*

        ``Themes=``
            Contains a /t delimited list of the song themes
            e.g. *Themes=Cross/tKingship/tMajesty/tRedeemer*

        ``Keys=``
            Contains the keys in which the music is played??
            e.g. *Keys=A*

        ``Fields=``
            Contains a list of the songs fields in order /t delimited
            e.g. *Fields=Vers 1/tVers 2/tChorus 1/tAndere 1*

        ``Words=``
            Contains the songs various lyrics in order as shown by the
            *Fields* description
            e.g. *Words=Above all powers....* [/n = CR, /n/t = CRLF]

        :param text_list: An array of strings containing the usr file content.
        """
        log.debug('USR file text: %s', text_list)
        song_author = ''
        song_topics = ''
        for line in text_list:
            if line.startswith('[S '):
                ccli, line = line.split(']', 1)
                if ccli.startswith('[S A'):
                    self.ccli_number = ccli[4:].strip()
                else:
                    self.ccli_number = ccli[3:].strip()
            if line.startswith('Title='):
                self.title = line[6:].strip()
            elif line.startswith('Author='):
                song_author = line[7:].strip()
            elif line.startswith('Copyright='):
                self.copyright = line[10:].strip()
            elif line.startswith('Themes='):
                song_topics = line[7:].strip().replace(' | ', '/t')
            elif line.startswith('Fields='):
                # Fields contain single line indicating verse, chorus, etc,
                # /t delimited, same as with words field. store separately
                # and process at end.
                song_fields = line[7:].strip()
            elif line.startswith('Words='):
                song_words = line[6:].strip()
            # Unhandled usr keywords: Type, Version, Admin, Keys
        # Process Fields and words sections.
        check_first_verse_line = False
        field_list = song_fields.split('/t')
        words_list = song_words.split('/t')
        for counter in range(len(field_list)):
            if field_list[counter].startswith('Ver'):
                verse_type = VerseType.tags[VerseType.Verse]
            elif field_list[counter].startswith('Ch'):
                verse_type = VerseType.tags[VerseType.Chorus]
            elif field_list[counter].startswith('Br'):
                verse_type = VerseType.tags[VerseType.Bridge]
            else:
                verse_type = VerseType.tags[VerseType.Other]
                check_first_verse_line = True
            verse_text = str(words_list[counter])
            verse_text = verse_text.replace('/n', '\n')
            verse_text = verse_text.replace(' | ', '\n')
            verse_lines = verse_text.split('\n', 1)
            if check_first_verse_line:
                if verse_lines[0].startswith('(PRE-CHORUS'):
                    verse_type = VerseType.tags[VerseType.PreChorus]
                    log.debug('USR verse PRE-CHORUS: %s', verse_lines[0])
                    verse_text = verse_lines[1]
                elif verse_lines[0].startswith('(BRIDGE'):
                    verse_type = VerseType.tags[VerseType.Bridge]
                    log.debug('USR verse BRIDGE')
                    verse_text = verse_lines[1]
                elif verse_lines[0].startswith('('):
                    verse_type = VerseType.tags[VerseType.Other]
                    verse_text = verse_lines[1]
            if verse_text:
                self.add_verse(verse_text, verse_type)
            check_first_verse_line = False
        # Handle multiple authors
        author_list = song_author.split('/')
        if len(author_list) < 2:
            author_list = song_author.split('|')
        for author in author_list:
            separated = author.split(',')
            if len(separated) > 1:
                author = ' '.join(map(str.strip, reversed(separated)))
            self.add_author(author.strip())
        self.topics = [topic.strip() for topic in song_topics.split('/t')]
        return self.finish()

    def do_import_txt_file(self, text_list):
        """
        The :func:`doImport_txt_file` method provides OpenLP with the ability
        to import CCLI SongSelect songs in *TXT* file format.

        :param text_list: An array of strings containing the txt file content.

        SongSelect .txt file format::

            Song Title                  # Contains the song title
            <Empty line>
            Verse type and number       # e.g. Verse 1, Chorus 1
            Verse lyrics
            <Empty line>
            <Empty line>
            Verse type and number (repeats)
            Verse lyrics
            <Empty line>
            <Empty line>
            Song CCLI number
                # e.g. CCLI Number (e.g.CCLI-Liednummer: 2672885)
            Song copyright (if it begins ©, otherwise after authors)
                # e.g. © 1999 Integrity's Hosanna! Music | LenSongs Publishing
            Song authors                # e.g. Lenny LeBlanc | Paul Baloche
            Licencing info
                # e.g. For use solely with the SongSelect Terms of Use.
            All rights Reserved.  www.ccli.com
            CCLI Licence number of user
                # e.g. CCLI-Liedlizenznummer: 14 / CCLI License No. 14

        """
        log.debug('TXT file text: %s', text_list)
        line_number = 0
        check_first_verse_line = False
        verse_text = ''
        song_author = ''
        verse_start = False
        for line in text_list:
            clean_line = line.strip()
            if not clean_line:
                if line_number == 0:
                    continue
                elif verse_start:
                    if verse_text:
                        self.add_verse(verse_text, verse_type)
                        verse_text = ''
                        verse_start = False
            else:
                # line_number=0, song title
                if line_number == 0:
                    self.title = clean_line
                    line_number += 1
                # line_number=1, verses
                elif line_number == 1:
                    # line_number=1, ccli number, first line after verses
                    if clean_line.startswith('CCLI'):
                        line_number += 1
                        ccli_parts = clean_line.split(' ')
                        self.ccli_number = ccli_parts[len(ccli_parts) - 1]
                    elif not verse_start:
                        # We have the verse descriptor
                        verse_desc_parts = clean_line.split(' ')
                        if len(verse_desc_parts) == 2:
                            if verse_desc_parts[0].startswith('Ver'):
                                verse_type = VerseType.tags[VerseType.Verse]
                            elif verse_desc_parts[0].startswith('Ch'):
                                verse_type = VerseType.tags[VerseType.Chorus]
                            elif verse_desc_parts[0].startswith('Br'):
                                verse_type = VerseType.tags[VerseType.Bridge]
                            else:
                                # we need to analyse the next line for
                                # verse type, so set flag
                                verse_type = VerseType.tags[VerseType.Other]
                                check_first_verse_line = True
                            verse_number = verse_desc_parts[1]
                        else:
                            verse_type = VerseType.tags[VerseType.Other]
                            verse_number = 1
                        verse_start = True
                    else:
                        # check first line for verse type
                        if check_first_verse_line:
                            if line.startswith('(PRE-CHORUS'):
                                verse_type = VerseType.tags[VerseType.PreChorus]
                            elif line.startswith('(BRIDGE'):
                                verse_type = VerseType.tags[VerseType.Bridge]
                            # Handle all other misc types
                            elif line.startswith('('):
                                verse_type = VerseType.tags[VerseType.Other]
                            else:
                                verse_text = verse_text + line
                            check_first_verse_line = False
                        else:
                            # We have verse content or the start of the
                            # last part. Add l so as to keep the CRLF
                            verse_text = verse_text + line
                else:
                    # line_number=2, copyright
                    if line_number == 2:
                        line_number += 1
                        if clean_line.startswith('©'):
                            self.copyright = clean_line
                        else:
                            song_author = clean_line
                    # n=3, authors
                    elif line_number == 3:
                        line_number += 1
                        if song_author:
                            self.copyright = clean_line
                        else:
                            song_author = clean_line
                    # line_number=4, comments lines before last line
                    elif line_number == 4 and not clean_line.startswith('CCL'):
                        self.comments += clean_line
        # split on known separators
        author_list = song_author.split('/')
        if len(author_list) < 2:
            author_list = song_author.split('|')
        # Clean spaces before and after author names.
        for author_name in author_list:
            self.add_author(author_name.strip())
        return self.finish()
