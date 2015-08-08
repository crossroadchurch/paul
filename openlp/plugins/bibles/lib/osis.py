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
from lxml import etree

from openlp.core.common import translate, trace_error_handler
from openlp.plugins.bibles.lib.db import BibleDB, BiblesResourcesDB
from openlp.core.lib.ui import critical_error_message_box

log = logging.getLogger(__name__)


def replacement(match):
    return match.group(2).upper()


class OSISBible(BibleDB):
    """
    `OSIS <http://www.bibletechnologies.net/>`_ Bible format importer class.
    """
    log.info('BibleOSISImpl loaded')

    def __init__(self, parent, **kwargs):
        log.debug(self.__class__.__name__)
        BibleDB.__init__(self, parent, **kwargs)
        self.filename = kwargs['filename']

    def do_import(self, bible_name=None):
        """
        Loads a Bible from file.
        """
        log.debug('Starting OSIS import from "%s"' % self.filename)
        if not isinstance(self.filename, str):
            self.filename = str(self.filename, 'utf8')
        import_file = None
        success = True
        try:
            # NOTE: We don't need to do any of the normal encoding detection here, because lxml does it's own encoding
            # detection, and the two mechanisms together interfere with each other.
            import_file = open(self.filename, 'rb')
            osis_bible_tree = etree.parse(import_file, parser=etree.XMLParser(recover=True))
            namespace = {'ns': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}
            # Find bible language
            language_id = None
            language = osis_bible_tree.xpath("//ns:osisText/@xml:lang", namespaces=namespace)
            if language:
                language_id = BiblesResourcesDB.get_language(language[0])
            # The language couldn't be detected, ask the user
            if not language_id:
                language_id = self.get_language(bible_name)
            if not language_id:
                log.error('Importing books from "%s" failed' % self.filename)
                return False
            self.save_meta('language_id', language_id)
            num_books = int(osis_bible_tree.xpath("count(//ns:div[@type='book'])", namespaces=namespace))
            self.wizard.increment_progress_bar(translate('BiblesPlugin.OsisImport',
                                                         'Removing unused tags (this may take a few minutes)...'))
            # We strip unused tags from the XML, this should leave us with only chapter, verse and div tags.
            # Strip tags we don't use - remove content
            etree.strip_elements(osis_bible_tree, ('{http://www.bibletechnologies.net/2003/OSIS/namespace}note',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}milestone',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}title',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}abbr',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}catchWord',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}index',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}rdg',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}rdgGroup',
                                                   '{http://www.bibletechnologies.net/2003/OSIS/namespace}figure'),
                                 with_tail=False)
            # Strip tags we don't use - keep content
            etree.strip_tags(osis_bible_tree, ('{http://www.bibletechnologies.net/2003/OSIS/namespace}p',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}l',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}lg',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}q',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}a',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}w',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}divineName',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}foreign',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}hi',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}inscription',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}mentioned',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}name',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}reference',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}seg',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}transChange',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}salute',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}signed',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}closer',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}speech',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}speaker',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}list',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}item',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}table',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}head',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}row',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}cell',
                                               '{http://www.bibletechnologies.net/2003/OSIS/namespace}caption'))
            # Precompile a few xpath-querys
            verse_in_chapter = etree.XPath('count(//ns:chapter[1]/ns:verse)', namespaces=namespace)
            text_in_verse = etree.XPath('count(//ns:verse[1]/text())', namespaces=namespace)
            # Find books in the bible
            bible_books = osis_bible_tree.xpath("//ns:div[@type='book']", namespaces=namespace)
            for book in bible_books:
                if self.stop_import_flag:
                    break
                # Remove div-tags in the book
                etree.strip_tags(book, ('{http://www.bibletechnologies.net/2003/OSIS/namespace}div'))
                book_ref_id = self.get_book_ref_id_by_name(book.get('osisID'), num_books, language_id)
                if not book_ref_id:
                    book_ref_id = self.get_book_ref_id_by_localised_name(book.get('osisID'))
                if not book_ref_id:
                    log.error('Importing books from "%s" failed' % self.filename)
                    return False
                book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                db_book = self.create_book(book_details['name'], book_ref_id, book_details['testament_id'])
                # Find out if chapter-tags contains the verses, or if it is used as milestone/anchor
                if int(verse_in_chapter(book)) > 0:
                    # The chapter tags contains the verses
                    for chapter in book:
                        chapter_number = chapter.get("osisID").split('.')[1]
                        # Find out if verse-tags contains the text, or if it is used as milestone/anchor
                        if int(text_in_verse(chapter)) == 0:
                            # verse-tags are used as milestone
                            for verse in chapter:
                                # If this tag marks the start of a verse, the verse text is between this tag and
                                # the next tag, which the "tail" attribute gives us.
                                if verse.get('sID'):
                                    verse_number = verse.get("osisID").split('.')[2]
                                    verse_text = verse.tail
                                    if verse_text:
                                        self.create_verse(db_book.id, chapter_number, verse_number, verse_text.strip())
                        else:
                            # Verse-tags contains the text
                            for verse in chapter:
                                verse_number = verse.get("osisID").split('.')[2]
                                if verse.text:
                                    self.create_verse(db_book.id, chapter_number, verse_number, verse.text.strip())
                        self.wizard.increment_progress_bar(
                            translate('BiblesPlugin.OsisImport', 'Importing %(bookname)s %(chapter)s...') %
                            {'bookname': db_book.name, 'chapter': chapter_number})
                else:
                    # The chapter tags is used as milestones. For now we assume verses is also milestones
                    chapter_number = 0
                    for element in book:
                        if element.tag == '{http://www.bibletechnologies.net/2003/OSIS/namespace}chapter' \
                                and element.get('sID'):
                            chapter_number = element.get("osisID").split('.')[1]
                            self.wizard.increment_progress_bar(
                                translate('BiblesPlugin.OsisImport', 'Importing %(bookname)s %(chapter)s...') %
                                {'bookname': db_book.name, 'chapter': chapter_number})
                        elif element.tag == '{http://www.bibletechnologies.net/2003/OSIS/namespace}verse' \
                                and element.get('sID'):
                            # If this tag marks the start of a verse, the verse text is between this tag and
                            # the next tag, which the "tail" attribute gives us.
                            verse_number = element.get("osisID").split('.')[2]
                            verse_text = element.tail
                            if verse_text:
                                self.create_verse(db_book.id, chapter_number, verse_number, verse_text.strip())
                self.session.commit()
            self.application.process_events()
        except (ValueError, IOError):
            log.exception('Loading bible from OSIS file failed')
            trace_error_handler(log)
            success = False
        except etree.XMLSyntaxError as e:
            log.exception('Loading bible from OSIS file failed')
            trace_error_handler(log)
            success = False
            critical_error_message_box(message=translate('BiblesPlugin.OsisImport',
                                                         'The file is not a valid OSIS-XML file: \n%s' % e.msg))
        finally:
            if import_file:
                import_file.close()
        if self.stop_import_flag:
            return False
        else:
            return success
