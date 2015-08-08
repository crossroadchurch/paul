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
The :mod:`wordsofworship` module provides the functionality for importing Words of
Worship songs into the OpenLP database.
"""
import os
import logging

from openlp.core.common import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

BLOCK_TYPES = ('V', 'C', 'B')

log = logging.getLogger(__name__)


class WordsOfWorshipImport(SongImport):
    """
    The :class:`WordsOfWorshipImport` class provides the ability to import song files from Words of Worship.

    **Words Of Worship Song File Format:**

    The Words Of Worship song file format is as follows:

    * The song title is the file name minus the extension.
    * The song has a header, a number of blocks, followed by footer containing
      the author and the copyright.
    * A block can be a verse, chorus or bridge.

    File Header:
        Bytes are counted from one, i.e. the first byte is byte 1. The first 19
        bytes should be "WoW File \\nSong Words" The bytes after this and up to
        the 56th byte, can change but no real meaning has been found. The
        56th byte specifies how many blocks there are. The first block starts
        with byte 83 after the "CSongDoc::CBlock" declaration.

    Blocks:
        Each block has a starting header, some lines of text, and an ending
        footer. Each block starts with a 32 bit number, which specifies how
        many lines are in that block.

        Each block ends with a 32 bit number, which defines what type of
        block it is:

        * ``NUL`` (0x00) - Verse
        * ``SOH`` (0x01) - Chorus
        * ``STX`` (0x02) - Bridge

        Blocks are separated by two bytes. The first byte is 0x01, and the
        second byte is 0x80.

    Lines:
        Each line starts with a byte which specifies how long that line is,
        the line text, and ends with a null byte.

    Footer:
        The footer follows on after the last block, the first byte specifies
        the length of the author text, followed by the author text, if
        this byte is null, then there is no author text. The byte after the
        author text specifies the length of the copyright text, followed
        by the copyright text.

        The file is ended with four null bytes.

    Valid extensions for a Words of Worship song file are:

    * .wsg
    * .wow-song
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the Words of Worship importer.
        """
        super(WordsOfWorshipImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if isinstance(self.import_source, list):
            self.import_wizard.progress_bar.setMaximum(len(self.import_source))
            for source in self.import_source:
                if self.stop_import_flag:
                    return
                self.set_defaults()
                song_data = open(source, 'rb')
                if song_data.read(19).decode() != 'WoW File\nSong Words':
                    self.log_error(source,
                                   str(translate('SongsPlugin.WordsofWorshipSongImport',
                                                 'Invalid Words of Worship song file. Missing "WoW File\\nSong '
                                                 'Words" header.')))
                    continue
                # Seek to byte which stores number of blocks in the song
                song_data.seek(56)
                no_of_blocks = ord(song_data.read(1))
                song_data.seek(66)
                if song_data.read(16).decode() != 'CSongDoc::CBlock':
                    self.log_error(source,
                                   str(translate('SongsPlugin.WordsofWorshipSongImport',
                                                 'Invalid Words of Worship song file. Missing "CSongDoc::CBlock" '
                                                 'string.')))
                    continue
                # Seek to the beginning of the first block
                song_data.seek(82)
                for block in range(no_of_blocks):
                    skip_char_at_end = True
                    self.lines_to_read = ord(song_data.read(4)[:1])
                    block_text = ''
                    while self.lines_to_read:
                        self.line_text = str(song_data.read(ord(song_data.read(1))), 'cp1252')
                        if skip_char_at_end:
                            skip_char = ord(song_data.read(1))
                            # Check if we really should skip a char. In some wsg files we shouldn't
                            if skip_char != 0:
                                song_data.seek(-1, os.SEEK_CUR)
                                skip_char_at_end = False
                        if block_text:
                            block_text += '\n'
                        block_text += self.line_text
                        self.lines_to_read -= 1
                    block_type = BLOCK_TYPES[ord(song_data.read(4)[:1])]
                    # Blocks are separated by 2 bytes, skip them, but not if
                    # this is the last block!
                    if block + 1 < no_of_blocks:
                        song_data.seek(2, os.SEEK_CUR)
                    self.add_verse(block_text, block_type)
                # Now to extract the author
                author_length = ord(song_data.read(1))
                if author_length:
                    self.parse_author(str(song_data.read(author_length), 'cp1252'))
                # Finally the copyright
                copyright_length = ord(song_data.read(1))
                if copyright_length:
                    self.add_copyright(str(song_data.read(copyright_length), 'cp1252'))
                file_name = os.path.split(source)[1]
                # Get the song title
                self.title = file_name.rpartition('.')[0]
                song_data.close()
                if not self.finish():
                    self.log_error(source)
