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
The :mod:`dreambeam` module provides the functionality for importing DreamBeam songs into the OpenLP database.
"""
import logging

from lxml import etree, objectify

from openlp.core.lib import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class DreamBeamImport(SongImport):
    """
    The :class:`DreamBeamImport` class provides the ability to import song files from
    DreamBeam.

    An example of DreamBeam xml mark-up::

        <?xml version="1.0"?>
        <DreamSong xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
          <WordWrap>false</WordWrap>
          <Version>0.80</Version>
          <Title>Amazing Grace</Title>
          <Author>John Newton</Author>
          <Collection />
          <Number />
          <Notes />
          <KeyRangeLow>F</KeyRangeLow>
          <KeyRangeHigh>G</KeyRangeHigh>
          <MinorKey>false</MinorKey>
          <DualLanguage>false</DualLanguage>
          <SongLyrics>
            <LyricsItem Type="Verse" Number="1">Amazing Grace, how sweet the sound,
            That saved a wretch like me.
            I once was lost but now am found,
            Was blind, but now, I see.</LyricsItem>
            <LyricsItem Type="Verse" Number="2">T’was Grace that taught my heart to fear.
            And Grace, my fears relieved.
            How precious did that Grace appear…
            the hour I first believed.</LyricsItem>
          </SongLyrics>
          <Sequence>
            <LyricsSequenceItem Type="Verse" Number="1" />
            <LyricsSequenceItem Type="Verse" Number="2" />
          </Sequence>
          <ShowRectangles>false</ShowRectangles>
        </DreamSong>

    Valid extensions for a DreamBeam song file are:

        * \*.xml
    """

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if isinstance(self.import_source, list):
            self.import_wizard.progress_bar.setMaximum(len(self.import_source))
            for file in self.import_source:
                if self.stop_import_flag:
                    return
                self.set_defaults()
                parser = etree.XMLParser(remove_blank_text=True)
                try:
                    parsed_file = etree.parse(open(file, 'r'), parser)
                except etree.XMLSyntaxError:
                    log.exception('XML syntax error in file %s' % file)
                    self.log_error(file, SongStrings.XMLSyntaxError)
                    continue
                xml = etree.tostring(parsed_file).decode()
                song_xml = objectify.fromstring(xml)
                if song_xml.tag != 'DreamSong':
                    self.log_error(
                        file,
                        translate('SongsPlugin.DreamBeamImport', 'Invalid DreamBeam song file. Missing DreamSong tag.'))
                    continue
                if hasattr(song_xml, 'Version'):
                    self.version = float(song_xml.Version.text)
                else:
                    self.version = 0
                # Version numbers found in DreamBeam Source /FileTypes/Song.cs
                if self.version >= 0.5:
                    if hasattr(song_xml, 'Title'):
                        self.title = str(song_xml.Title.text)
                    if hasattr(song_xml, 'Author'):
                        author_copyright = song_xml.Author.text
                    if hasattr(song_xml, 'SongLyrics'):
                        for lyrics_item in song_xml.SongLyrics.iterchildren():
                            verse_type = lyrics_item.get('Type')
                            verse_number = lyrics_item.get('Number')
                            verse_text = str(lyrics_item.text)
                            self.add_verse(verse_text, ('%s%s' % (verse_type[:1], verse_number)))
                    if hasattr(song_xml, 'Collection'):
                        self.song_book_name = str(song_xml.Collection.text)
                    if hasattr(song_xml, 'Number'):
                        self.song_number = str(song_xml.Number.text)
                    if hasattr(song_xml, 'Sequence'):
                        for lyrics_sequence_item in (song_xml.Sequence.iterchildren()):
                            self.verse_order_list.append("%s%s" % (lyrics_sequence_item.get('Type')[:1],
                                                         lyrics_sequence_item.get('Number')))
                    if hasattr(song_xml, 'Notes'):
                        self.comments = str(song_xml.Notes.text)
                else:
                    if hasattr(song_xml.Text0, 'Text'):
                        self.title = str(song_xml.Text0.Text.text)
                    if hasattr(song_xml.Text1, 'Text'):
                        self.lyrics = str(song_xml.Text1.Text.text)
                        for verse in self.lyrics.split('\n\n\n'):
                            self.add_verse(verse)
                    if hasattr(song_xml.Text2, 'Text'):
                        author_copyright = song_xml.Text2.Text.text
                if author_copyright:
                    author_copyright = str(author_copyright)
                    if author_copyright.find(str(SongStrings.CopyrightSymbol)) >= 0:
                        self.add_copyright(author_copyright)
                    else:
                        self.parse_author(author_copyright)
                if not self.finish():
                    self.log_error(file)
