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
The :mod:`xml` module provides the XML functionality.

The basic XML for storing the lyrics in the song database looks like this::

    <?xml version="1.0" encoding="UTF-8"?>
    <song version="1.0">
        <lyrics>
            <verse type="c" label="1" lang="en">
                <![CDATA[Chorus optional split 1[---]Chorus optional split 2]]>
            </verse>
        </lyrics>
    </song>


The XML of an `OpenLyrics <http://openlyrics.info/>`_  song looks like this::

    <song xmlns="http://openlyrics.info/namespace/2009/song"
        version="0.7"
        createdIn="OpenLP 1.9.0"
        modifiedIn="ChangingSong 0.0.1"
        modifiedDate="2010-01-28T13:15:30+01:00">
    <properties>
        <titles>
            <title>Amazing Grace</title>
        </titles>
    </properties>
        <lyrics>
            <verse name="v1">
                <lines>
                    <line>Amazing grace how sweet the sound</line>
                </lines>
            </verse>
        </lyrics>
    </song>
"""
import html
import logging
import re

from lxml import etree, objectify

from openlp.core.common import translate
from openlp.core.lib import FormattingTags
from openlp.plugins.songs.lib import VerseType, clean_song
from openlp.plugins.songs.lib.db import Author, AuthorType, Book, Song, Topic
from openlp.core.utils import get_application_version

log = logging.getLogger(__name__)

NAMESPACE = 'http://openlyrics.info/namespace/2009/song'
NSMAP = '{' + NAMESPACE + '}' + '%s'


class SongXML(object):
    """
    This class builds and parses the XML used to describe songs.
    """
    log.info('SongXML Loaded')

    def __init__(self):
        """
        Set up the default variables.
        """
        self.song_xml = objectify.fromstring('<song version="1.0" />')
        self.lyrics = etree.SubElement(self.song_xml, 'lyrics')

    def add_verse_to_lyrics(self, type, number, content, lang=None):
        """
        Add a verse to the ``<lyrics>`` tag.

        :param type:  A string denoting the type of verse. Possible values are *v*, *c*, *b*, *p*, *i*, *e* and *o*.
        Any other type is **not** allowed, this also includes translated types.
        :param number: An integer denoting the number of the item, for example: verse 1.
        :param content: The actual text of the verse to be stored.
        :param lang:  The verse's language code (ISO-639). This is not required, but should be added if available.
        """
        verse = etree.Element('verse', type=str(type), label=str(number))
        if lang:
            verse.set('lang', lang)
        verse.text = etree.CDATA(content)
        self.lyrics.append(verse)

    def extract_xml(self):
        """
        Extract our newly created XML song.
        """
        return etree.tostring(self.song_xml, encoding='UTF-8', xml_declaration=True)

    def get_verses(self, xml):
        """
        Iterates through the verses in the XML and returns a list of verses and their attributes.

        :param xml: The XML of the song to be parsed.
        The returned list has the following format::

            [[{'type': 'v', 'label': '1'}, u"optional slide split 1[---]optional slide split 2"],
            [{'lang': 'en', 'type': 'c', 'label': '1'}, u"English chorus"]]
        """
        self.song_xml = None
        verse_list = []
        if not xml.startswith('<?xml') and not xml.startswith('<song'):
            # This is an old style song, without XML. Let's handle it correctly by iterating through the verses, and
            # then recreating the internal xml object as well.
            self.song_xml = objectify.fromstring('<song version="1.0" />')
            self.lyrics = etree.SubElement(self.song_xml, 'lyrics')
            verses = xml.split('\n\n')
            for count, verse in enumerate(verses):
                verse_list.append([{'type': 'v', 'label': str(count)}, str(verse)])
                self.add_verse_to_lyrics('v', str(count), verse)
            return verse_list
        elif xml.startswith('<?xml'):
            xml = xml[38:]
        try:
            self.song_xml = objectify.fromstring(xml)
        except etree.XMLSyntaxError:
            log.exception('Invalid xml %s', xml)
        xml_iter = self.song_xml.getiterator()
        for element in xml_iter:
            if element.tag == 'verse':
                if element.text is None:
                    element.text = ''
                verse_list.append([element.attrib, str(element.text)])
        return verse_list

    def dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return etree.dump(self.song_xml)


class OpenLyrics(object):
    """
    This class represents the converter for OpenLyrics XML (version 0.8) to/from a song.

    As OpenLyrics has a rich set of different features, we cannot support them all. The following features are
    supported by the :class:`OpenLyrics` class:

    ``<authors>``
        OpenLP does not support the attribute *lang*.

    ``<chord>``
        This property is fully supported.

    ``<comments>``
        The ``<comments>`` property is fully supported. But comments in lyrics are not supported.

    ``<copyright>``
        This property is fully supported.

    ``<customVersion>``
        This property is not supported.

    ``<key>``
        This property is fully supported.

    ``<format>``
        The custom formatting tags are fully supported.

    ``<keywords>``
        This property is not supported.

    ``<lines>``
        The attribute *part* is not supported. The *break* attribute is supported.

    ``<publisher>``
        This property is not supported.

    ``<songbooks>``
        As OpenLP does only support one songbook, we cannot consider more than one songbook.

    ``<tempo>``
        This property is not supported.

    ``<themes>``
        Topics, as they are called in OpenLP, are fully supported, whereby only the topic text (e. g. Grace) is
        considered, but neither the *id* nor *lang*.

    ``<transposition>``
        This property is fully supported.

    ``<variant>``
        This property is not supported.

    ``<verse name="v1a" lang="he" translit="en">``
        The attribute *translit* is not supported. Note, the attribute *lang* is considered, but there is not further
        functionality implemented yet. The following verse "types" are supported by OpenLP:

            * v
            * c
            * b
            * p
            * i
            * e
            * o

        The verse "types" stand for *Verse*, *Chorus*, *Bridge*, *Pre-Chorus*, *Intro*, *Ending* and *Other*. Any
        numeric value is allowed after the verse type. The complete verse name in OpenLP always consists of the verse
        type and the verse number. If not number is present *1* is assumed. OpenLP will merge verses which are split
        up by appending a letter to the verse name, such as *v1a*.

    ``<verseOrder>``
        OpenLP supports this property.

    """
    IMPLEMENTED_VERSION = '0.8'
    START_TAGS_REGEX = re.compile(r'\{(\w+)\}')
    END_TAGS_REGEX = re.compile(r'\{\/(\w+)\}')
    VERSE_TAG_SPLITTER = re.compile('([a-zA-Z]+)([0-9]*)([a-zA-Z]?)')

    def __init__(self, manager):
        self.manager = manager
        FormattingTags.load_tags()

    def song_to_xml(self, song):
        """
        Convert the song to OpenLyrics Format.
        """
        sxml = SongXML()
        song_xml = objectify.fromstring('<song/>')
        # Append the necessary meta data to the song.
        song_xml.set('xmlns', NAMESPACE)
        song_xml.set('version', OpenLyrics.IMPLEMENTED_VERSION)
        application_name = 'OpenLP ' + get_application_version()['version']
        song_xml.set('createdIn', application_name)
        song_xml.set('modifiedIn', application_name)
        # "Convert" 2012-08-27 11:49:15 to 2012-08-27T11:49:15.
        song_xml.set('modifiedDate', str(song.last_modified).replace(' ', 'T'))
        properties = etree.SubElement(song_xml, 'properties')
        titles = etree.SubElement(properties, 'titles')
        self._add_text_to_element('title', titles, song.title)
        if song.alternate_title:
            self._add_text_to_element('title', titles, song.alternate_title)
        if song.comments:
            comments = etree.SubElement(properties, 'comments')
            self._add_text_to_element('comment', comments, song.comments)
        if song.copyright:
            self._add_text_to_element('copyright', properties, song.copyright)
        if song.song_key:
            self._add_text_to_element('key', properties, song.song_key)
        if song.transpose_by:
            self._add_text_to_element('transposition', properties, song.transpose_by)
        if song.verse_order:
            self._add_text_to_element(
                'verseOrder', properties, song.verse_order.lower())
        if song.ccli_number:
            self._add_text_to_element('ccliNo', properties, song.ccli_number)
        if song.authors_songs:
            authors = etree.SubElement(properties, 'authors')
            for author_song in song.authors_songs:
                element = self._add_text_to_element('author', authors, author_song.author.display_name)
                if author_song.author_type:
                    # Handle the special case 'words+music': Need to create two separate authors for that
                    if author_song.author_type == AuthorType.WordsAndMusic:
                        element.set('type', AuthorType.Words)
                        element = self._add_text_to_element('author', authors, author_song.author.display_name)
                        element.set('type', AuthorType.Music)
                    else:
                        element.set('type', author_song.author_type)
        book = self.manager.get_object_filtered(Book, Book.id == song.song_book_id)
        if book is not None:
            book = book.name
            songbooks = etree.SubElement(properties, 'songbooks')
            element = self._add_text_to_element('songbook', songbooks, None, book)
            if song.song_number:
                element.set('entry', song.song_number)
        if song.topics:
            themes = etree.SubElement(properties, 'themes')
            for topic in song.topics:
                self._add_text_to_element('theme', themes, topic.name)
        # Process the formatting tags.
        # Have we any tags in song lyrics?
        tags_element = None
        match = re.search('\{/?\w+\}', song.lyrics, re.UNICODE)
        if match:
            # Named 'format_' - 'format' is built-in fuction in Python.
            format_ = etree.SubElement(song_xml, 'format')
            tags_element = etree.SubElement(format_, 'tags')
            tags_element.set('application', 'OpenLP')
        # Process the song's lyrics.
        lyrics = etree.SubElement(song_xml, 'lyrics')
        if song.chords:
            verse_list = sxml.get_verses(song.chords)
        else:
            verse_list = sxml.get_verses(song.lyrics)
        # Add a suffix letter to each verse
        verse_tags = []
        for verse in verse_list:
            verse_tag = verse[0]['type'][0].lower()
            verse_number = verse[0]['label']
            verse_def = verse_tag + verse_number
            # Create the letter from the number of duplicates
            verse[0][u'suffix'] = chr(97 + (verse_tags.count(verse_def) % 26))
            verse_tags.append(verse_def)
        # If the verse tag is a duplicate use the suffix letter
        for verse in verse_list:
            verse_tag = verse[0]['type'][0].lower()
            verse_number = verse[0]['label']
            verse_def = verse_tag + verse_number
            if verse_tags.count(verse_def) > 1:
                verse_def += verse[0]['suffix']
            verse_element = self._add_text_to_element('verse', lyrics, None, verse_def)
            if 'lang' in verse[0]:
                verse_element.set('lang', verse[0]['lang'])
            # Create a list with all "optional" verses.
            # Don't html.escape the chord tags
            optional_verses = ''
            for lyric_chord_part in re.split('(<[\w\+#"=// ]* />)', verse[1]):
                if lyric_chord_part.startswith('<'):
                    optional_verses += lyric_chord_part
                else:
                    optional_verses += html.escape(lyric_chord_part)
            optional_verses = optional_verses.split('\n[---]\n')
            start_tags = ''
            end_tags = ''
            for index, optional_verse in enumerate(optional_verses):
                # Fix up missing end and start tags such as {r} or {/r}.
                optional_verse = start_tags + optional_verse
                start_tags, end_tags = self._get_missing_tags(optional_verse)
                optional_verse += end_tags
                # Add formatting tags to text
                lines_element = self._add_text_with_tags_to_lines(verse_element, optional_verse, tags_element)
                # Do not add the break attribute to the last lines element.
                if index < len(optional_verses) - 1:
                    lines_element.set('break', 'optional')
        return self._extract_xml(song_xml).decode()

    def _get_missing_tags(self, text):
        """
        Tests the given text for not closed formatting tags and returns a tuple consisting of two unicode strings::

            ('{st}{r}', '{/r}{/st}')

        The first unicode string are the start tags (for the next slide). The second unicode string are the end tags.

        :param text: The text to test. The text must **not** contain html tags, only OpenLP formatting tags
        are allowed::

                {st}{r}Text text text
        """
        tags = []
        for tag in FormattingTags.get_html_tags():
            if tag['start tag'] == '{br}':
                continue
            if text.count(tag['start tag']) != text.count(tag['end tag']):
                tags.append((text.find(tag['start tag']), tag['start tag'], tag['end tag']))
        # Sort the lists, so that the tags which were opened first on the first slide (the text we are checking) will
        # be opened first on the next slide as well.
        tags.sort(key=lambda tag: tag[0])
        end_tags = []
        start_tags = []
        for tag in tags:
            start_tags.append(tag[1])
            end_tags.append(tag[2])
        end_tags.reverse()
        return ''.join(start_tags), ''.join(end_tags)

    def xml_to_song(self, xml, parse_and_temporary_save=False):
        """
        Create and save a song from OpenLyrics format xml to the database. Since we also export XML from external
        sources (e. g. OpenLyrics import), we cannot ensure, that it completely conforms to the OpenLyrics standard.

        :param xml: The XML to parse (unicode).
        :param parse_and_temporary_save: Switch to skip processing the whole song and storing the songs in the database
        with a temporary flag. Defaults to ``False``.
        """
        # No xml get out of here.
        if not xml:
            return None
        if xml[:5] == '<?xml':
            xml = xml[38:]
        song_xml = objectify.fromstring(xml)
        if hasattr(song_xml, 'properties'):
            properties = song_xml.properties
        else:
            return None
        # Formatting tags are new in OpenLyrics 0.8
        if float(song_xml.get('version')) > 0.7:
            self._process_formatting_tags(song_xml, parse_and_temporary_save)
        song = Song()
        # Values will be set when cleaning the song.
        song.search_lyrics = ''
        song.verse_order = ''
        song.search_title = ''
        song.temporary = parse_and_temporary_save
        self._process_copyright(properties, song)
        self._process_cclinumber(properties, song)
        self._process_song_key(properties, song)
        self._process_transpose(properties, song)
        self._process_titles(properties, song)
        # The verse order is processed with the lyrics!
        self._process_lyrics(properties, song_xml, song)
        self._process_comments(properties, song)
        self._process_authors(properties, song)
        self._process_songbooks(properties, song)
        self._process_topics(properties, song)
        clean_song(self.manager, song)
        self.manager.save_object(song)
        return song

    def _add_text_to_element(self, tag, parent, text=None, label=None):
        """
        Build an element

        :param tag: A Tag
        :param parent: Its parent
        :param text: Some text to be added
        :param label: And a label
        :return:
        """
        if label:
            element = etree.Element(tag, name=str(label))
        else:
            element = etree.Element(tag)
        if text:
            element.text = str(text)
        parent.append(element)
        return element

    def _add_tag_to_formatting(self, tag_name, tags_element):
        """
        Add new formatting tag to the element ``<format>`` if the tag is not present yet.

        :param tag_name: The tag_name
        :param tags_element: Some tag elements
        """
        available_tags = FormattingTags.get_html_tags()
        start_tag = '{%s}' % tag_name
        for tag in available_tags:
            if tag['start tag'] == start_tag:
                # Create new formatting tag in openlyrics xml.
                element = self._add_text_to_element('tag', tags_element)
                element.set('name', tag_name)
                element_open = self._add_text_to_element('open', element)
                element_open.text = etree.CDATA(tag['start html'])
                # Check if formatting tag contains end tag. Some formatting
                # tags e.g. {br} has only start tag. If no end tag is present
                # <close> element has not to be in OpenLyrics xml.
                if tag['end tag']:
                    element_close = self._add_text_to_element('close', element)
                    element_close.text = etree.CDATA(tag['end html'])

    def _add_text_with_tags_to_lines(self, verse_element, text, tags_element):
        """
        Convert text with formatting tags from OpenLP format to OpenLyrics format and append it to element ``<lines>``.
        """
        start_tags = OpenLyrics.START_TAGS_REGEX.findall(text)
        end_tags = OpenLyrics.END_TAGS_REGEX.findall(text)
        # Replace start tags with xml syntax.
        for tag in start_tags:
            # Tags already converted to xml structure.
            xml_tags = tags_element.xpath('tag/attribute::name')
            # Some formatting tag has only starting part e.g. <br>. Handle this case.
            if tag in end_tags:
                text = text.replace('{%s}' % tag, '<tag name="%s">' % tag)
            else:
                text = text.replace('{%s}' % tag, '<tag name="%s"/>' % tag)
            # Add tag to <format> element if tag not present.
            if tag not in xml_tags:
                self._add_tag_to_formatting(tag, tags_element)
        # Replace end tags.
        for tag in end_tags:
            text = text.replace('{/%s}' % tag, '</tag>')
        # Replace \n with <br/>.
        text = text.replace('\n', '<br/>')
        element = etree.XML('<lines>%s</lines>' % text)
        verse_element.append(element)
        return element

    def _extract_xml(self, xml):
        """
        Extract our newly created XML song.

        :param xml: The XML
        """
        return etree.tostring(xml, encoding='UTF-8', xml_declaration=True)

    def _text(self, element):
        """
        This returns the text of an element as unicode string.

        :param element: The element.
        """
        if element.text is not None:
            return str(element.text)
        return ''

    def _process_authors(self, properties, song):
        """
        Adds the authors specified in the XML to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object
        """
        authors = []
        if hasattr(properties, 'authors'):
            for author in properties.authors.author:
                display_name = self._text(author)
                author_type = author.get('type', '')
                # As of 0.8 OpenLyrics supports these 3 author types
                if author_type not in ('words', 'music', 'translation'):
                    author_type = ''
                if display_name:
                    # Check if an author is listed for both music and words. In that case we use a special type
                    if author_type == 'words' and (display_name, 'music') in authors:
                        authors.remove((display_name, 'music'))
                        authors.append((display_name, 'words+music'))
                    elif author_type == 'music' and (display_name, 'words') in authors:
                        authors.remove((display_name, 'words'))
                        authors.append((display_name, 'words+music'))
                    else:
                        authors.append((display_name, author_type))
        for (display_name, author_type) in authors:
            author = self.manager.get_object_filtered(Author, Author.display_name == display_name)
            if author is None:
                # We need to create a new author, as the author does not exist.
                author = Author.populate(display_name=display_name,
                                         last_name=display_name.split(' ')[-1],
                                         first_name=' '.join(display_name.split(' ')[:-1]))
            song.add_author(author, author_type)

    def _process_cclinumber(self, properties, song):
        """
        Adds the CCLI number to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'ccliNo'):
            song.ccli_number = self._text(properties.ccliNo)

    def _process_comments(self, properties, song):
        """
        Joins the comments specified in the XML and add it to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'comments'):
            comments_list = []
            for comment in properties.comments.comment:
                comment_text = self._text(comment)
                if comment_text:
                    comments_list.append(comment_text)
            song.comments = '\n'.join(comments_list)

    def _process_copyright(self, properties, song):
        """
        Adds the copyright to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'copyright'):
            song.copyright = self._text(properties.copyright)

    def _process_formatting_tags(self, song_xml, temporary):
        """
        Process the formatting tags from the song and either add missing tags temporary or permanently to the
        formatting tag list.

        :param song_xml: The song XML
        :param temporary: Is the song temporary?
        """
        if not hasattr(song_xml, 'format'):
            return
        found_tags = []
        for tag in song_xml.format.tags.getchildren():
            name = tag.get('name')
            if name is None:
                continue
            start_tag = '{%s}' % name[:5]
            # Some tags have only start tag e.g. {br}
            end_tag = '{/' + name[:5] + '}' if hasattr(tag, 'close') else ''
            openlp_tag = {
                'desc': name,
                'start tag': start_tag,
                'end tag': end_tag,
                'start html': tag.open.text,
                # Some tags have only start html e.g. {br}
                'end html': tag.close.text if hasattr(tag, 'close') else '',
                'protected': False,
                # Add 'temporary' key in case the formatting tag should not be saved otherwise it is supposed that
                # formatting tag is permanent.
                'temporary': temporary
            }
            found_tags.append(openlp_tag)
        existing_tag_ids = [tag['start tag'] for tag in FormattingTags.get_html_tags()]
        new_tags = [tag for tag in found_tags if tag['start tag'] not in existing_tag_ids]
        # Do not save an empty list.
        if new_tags:
            FormattingTags.add_html_tags(new_tags)
            if not temporary:
                custom_tags = [tag for tag in FormattingTags.get_html_tags()
                               if not tag['protected'] and not tag['temporary']]
                FormattingTags.save_html_tags(custom_tags)

    def _process_lines_mixed_content(self, element, newlines=True):
        """
        Converts the xml text with mixed content to OpenLP representation. Chords are included and formatting tags are
        converted.

        :param element: The property object (lxml.etree.Element).
        :param newlines: The switch to enable/disable processing of line breaks <br/>. The <br/> is used since
        OpenLyrics 0.8.
        """
        text = ''
        use_endtag = True
        # Skip <comment> elements - not yet supported.
        if element.tag == NSMAP % 'comment':
            if element.tail:
                # Append tail text at chord element.
                text += element.tail
            return text
        # Process <chord> element.
        elif element.tag == NSMAP % 'chord':
            text += '<chord name = \"' + element.get('name') + '\" />'

            if element.tail:
                # Append tail text at chord element.
                text += element.tail
            return text
        # Convert line breaks <br/> to \n.
        elif newlines and element.tag == NSMAP % 'br':
            text += '\n'
            if element.tail:
                text += element.tail
            return text
        # Start formatting tag.
        if element.tag == NSMAP % 'tag':
            text += '{%s}' % element.get('name')
            # Some formattings may have only start tag.
            # Handle this case if element has no children and contains no text.
            if not element and not element.text:
                use_endtag = False
        # Append text from element.
        if element.text:
            text += element.text
        # Process nested formatting tags.
        for child in element:
            # Use recursion since nested formatting tags are allowed.
            text += self._process_lines_mixed_content(child, newlines)
        # Append text from tail and add formatting end tag.
        if element.tag == NSMAP % 'tag' and use_endtag:
            text += '{/%s}' % element.get('name')
        # Append text from tail.
        if element.tail:
            text += element.tail
        return text

    def _process_song_key(self, properties, song):
        """
        Adds the key to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'key'):
            song.song_key = self._text(properties.key)

    def _process_transpose(self, properties, song):
        """
        Adds the transposition amount to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'transposition'):
            song.transpose_by = self._text(properties.transposition)

    def _process_verse_lines(self, lines, version):
        """
        Converts lyrics lines to OpenLP representation.

        :param lines: The lines object (lxml.objectify.ObjectifiedElement).
        :param version:
        """
        text = ''
        # Convert lxml.objectify to lxml.etree representation.
        lines = etree.tostring(lines)
        element = etree.XML(lines)

        # OpenLyrics 0.8 uses <br/> for new lines. Append text from "lines" element to verse text.
        if version > '0.7':
            text = self._process_lines_mixed_content(element)
        # OpenLyrics version <= 0.7 contains <line> elements to represent lines. First child element is tested.
        else:
            # Loop over the "line" elements removing comments and chords.
            for line in element:
                # Skip comment lines.
                if line.tag == NSMAP % 'comment':
                    continue
                if text:
                    text += '\n'
                text += self._process_lines_mixed_content(line, newlines=False)
        return text

    def _process_lyrics(self, properties, song_xml, song_obj):
        """
        Processes the verses and search_lyrics for the song.

        :param properties: The properties object (lxml.objectify.ObjectifiedElement).
        :param song_xml: The objectified song (lxml.objectify.ObjectifiedElement).
        :param song_obj: The song object.
        """
        sxml = SongXML()
        verses = {}
        verse_def_list = []
        verse_order = self._text(properties.verseOrder).split(' ') if hasattr(properties, 'verseOrder') else []
        try:
            lyrics = song_xml.lyrics
        except AttributeError:
            raise OpenLyricsError(OpenLyricsError.LyricsError, '<lyrics> tag is missing.',
                                  translate('OpenLP.OpenLyricsImportError', '<lyrics> tag is missing.'))
        try:
            verse_list = lyrics.verse
        except AttributeError:
            raise OpenLyricsError(OpenLyricsError.VerseError, '<verse> tag is missing.',
                                  translate('OpenLP.OpenLyricsImportError', '<verse> tag is missing.'))
        # Loop over the "verse" elements.
        for verse in verse_list:
            text = ''
            # Loop over the "lines" elements.
            for lines in verse.lines:
                if text:
                    text += '\n'
                # Append text from "lines" element to verse text.
                text += self._process_verse_lines(lines, version=song_xml.get('version'))
                # Add an optional split to the verse text.
                if lines.get('break') is not None:
                    text += '\n[---]'
            verse_def = verse.get('name', ' ').lower()
            verse_tag, verse_number, verse_part = OpenLyrics.VERSE_TAG_SPLITTER.search(verse_def).groups()
            if verse_tag not in VerseType.tags:
                verse_tag = VerseType.tags[VerseType.Other]
            # OpenLyrics allows e. g. "c", but we need "c1". However, this does not correct the verse order.
            if not verse_number:
                verse_number = '1'
            lang = verse.get('lang')
            translit = verse.get('translit')
            # In OpenLP 1.9.6 we used v1a, v1b ... to represent visual slide breaks. In OpenLyrics 0.7 an attribute has
            # been added.
            if song_xml.get('modifiedIn') in ('1.9.6', 'OpenLP 1.9.6') and \
                    song_xml.get('version') == '0.7' and (verse_tag, verse_number, lang, translit) in verses:
                verses[(verse_tag, verse_number, lang, translit, None)] += '\n[---]\n' + text
            # Merge v1a, v1b, .... to v1.
            elif (verse_tag, verse_number, lang, translit, verse_part) in verses:
                verses[(verse_tag, verse_number, lang, translit, verse_part)] += '\n' + text
            else:
                verses[(verse_tag, verse_number, lang, translit, verse_part)] = text
                verse_def_list.append((verse_tag, verse_number, lang, translit, verse_part))
            # Update verse order when the verse name has changed
            if verse_def != verse_tag + verse_number + verse_part:
                for i in range(len(verse_order)):
                    if verse_order[i] == verse_def:
                        verse_order[i] = verse_tag + verse_number + verse_part
        # We have to use a list to keep the order, as dicts are not sorted.
        for verse in verse_def_list:
            sxml.add_verse_to_lyrics(verse[0], verse[1], verses[verse], verse[2])

        # Determine if song has chords - if so store both chords and lyrics
        if(str(sxml.extract_xml(), 'utf-8').find('<chord') > -1):
            song_obj.chords = str(sxml.extract_xml(), 'utf-8')
            # Remove chord tags and store in lyrics
            song_obj.lyrics = ''.join(re.split('<chord[\w\+#"=// ]* />', str(sxml.extract_xml(), 'utf-8')))
        else:
            song_obj.lyrics = str(sxml.extract_xml(), 'utf-8')

        # Process verse order
        song_obj.verse_order = ' '.join(verse_order)

    def _process_songbooks(self, properties, song):
        """
        Adds the song book and song number specified in the XML to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        song.song_book_id = None
        song.song_number = ''
        if hasattr(properties, 'songbooks'):
            for songbook in properties.songbooks.songbook:
                book_name = songbook.get('name', '')
                if book_name:
                    book = self.manager.get_object_filtered(Book, Book.name == book_name)
                    if book is None:
                        # We need to create a book, because it does not exist.
                        book = Book.populate(name=book_name, publisher='')
                        self.manager.save_object(book)
                    song.song_book_id = book.id
                    song.song_number = songbook.get('entry', '')
                    # We only support one song book, so take the first one.
                    break

    def _process_titles(self, properties, song):
        """
        Processes the titles specified in the song's XML.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        for title in properties.titles.title:
            if not song.title:
                song.title = self._text(title)
                song.alternate_title = ''
            else:
                song.alternate_title = self._text(title)

    def _process_topics(self, properties, song):
        """
        Adds the topics to the song.

        :param properties: The property object (lxml.objectify.ObjectifiedElement).
        :param song: The song object.
        """
        if hasattr(properties, 'themes'):
            for topic_text in properties.themes.theme:
                topic_text = self._text(topic_text)
                if topic_text:
                    topic = self.manager.get_object_filtered(Topic, Topic.name == topic_text)
                    if topic is None:
                        # We need to create a topic, because it does not exist.
                        topic = Topic.populate(name=topic_text)
                        self.manager.save_object(topic)
                    song.topics.append(topic)

    def _dump_xml(self, xml):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return etree.tostring(xml, encoding='UTF-8', xml_declaration=True, pretty_print=True)


    def song_to_line_dict(self, song):

        song_xml = SongXML()
        if song.chords:
            verse_chords_xml = song_xml.get_verses(song.chords)
        else:
            verse_chords_xml = song_xml.get_verses(song.lyrics)

        section_line_dict = {}
        for count, verse in enumerate(verse_chords_xml):
            # This silently migrates from localized verse type markup.
            # If we trusted the database, this would be unnecessary.
            verse_tag = verse[0]['type']
            index = None
            if len(verse_tag) > 1:
                index = VerseType.from_translated_string(verse_tag)
                if index is None:
                    index = VerseType.from_string(verse_tag, None)
                else:
                    verse_tags_translated = True
            if index is None:
                index = VerseType.from_tag(verse_tag)
            verse[0]['type'] = VerseType.tags[index]
            if verse[0]['label'] == '':
                verse[0]['label'] = '1'
            section_header = '%s%s' % (verse[0]['type'], verse[0]['label'])

            line_list = []
            for line in verse[1].split('\n'):
                line_list.append(line)

            section_line_dict[section_header] = line_list

        return section_line_dict


class OpenLyricsError(Exception):
    # XML tree is missing the lyrics tag
    LyricsError = 1
    # XML tree has no verse tags
    VerseError = 2

    def __init__(self, type, log_message, display_message):
        super(OpenLyricsError, self).__init__()
        self.type = type
        self.log_message = log_message
        self.display_message = display_message
