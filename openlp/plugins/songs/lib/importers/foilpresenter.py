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
The XML of `Foilpresenter <http://foilpresenter.de/>`_  songs is of the format::

    <?xml version="1.0" encoding="UTF-8"?>
    <foilpresenterfolie version="00300.000092">
    <id>2004.6.18.18.44.37.0767</id>
    <lastchanged>2012.1.21.8.53.5</lastchanged>
    <titel>
        <titelstring>Above all</titelstring>
    </titel>
    <sprache>1</sprache>
    <ccliid></ccliid>
    <tonart></tonart>
    <valign>0</valign>
    <notiz>Notiz</notiz>
    <versionsinfo>1.0</versionsinfo>
    <farben>
        <cback>0,0,0</cback>
        <ctext>255,255,255</ctext>
    </farben>
    <reihenfolge>
        <name>Standard</name>
        <strophennummer>0</strophennummer>
    </reihenfolge>
    <strophen>
        <strophe>
            <align>0</align>
            <font>Verdana</font>
            <textsize>14</textsize>
            <bold>0</bold>
            <italic>0</italic>
            <underline>0</underline>
            <key>1</key>
            <text>Above all powers, above all kings,
    above all nature an all created things;
    above all wisdom and all the ways of man,
    You were here before the world began.</text>
            <sortnr>1</sortnr>
        </strophe>
    </strophen>
    <verkn>
        <filename>Herr du bist maechtig.foil</filename>
    </verkn>
    <copyright>
        <font>Arial</font>
        <textsize>7</textsize>
        <anzeigedauer>3</anzeigedauer>
        <bold>0</bold>
        <italic>1</italic>
        <underline>0</underline>
        <text>Text und Musik: Lenny LeBlanc/Paul Baloche</text>
    </copyright>
    <buch>
        <bucheintrag>
            <name>Feiert Jesus 3</name>
            <nummer>10</nummer>
        </bucheintrag>
    </buch>
    <kategorien>
        <name>Worship</name>
    </kategorien>
    </foilpresenterfolie>
"""

import logging
import re
import os

from lxml import etree, objectify

from openlp.core.lib import translate
from openlp.core.ui.wizard import WizardStrings
from openlp.plugins.songs.lib import clean_song, VerseType
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.db import Author, Book, Song, Topic
from openlp.plugins.songs.lib.ui import SongStrings
from openlp.plugins.songs.lib.openlyricsxml import SongXML

log = logging.getLogger(__name__)


class FoilPresenterImport(SongImport):
    """
    This provides the Foilpresenter import.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the import.
        """
        log.debug('initialise FoilPresenterImport')
        SongImport.__init__(self, manager, **kwargs)
        self.foil_presenter = FoilPresenter(self.manager, self)

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
                parsed_file = etree.parse(file_path, parser)
                xml = etree.tostring(parsed_file).decode()
                self.foil_presenter.xml_to_song(xml)
            except etree.XMLSyntaxError:
                self.log_error(file_path, SongStrings.XMLSyntaxError)
                log.exception('XML syntax error in file %s' % file_path)


class FoilPresenter(object):
    """
    This class represents the converter for Foilpresenter XML from a song.

    As Foilpresenter has a rich set of different features, we cannot support
    them all. The following features are supported by the :class:`Foilpresenter`

    OpenPL does not support styletype and font attributes like "align, font,
        textsize, bold, italic, underline"

    *<lastchanged>*
        This property is currently not supported.

    *<title>*
        As OpenLP does only support one title, the first titlestring becomes
            title, all other titlestrings will be alternate titles

    *<sprache>*
        This property is not supported.

    *<ccliid>*
        The *<ccliid>* property is fully supported.

    *<tonart>*
        This property is currently not supported.

    *<valign>*
        This property is not supported.

    *<notiz>*
        The *<notiz>* property is fully supported.

    *<versionsinfo>*
        This property is not supported.

    *<farben>*
        This property is not supported.

    *<reihenfolge>* = verseOrder
        OpenLP supports this property.

    *<strophen>*
        Only the attributes *key* and *text* are supported.

    *<verkn>*
        This property is not supported.

    *<verkn>*
        This property is not supported.

    *<copyright>*
        Only the attribute *text* is supported. => Done

    *<buch>* = songbooks
        As OpenLP does only support one songbook, we cannot consider more than
        one songbook.

    *<kategorien>*
        This property is not supported.

    The tag *<author>* is not support by foilpresenter, mostly the author is
        named in the <copyright> tag. We try to extract the authors from the
        <copyright> tag.

    """
    def __init__(self, manager, importer):
        self.manager = manager
        self.importer = importer

    def xml_to_song(self, xml):
        """
        Create and save a song from Foilpresenter format xml to the database.

        :param xml: The XML to parse (unicode).
        """
        # No xml get out of here.
        if not xml:
            return
        if xml[:5] == '<?xml':
            xml = xml[38:]
        song = Song()
        # Values will be set when cleaning the song.
        song.search_lyrics = ''
        song.verse_order = ''
        song.search_title = ''
        self.save_song = True
        # Because "text" seems to be an reserved word, we have to recompile it.
        xml = re.compile('<text>').sub('<text_>', xml)
        xml = re.compile('</text>').sub('</text_>', xml)
        song_xml = objectify.fromstring(xml)
        self._process_copyright(song_xml, song)
        self._process_cclinumber(song_xml, song)
        self._process_titles(song_xml, song)
        # The verse order is processed with the lyrics!
        self._process_lyrics(song_xml, song)
        self._process_comments(song_xml, song)
        self._process_authors(song_xml, song)
        self._process_songbooks(song_xml, song)
        self._process_topics(song_xml, song)
        if self.save_song:
            clean_song(self.manager, song)
            self.manager.save_object(song)

    def _child(self, element):
        """
        This returns the text of an element as unicode string.

        :param element: The element
        """
        if element is not None:
            return str(element)
        return ''

    def _process_authors(self, foilpresenterfolie, song):
        """
        Adds the authors specified in the XML to the song.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        authors = []
        try:
            copyright = self._child(foilpresenterfolie.copyright.text_)
        except AttributeError:
            copyright = None
        if copyright:
            strings = []
            if copyright.find('Copyright') != -1:
                temp = copyright.partition('Copyright')
                copyright = temp[0]
            elif copyright.find('copyright') != -1:
                temp = copyright.partition('copyright')
                copyright = temp[0]
            elif copyright.find('©') != -1:
                temp = copyright.partition('©')
                copyright = temp[0]
            elif copyright.find('(c)') != -1:
                temp = copyright.partition('(c)')
                copyright = temp[0]
            elif copyright.find('(C)') != -1:
                temp = copyright.partition('(C)')
                copyright = temp[0]
            elif copyright.find('c)') != -1:
                temp = copyright.partition('c)')
                copyright = temp[0]
            elif copyright.find('C)') != -1:
                temp = copyright.partition('C)')
                copyright = temp[0]
            elif copyright.find('C:') != -1:
                temp = copyright.partition('C:')
                copyright = temp[0]
            elif copyright.find('C,)') != -1:
                temp = copyright.partition('C,)')
                copyright = temp[0]
            copyright = re.compile('\\n').sub(' ', copyright)
            copyright = re.compile('\(.*\)').sub('', copyright)
            if copyright.find('Rechte') != -1:
                temp = copyright.partition('Rechte')
                copyright = temp[0]
            markers = ['Text +u\.?n?d? +Melodie[\w\,\. ]*:',
                       'Text +u\.?n?d? +Musik', 'T & M', 'Melodie und Satz',
                       'Text[\w\,\. ]*:', 'Melodie', 'Musik', 'Satz',
                       'Weise', '[dD]eutsch', '[dD]t[\.\:]', 'Englisch',
                       '[oO]riginal', 'Bearbeitung', '[R|r]efrain']
            for marker in markers:
                copyright = re.compile(marker).sub('<marker>', copyright, re.U)
            copyright = re.compile('(?<=<marker>) *:').sub('', copyright)
            x = 0
            while True:
                if copyright.find('<marker>') != -1:
                    temp = copyright.partition('<marker>')
                    if temp[0].strip() and x > 0:
                        strings.append(temp[0])
                    copyright = temp[2]
                    x += 1
                elif x > 0:
                    strings.append(copyright)
                    break
                else:
                    break
            author_temp = []
            for author in strings:
                temp = re.split(',(?=\D{2})|(?<=\D),|\/(?=\D{3,})|(?<=\D);', author)
                for tempx in temp:
                    author_temp.append(tempx)
                for author in author_temp:
                    regex = '^[\/,;\-\s\.]+|[\/,;\-\s\.]+$|\s*[0-9]{4}\s*[\-\/]?\s*([0-9]{4})?[\/,;\-\s\.]*$'
                    author = re.compile(regex).sub('', author)
                    author = re.compile('[0-9]{1,2}\.\s?J(ahr)?h\.|um\s*$|vor\s*$').sub('', author)
                    author = re.compile('[N|n]ach.*$').sub('', author)
                    author = author.strip()
                    if re.search('\w+\.?\s+\w{3,}\s+[a|u]nd\s|\w+\.?\s+\w{3,}\s+&\s', author, re.U):
                        temp = re.split('\s[a|u]nd\s|\s&\s', author)
                        for tempx in temp:
                            tempx = tempx.strip()
                            authors.append(tempx)
                    elif len(author) > 2:
                        authors.append(author)
        for display_name in authors:
            author = self.manager.get_object_filtered(Author, Author.display_name == display_name)
            if author is None:
                # We need to create a new author, as the author does not exist.
                author = Author.populate(display_name=display_name, last_name=display_name.split(' ')[-1],
                                         first_name=' '.join(display_name.split(' ')[:-1]))
                self.manager.save_object(author)
            song.add_author(author)

    def _process_cclinumber(self, foilpresenterfolie, song):
        """
        Adds the CCLI number to the song.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        try:
            song.ccli_number = self._child(foilpresenterfolie.ccliid)
        except AttributeError:
            song.ccli_number = ''

    def _process_comments(self, foilpresenterfolie, song):
        """
        Joins the comments specified in the XML and add it to the song.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        try:
            song.comments = self._child(foilpresenterfolie.notiz)
        except AttributeError:
            song.comments = ''

    def _process_copyright(self, foilpresenterfolie, song):
        """
        Adds the copyright to the song.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        try:
            song.copyright = self._child(foilpresenterfolie.copyright.text_)
        except AttributeError:
            song.copyright = ''

    def _process_lyrics(self, foilpresenterfolie, song):
        """
        Processes the verses and search_lyrics for the song.

        :param foilpresenterfolie: The foilpresenterfolie object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        sxml = SongXML()
        temp_verse_order = {}
        temp_verse_order_backup = []
        temp_sortnr_backup = 1
        temp_sortnr_liste = []
        verse_count = {
            VerseType.tags[VerseType.Verse]: 1,
            VerseType.tags[VerseType.Chorus]: 1,
            VerseType.tags[VerseType.Bridge]: 1,
            VerseType.tags[VerseType.Ending]: 1,
            VerseType.tags[VerseType.Other]: 1,
            VerseType.tags[VerseType.Intro]: 1,
            VerseType.tags[VerseType.PreChorus]: 1
        }
        if not hasattr(foilpresenterfolie.strophen, 'strophe'):
            self.importer.log_error(self._child(foilpresenterfolie.titel),
                                    str(translate('SongsPlugin.FoilPresenterSongImport',
                                                  'Invalid Foilpresenter song file. No verses found.')))
            self.save_song = False
            return
        for strophe in foilpresenterfolie.strophen.strophe:
            text = self._child(strophe.text_) if hasattr(strophe, 'text_') else ''
            verse_name = self._child(strophe.key)
            children = strophe.getchildren()
            sortnr = False
            for child in children:
                if child.tag == 'sortnr':
                    verse_sortnr = self._child(strophe.sortnr)
                    sortnr = True
                # In older Version there is no sortnr, but we need one
            if not sortnr:
                verse_sortnr = str(temp_sortnr_backup)
                temp_sortnr_backup += 1
            # Foilpresenter allows e. g. "Ref" or "1", but we need "C1" or "V1".
            temp_sortnr_liste.append(verse_sortnr)
            temp_verse_name = re.compile('[0-9].*').sub('', verse_name)
            temp_verse_name = temp_verse_name[:3].lower()
            if temp_verse_name == 'ref':
                verse_type = VerseType.tags[VerseType.Chorus]
            elif temp_verse_name == 'r':
                verse_type = VerseType.tags[VerseType.Chorus]
            elif temp_verse_name == '':
                verse_type = VerseType.tags[VerseType.Verse]
            elif temp_verse_name == 'v':
                verse_type = VerseType.tags[VerseType.Verse]
            elif temp_verse_name == 'bri':
                verse_type = VerseType.tags[VerseType.Bridge]
            elif temp_verse_name == 'cod':
                verse_type = VerseType.tags[VerseType.Ending]
            elif temp_verse_name == 'sch':
                verse_type = VerseType.tags[VerseType.Ending]
            elif temp_verse_name == 'pre':
                verse_type = VerseType.tags[VerseType.PreChorus]
            elif temp_verse_name == 'int':
                verse_type = VerseType.tags[VerseType.Intro]
            else:
                verse_type = VerseType.tags[VerseType.Other]
            verse_number = re.compile('[a-zA-Z.+-_ ]*').sub('', verse_name)
            # Foilpresenter allows e. g. "C", but we need "C1".
            if not verse_number:
                verse_number = str(verse_count[verse_type])
                verse_count[verse_type] += 1
            else:
                # test if foilpresenter have the same versenumber two times with
                # different parts raise the verse number
                for value in temp_verse_order_backup:
                    if value == ''.join((verse_type, verse_number)):
                        verse_number = str(int(verse_number) + 1)
            verse_type_index = VerseType.from_tag(verse_type[0])
            verse_type = VerseType.tags[verse_type_index]
            temp_verse_order[verse_sortnr] = ''.join((verse_type[0], verse_number))
            temp_verse_order_backup.append(''.join((verse_type[0], verse_number)))
            sxml.add_verse_to_lyrics(verse_type, verse_number, text)
        song.lyrics = str(sxml.extract_xml(), 'utf-8')
        # Process verse order
        verse_order = []
        verse_strophenr = []
        try:
            for strophennummer in foilpresenterfolie.reihenfolge.strophennummer:
                verse_strophenr.append(strophennummer)
        except AttributeError:
            pass
        # Currently we do not support different "parts"!
        if '0' in temp_verse_order:
            for vers in temp_verse_order_backup:
                verse_order.append(vers)
        else:
            for number in verse_strophenr:
                numberx = temp_sortnr_liste[int(number)]
                verse_order.append(temp_verse_order[str(numberx)])
        song.verse_order = ' '.join(verse_order)

    def _process_songbooks(self, foilpresenterfolie, song):
        """
        Adds the song book and song number specified in the XML to the song.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        song.song_book_id = 0
        song.song_number = ''
        try:
            for bucheintrag in foilpresenterfolie.buch.bucheintrag:
                book_name = self._child(bucheintrag.name)
                if book_name:
                    book = self.manager.get_object_filtered(Book, Book.name == book_name)
                    if book is None:
                        # We need to create a book, because it does not exist.
                        book = Book.populate(name=book_name, publisher='')
                        self.manager.save_object(book)
                    song.song_book_id = book.id
                    try:
                        if self._child(bucheintrag.nummer):
                            song.song_number = self._child(bucheintrag.nummer)
                    except AttributeError:
                        pass
                    # We only support one song book, so take the first one.
                    break
        except AttributeError:
            pass

    def _process_titles(self, foilpresenterfolie, song):
        """
        Processes the titles specified in the song's XML.

        :param foilpresenterfolie: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        try:
            for title_string in foilpresenterfolie.titel.titelstring:
                if not song.title:
                    song.title = self._child(title_string)
                    song.alternate_title = ''
                else:
                    song.alternate_title = self._child(title_string)
        except AttributeError:
            # Use first line of first verse
            first_line = self._child(foilpresenterfolie.strophen.strophe.text_)
            song.title = first_line.split('\n')[0]

    def _process_topics(self, foilpresenterfolie, song):
        """
        Adds the topics to the song.

        :param foilpresenterfolie:  The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        try:
            for name in foilpresenterfolie.kategorien.name:
                topic_text = self._child(name)
                if topic_text:
                    topic = self.manager.get_object_filtered(Topic, Topic.name == topic_text)
                    if topic is None:
                        # We need to create a topic, because it does not exist.
                        topic = Topic.populate(name=topic_text)
                        self.manager.save_object(topic)
                    song.topics.append(topic)
        except AttributeError:
            pass
