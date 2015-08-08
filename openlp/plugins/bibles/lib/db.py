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

import chardet
import logging
import os
import re
import sqlite3
import time

from PyQt4 import QtCore
from sqlalchemy import Column, ForeignKey, Table, or_, types, func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import class_mapper, mapper, relation
from sqlalchemy.orm.exc import UnmappedClassError

from openlp.core.common import Registry, RegistryProperties, AppLocation, translate
from openlp.core.lib.db import BaseModel, init_db, Manager
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.utils import clean_filename
from . import upgrade

log = logging.getLogger(__name__)

RESERVED_CHARACTERS = '\\.^$*+?{}[]()'


class BibleMeta(BaseModel):
    """
    Bible Meta Data
    """
    pass


class Book(BaseModel):
    """
    Song model
    """
    pass


class Verse(BaseModel):
    """
    Topic model
    """
    pass


def init_schema(url):
    """
    Setup a bible database connection and initialise the database schema.

    :param url: The database to setup.
    """
    session, metadata = init_db(url)

    meta_table = Table('metadata', metadata,
                       Column('key', types.Unicode(255), primary_key=True, index=True),
                       Column('value', types.Unicode(255)),)

    book_table = Table('book', metadata,
                       Column('id', types.Integer, primary_key=True),
                       Column('book_reference_id', types.Integer, index=True),
                       Column('testament_reference_id', types.Integer),
                       Column('name', types.Unicode(50), index=True),)
    verse_table = Table('verse', metadata,
                        Column('id', types.Integer, primary_key=True, index=True),
                        Column('book_id', types.Integer, ForeignKey(
                            'book.id'), index=True),
                        Column('chapter', types.Integer, index=True),
                        Column('verse', types.Integer, index=True),
                        Column('text', types.UnicodeText, index=True),)

    try:
        class_mapper(BibleMeta)
    except UnmappedClassError:
        mapper(BibleMeta, meta_table)
    try:
        class_mapper(Book)
    except UnmappedClassError:
        mapper(Book, book_table, properties={'verses': relation(Verse, backref='book')})
    try:
        class_mapper(Verse)
    except UnmappedClassError:
        mapper(Verse, verse_table)

    metadata.create_all(checkfirst=True)
    return session


class BibleDB(QtCore.QObject, Manager, RegistryProperties):
    """
    This class represents a database-bound Bible. It is used as a base class for all the custom importers, so that
    the can implement their own import methods, but benefit from the database methods in here via inheritance,
    rather than depending on yet another object.
    """
    log.info('BibleDB loaded')

    def __init__(self, parent, **kwargs):
        """
        The constructor loads up the database and creates and initialises the
        tables if the database doesn't exist.

        :param parent:
        :param kwargs:
            ``path``
                The path to the bible database file.

            ``name``
                The name of the database. This is also used as the file name for SQLite databases.
        """
        log.info('BibleDB loaded')
        QtCore.QObject.__init__(self)
        self.bible_plugin = parent
        self.session = None
        if 'path' not in kwargs:
            raise KeyError('Missing keyword argument "path".')
        if 'name' not in kwargs and 'file' not in kwargs:
            raise KeyError('Missing keyword argument "name" or "file".')
        self.stop_import_flag = False
        if 'name' in kwargs:
            self.name = kwargs['name']
            if not isinstance(self.name, str):
                self.name = str(self.name, 'utf-8')
            self.file = clean_filename(self.name) + '.sqlite'
        if 'file' in kwargs:
            self.file = kwargs['file']
        Manager.__init__(self, 'bibles', init_schema, self.file, upgrade)
        if self.session and 'file' in kwargs:
                self.get_name()
        if 'path' in kwargs:
            self.path = kwargs['path']
        self.wizard = None
        Registry().register_function('openlp_stop_wizard', self.stop_import)

    def stop_import(self):
        """
        Stops the import of the Bible.
        """
        log.debug('Stopping import')
        self.stop_import_flag = True

    def get_name(self):
        """
        Returns the version name of the Bible.
        """
        version_name = self.get_object(BibleMeta, 'name')
        self.name = version_name.value if version_name else None
        return self.name

    def register(self, wizard):
        """
        This method basically just initialises the database. It is called from the Bible Manager when a Bible is
        imported. Descendant classes may want to override this method to supply their own custom
        initialisation as well.

        :param wizard: The actual Qt wizard form.
        """
        self.wizard = wizard
        return self.name

    def create_book(self, name, bk_ref_id, testament=1):
        """
        Add a book to the database.

        :param name: The name of the book.
        :param bk_ref_id: The book_reference_id from bibles_resources.sqlite of the book.
        :param testament: *Defaults to 1.* The testament_reference_id from
            bibles_resources.sqlite of the testament this book belongs to.
        """
        log.debug('BibleDB.create_book("%s", "%s")' % (name, bk_ref_id))
        book = Book.populate(name=name, book_reference_id=bk_ref_id, testament_reference_id=testament)
        self.save_object(book)
        return book

    def update_book(self, book):
        """
        Update a book in the database.

        :param book: The book object
        """
        log.debug('BibleDB.update_book("%s")' % book.name)
        return self.save_object(book)

    def delete_book(self, db_book):
        """
        Delete a book from the database.

        :param db_book: The book object.
        """
        log.debug('BibleDB.delete_book("%s")' % db_book.name)
        if self.delete_object(Book, db_book.id):
            return True
        return False

    def create_chapter(self, book_id, chapter, text_list):
        """
        Add a chapter and its verses to a book.

        :param book_id: The id of the book being appended.
        :param chapter: The chapter number.
        :param text_list: A dict of the verses to be inserted. The key is the verse number, and the value is the
        verse text.
        """
        log.debug('BibleDBcreate_chapter("%s", "%s")' % (book_id, chapter))
        # Text list has book and chapter as first two elements of the array.
        for verse_number, verse_text in text_list.items():
            verse = Verse.populate(
                book_id=book_id,
                chapter=chapter,
                verse=verse_number,
                text=verse_text
            )
            self.session.add(verse)
        try:
            self.session.commit()
        except OperationalError:
            # Wait 10ms and try again (lp#1154467)
            time.sleep(0.01)
            self.session.commit()

    def create_verse(self, book_id, chapter, verse, text):
        """
        Add a single verse to a chapter.

        :param book_id: The id of the book being appended.
        :param chapter: The chapter number.
        :param verse: The verse number.
        :param text: The verse text.
        """
        if not isinstance(text, str):
            details = chardet.detect(text)
            text = str(text, details['encoding'])
        verse = Verse.populate(
            book_id=book_id,
            chapter=chapter,
            verse=verse,
            text=text
        )
        self.session.add(verse)
        return verse

    def save_meta(self, key, value):
        """
        Utility method to save or update BibleMeta objects in a Bible database.

        :param key: The key for this instance.
        :param value: The value for this instance.
        """
        if not isinstance(value, str):
            value = str(value)
        log.debug('BibleDB.save_meta("%s/%s")' % (key, value))
        meta = self.get_object(BibleMeta, key)
        if meta:
            meta.value = value
            self.save_object(meta)
        else:
            self.save_object(BibleMeta.populate(key=key, value=value))

    def get_book(self, book):
        """
        Return a book object from the database.

        :param book: The name of the book to return.
        """
        log.debug('BibleDB.get_book("%s")' % book)
        return self.get_object_filtered(Book, Book.name.like(book + '%'))

    def get_books(self):
        """
        A wrapper so both local and web bibles have a get_books() method that
        manager can call. Used in the media manager advanced search tab.
        """
        log.debug('BibleDB.get_books()')
        return self.get_all_objects(Book, order_by_ref=Book.id)

    def get_book_by_book_ref_id(self, ref_id):
        """
        Return a book object from the database.

        :param ref_id: The reference id of the book to return.
        """
        log.debug('BibleDB.get_book_by_book_ref_id("%s")' % ref_id)
        return self.get_object_filtered(Book, Book.book_reference_id.like(ref_id))

    def get_book_ref_id_by_name(self, book, maxbooks, language_id=None):
        log.debug('BibleDB.get_book_ref_id_by_name:("%s", "%s")' % (book, language_id))
        book_id = None
        if BiblesResourcesDB.get_book(book, True):
            book_temp = BiblesResourcesDB.get_book(book, True)
            book_id = book_temp['id']
        elif BiblesResourcesDB.get_alternative_book_name(book):
            book_id = BiblesResourcesDB.get_alternative_book_name(book)
        elif AlternativeBookNamesDB.get_book_reference_id(book):
            book_id = AlternativeBookNamesDB.get_book_reference_id(book)
        else:
            from openlp.plugins.bibles.forms import BookNameForm
            book_name = BookNameForm(self.wizard)
            if book_name.exec_(book, self.get_books(), maxbooks):
                book_id = book_name.book_id
            if book_id:
                AlternativeBookNamesDB.create_alternative_book_name(
                    book, book_id, language_id)
        return book_id

    def get_book_ref_id_by_localised_name(self, book, language_selection):
        """
        Return the id of a named book.

        :param book: The name of the book, according to the selected language.
        :param language_selection:  The language selection the user has chosen in the settings section of the Bible.
        """
        log.debug('get_book_ref_id_by_localised_name("%s", "%s")' % (book, language_selection))
        from openlp.plugins.bibles.lib import LanguageSelection, BibleStrings
        book_names = BibleStrings().BookNames
        # escape reserved characters
        book_escaped = book
        for character in RESERVED_CHARACTERS:
            book_escaped = book_escaped.replace(character, '\\' + character)
        regex_book = re.compile('\s*%s\s*' % '\s*'.join(
            book_escaped.split()), re.UNICODE | re.IGNORECASE)
        if language_selection == LanguageSelection.Bible:
            db_book = self.get_book(book)
            if db_book:
                return db_book.book_reference_id
        elif language_selection == LanguageSelection.Application:
            books = [key for key in list(book_names.keys()) if regex_book.match(str(book_names[key]))]
            books = [_f for _f in map(BiblesResourcesDB.get_book, books) if _f]
            for value in books:
                if self.get_book_by_book_ref_id(value['id']):
                    return value['id']
        elif language_selection == LanguageSelection.English:
            books = BiblesResourcesDB.get_books_like(book)
            if books:
                book_list = [value for value in books if regex_book.match(value['name'])]
                if not book_list:
                    book_list = books
                for value in book_list:
                    if self.get_book_by_book_ref_id(value['id']):
                        return value['id']
        return False

    def get_verses(self, reference_list, show_error=True):
        """
        This is probably the most used function. It retrieves the list of
        verses based on the user's query.

        :param reference_list: This is the list of references the media manager item wants. It is a list of tuples, with
            the following format::

                (book_reference_id, chapter, start_verse, end_verse)

            Therefore, when you are looking for multiple items, simply break them up into references like this, bundle
            them into a list. This function then runs through the list, and returns an amalgamated list of ``Verse``
            objects. For example::

                [('35', 1, 1, 1), ('35', 2, 2, 3)]
        :param show_error:
        """
        log.debug('BibleDB.get_verses("%s")' % reference_list)
        verse_list = []
        book_error = False
        for book_id, chapter, start_verse, end_verse in reference_list:
            db_book = self.get_book_by_book_ref_id(book_id)
            if db_book:
                book_id = db_book.book_reference_id
                log.debug('Book name corrected to "%s"' % db_book.name)
                if end_verse == -1:
                    end_verse = self.get_verse_count(book_id, chapter)
                verses = self.session.query(Verse) \
                    .filter_by(book_id=db_book.id) \
                    .filter_by(chapter=chapter) \
                    .filter(Verse.verse >= start_verse) \
                    .filter(Verse.verse <= end_verse) \
                    .order_by(Verse.verse) \
                    .all()
                verse_list.extend(verses)
            else:
                log.debug('OpenLP failed to find book with id "%s"' % book_id)
                book_error = True
        if book_error and show_error:
            critical_error_message_box(
                translate('BiblesPlugin', 'No Book Found'),
                translate('BiblesPlugin', 'No matching book '
                          'could be found in this Bible. Check that you have spelled the name of the book correctly.'))
        return verse_list

    def verse_search(self, text):
        """
        Search for verses containing text ``text``.

        :param text:
            The text to search for. If the text contains commas, it will be
            split apart and OR'd on the list of values. If the text just
            contains spaces, it will split apart and AND'd on the list of
            values.
        """
        log.debug('BibleDB.verse_search("%s")' % text)
        verses = self.session.query(Verse)
        if text.find(',') > -1:
            keywords = ['%%%s%%' % keyword.strip() for keyword in text.split(',')]
            or_clause = [Verse.text.like(keyword) for keyword in keywords]
            verses = verses.filter(or_(*or_clause))
        else:
            keywords = ['%%%s%%' % keyword.strip() for keyword in text.split(' ')]
            for keyword in keywords:
                verses = verses.filter(Verse.text.like(keyword))
        verses = verses.all()
        return verses

    def get_chapter_count(self, book):
        """
        Return the number of chapters in a book.

        :param book: The book object to get the chapter count for.
        """
        log.debug('BibleDB.get_chapter_count("%s")' % book.name)
        count = self.session.query(func.max(Verse.chapter)).join(Book).filter(
            Book.book_reference_id == book.book_reference_id).scalar()
        if not count:
            return 0
        return count

    def get_verse_count(self, book_ref_id, chapter):
        """
        Return the number of verses in a chapter.

        :param book_ref_id: The book reference id.
        :param chapter: The chapter to get the verse count for.
        """
        log.debug('BibleDB.get_verse_count("%s", "%s")' % (book_ref_id, chapter))
        count = self.session.query(func.max(Verse.verse)).join(Book) \
            .filter(Book.book_reference_id == book_ref_id) \
            .filter(Verse.chapter == chapter) \
            .scalar()
        if not count:
            return 0
        return count

    def get_language(self, bible_name=None):
        """
        If no language is given it calls a dialog window where the user could  select the bible language.
        Return the language id of a bible.

        :param bible_name: The language the bible is.
        """
        log.debug('BibleDB.get_language()')
        from openlp.plugins.bibles.forms import LanguageForm
        language = None
        language_form = LanguageForm(self.wizard)
        if language_form.exec_(bible_name):
            language = str(language_form.language_combo_box.currentText())
        if not language:
            return False
        language = BiblesResourcesDB.get_language(language)
        language_id = language['id']
        self.save_meta('language_id', language_id)
        return language_id

    def is_old_database(self):
        """
        Returns ``True`` if it is a bible database, which has been created prior to 1.9.6.
        """
        try:
            self.session.query(Book).all()
        except:
            return True
        return False

    def dump_bible(self):
        """
        Utility debugging method to dump the contents of a bible.
        """
        log.debug('.........Dumping Bible Database')
        log.debug('...............................Books ')
        books = self.session.query(Book).all()
        log.debug(books)
        log.debug('...............................Verses ')
        verses = self.session.query(Verse).all()
        log.debug(verses)


class BiblesResourcesDB(QtCore.QObject, Manager):
    """
    This class represents the database-bound Bible Resources. It provide
    some resources which are used in the Bibles plugin.
    A wrapper class around a small SQLite database which contains the download
    resources, a biblelist from the different download resources, the books,
    chapter counts and verse counts for the web download Bibles, a language
    reference, the testament reference and some alternative book names. This
    class contains a singleton "cursor" so that only one connection to the
    SQLite database is ever used.
    """
    cursor = None

    @staticmethod
    def get_cursor():
        """
        Return the cursor object. Instantiate one if it doesn't exist yet.
        """
        if BiblesResourcesDB.cursor is None:
            file_path = os.path.join(AppLocation.get_directory(AppLocation.PluginsDir),
                                     'bibles', 'resources', 'bibles_resources.sqlite')
            conn = sqlite3.connect(file_path)
            BiblesResourcesDB.cursor = conn.cursor()
        return BiblesResourcesDB.cursor

    @staticmethod
    def run_sql(query, parameters=()):
        """
        Run an SQL query on the database, returning the results.

        ``query``
            The actual SQL query to run.

        ``parameters``
            Any variable parameters to add to the query.
        """
        cursor = BiblesResourcesDB.get_cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()

    @staticmethod
    def get_books():
        """
        Return a list of all the books of the Bible.
        """
        log.debug('BiblesResourcesDB.get_books()')
        books = BiblesResourcesDB.run_sql(
            'SELECT id, testament_id, name, abbreviation, chapters FROM book_reference ORDER BY id')
        return [{
            'id': book[0],
            'testament_id': book[1],
            'name': str(book[2]),
            'abbreviation': str(book[3]),
            'chapters': book[4]
        } for book in books]

    @staticmethod
    def get_book(name, lower=False):
        """
        Return a book by name or abbreviation.

        :param name: The name or abbreviation of the book.
        :param lower: True if the comparison should be only lowercase
        """
        log.debug('BiblesResourcesDB.get_book("%s")' % name)
        if not isinstance(name, str):
            name = str(name)
        if lower:
            books = BiblesResourcesDB.run_sql(
                'SELECT id, testament_id, name, abbreviation, chapters FROM book_reference WHERE '
                'LOWER(name) = ? OR LOWER(abbreviation) = ?', (name.lower(), name.lower()))
        else:
            books = BiblesResourcesDB.run_sql(
                'SELECT id, testament_id, name, abbreviation, chapters FROM book_reference WHERE name = ?'
                ' OR abbreviation = ?', (name, name))
        if books:
            return {
                'id': books[0][0],
                'testament_id': books[0][1],
                'name': str(books[0][2]),
                'abbreviation': str(books[0][3]),
                'chapters': books[0][4]
            }
        else:
            return None

    @staticmethod
    def get_books_like(string):
        """
        Return the books which include string.

        :param string: The string to search for in the book names or abbreviations.
        """
        log.debug('BiblesResourcesDB.get_book_like("%s")' % string)
        if not isinstance(string, str):
            name = str(string)
        books = BiblesResourcesDB.run_sql(
            'SELECT id, testament_id, name, abbreviation, chapters FROM book_reference WHERE '
            'LOWER(name) LIKE ? OR LOWER(abbreviation) LIKE ?',
            ('%' + string.lower() + '%', '%' + string.lower() + '%'))
        if books:
            return [{
                'id': book[0],
                'testament_id': book[1],
                'name': str(book[2]),
                'abbreviation': str(book[3]),
                'chapters': book[4]
            } for book in books]
        else:
            return None

    @staticmethod
    def get_book_by_id(book_id):
        """
        Return a book by id.

        :param book_id: The id of the book.
        """
        log.debug('BiblesResourcesDB.get_book_by_id("%s")' % book_id)
        if not isinstance(book_id, int):
            book_id = int(book_id)
        books = BiblesResourcesDB.run_sql(
            'SELECT id, testament_id, name, abbreviation, chapters FROM book_reference WHERE id = ?', (book_id, ))
        if books:
            return {
                'id': books[0][0],
                'testament_id': books[0][1],
                'name': str(books[0][2]),
                'abbreviation': str(books[0][3]),
                'chapters': books[0][4]
            }
        else:
            return None

    @staticmethod
    def get_chapter(book_ref_id, chapter):
        """
        Return the chapter details for a specific chapter of a book.

        :param book_ref_id: The id of a book.
        :param chapter: The chapter number.
        """
        log.debug('BiblesResourcesDB.get_chapter("%s", "%s")' % (book_ref_id, chapter))
        if not isinstance(chapter, int):
            chapter = int(chapter)
        chapters = BiblesResourcesDB.run_sql(
            'SELECT id, book_reference_id, '
            'chapter, verse_count FROM chapters WHERE book_reference_id = ?', (book_ref_id,))
        try:
            return {
                'id': chapters[chapter - 1][0],
                'book_reference_id': chapters[chapter - 1][1],
                'chapter': chapters[chapter - 1][2],
                'verse_count': chapters[chapter - 1][3]
            }
        except (IndexError, TypeError):
            return None

    @staticmethod
    def get_chapter_count(book_ref_id):
        """
        Return the number of chapters in a book.

        :param book_ref_id: The id of the book.
        """
        log.debug('BiblesResourcesDB.get_chapter_count("%s")' % book_ref_id)
        details = BiblesResourcesDB.get_book_by_id(book_ref_id)
        if details:
            return details['chapters']
        return 0

    @staticmethod
    def get_verse_count(book_ref_id, chapter):
        """
        Return the number of verses in a chapter.

        :param book_ref_id: The id of the book.
        :param chapter: The number of the chapter.
        """
        log.debug('BiblesResourcesDB.get_verse_count("%s", "%s")' % (book_ref_id, chapter))
        details = BiblesResourcesDB.get_chapter(book_ref_id, chapter)
        if details:
            return details['verse_count']
        return 0

    @staticmethod
    def get_download_source(source):
        """
        Return a download_source_id by source.

        :param source: The name or abbreviation of the book.
        """
        log.debug('BiblesResourcesDB.get_download_source("%s")' % source)
        if not isinstance(source, str):
            source = str(source)
        source = source.title()
        dl_source = BiblesResourcesDB.run_sql(
            'SELECT id, source FROM download_source WHERE source = ?', (source.lower(),))
        if dl_source:
            return {
                'id': dl_source[0][0],
                'source': dl_source[0][1]
            }
        else:
            return None

    @staticmethod
    def get_webbibles(source):
        """
        Return the bibles a web_bible provide for download.

        :param source: The source of the web_bible.
        """
        log.debug('BiblesResourcesDB.get_webbibles("%s")' % source)
        if not isinstance(source, str):
            source = str(source)
        source = BiblesResourcesDB.get_download_source(source)
        bibles = BiblesResourcesDB.run_sql('SELECT id, name, abbreviation, language_id, download_source_id '
                                           'FROM webbibles WHERE download_source_id = ?', (source['id'],))
        if bibles:
            return [{
                'id': bible[0],
                'name': bible[1],
                'abbreviation': bible[2],
                'language_id': bible[3],
                'download_source_id': bible[4]
            } for bible in bibles]
        else:
            return None

    @staticmethod
    def get_webbible(abbreviation, source):
        """
        Return the bibles a web_bible provide for download.

        :param abbreviation: The abbreviation of the web_bible.
        :param source: The source of the web_bible.
        """
        log.debug('BiblesResourcesDB.get_webbibles("%s", "%s")' % (abbreviation, source))
        if not isinstance(abbreviation, str):
            abbreviation = str(abbreviation)
        if not isinstance(source, str):
            source = str(source)
        source = BiblesResourcesDB.get_download_source(source)
        bible = BiblesResourcesDB.run_sql(
            'SELECT id, name, abbreviation, language_id, download_source_id FROM webbibles WHERE '
            'download_source_id = ? AND abbreviation = ?', (source['id'], abbreviation))
        try:
            return {
                'id': bible[0][0],
                'name': bible[0][1],
                'abbreviation': bible[0][2],
                'language_id': bible[0][3],
                'download_source_id': bible[0][4]
            }
        except (IndexError, TypeError):
            return None

    @staticmethod
    def get_alternative_book_name(name, language_id=None):
        """
        Return a book_reference_id if the name matches.

        :param name: The name to search the id.
        :param language_id: The language_id for which language should be searched
        """
        log.debug('BiblesResourcesDB.get_alternative_book_name("%s", "%s")' % (name, language_id))
        if language_id:
            books = BiblesResourcesDB.run_sql(
                'SELECT book_reference_id, name FROM alternative_book_names WHERE language_id = ? ORDER BY id',
                (language_id, ))
        else:
            books = BiblesResourcesDB.run_sql('SELECT book_reference_id, name FROM alternative_book_names ORDER BY id')
        for book in books:
            if book[1].lower() == name.lower():
                return book[0]
        return None

    @staticmethod
    def get_language(name):
        """
        Return a dict containing the language id, name and code by name or abbreviation.

        :param name: The name or abbreviation of the language.
        """
        log.debug('BiblesResourcesDB.get_language("%s")' % name)
        if not isinstance(name, str):
            name = str(name)
        language = BiblesResourcesDB.run_sql(
            'SELECT id, name, code FROM language WHERE name = ? OR code = ?', (name, name.lower()))
        if language:
            return {
                'id': language[0][0],
                'name': str(language[0][1]),
                'code': str(language[0][2])
            }
        else:
            return None

    @staticmethod
    def get_languages():
        """
        Return a dict containing all languages with id, name and code.
        """
        log.debug('BiblesResourcesDB.get_languages()')
        languages = BiblesResourcesDB.run_sql('SELECT id, name, code FROM language ORDER by name')
        if languages:
            return [{
                'id': language[0],
                'name': str(language[1]),
                'code': str(language[2])
            } for language in languages]
        else:
            return None

    @staticmethod
    def get_testament_reference():
        """
        Return a list of all testaments and their id of the Bible.
        """
        log.debug('BiblesResourcesDB.get_testament_reference()')
        testaments = BiblesResourcesDB.run_sql('SELECT id, name FROM testament_reference ORDER BY id')
        return [
            {'id': testament[0],
             'name': str(testament[1])
             }
            for testament in testaments
        ]


class AlternativeBookNamesDB(QtCore.QObject, Manager):
    """
    This class represents a database-bound alternative book names system.
    """
    cursor = None
    conn = None

    @staticmethod
    def get_cursor():
        """
        Return the cursor object. Instantiate one if it doesn't exist yet.
        If necessary loads up the database and creates the tables if the database doesn't exist.
        """
        if AlternativeBookNamesDB.cursor is None:
            file_path = os.path.join(
                AppLocation.get_directory(AppLocation.DataDir), 'bibles', 'alternative_book_names.sqlite')
            if not os.path.exists(file_path):
                # create new DB, create table alternative_book_names
                AlternativeBookNamesDB.conn = sqlite3.connect(file_path)
                AlternativeBookNamesDB.conn.execute(
                    'CREATE TABLE alternative_book_names(id INTEGER NOT NULL, '
                    'book_reference_id INTEGER, language_id INTEGER, name VARCHAR(50), PRIMARY KEY (id))')
            else:
                # use existing DB
                AlternativeBookNamesDB.conn = sqlite3.connect(file_path)
            AlternativeBookNamesDB.cursor = AlternativeBookNamesDB.conn.cursor()
        return AlternativeBookNamesDB.cursor

    @staticmethod
    def run_sql(query, parameters=(), commit=None):
        """
        Run an SQL query on the database, returning the results.

        :param query: The actual SQL query to run.
        :param parameters: Any variable parameters to add to the query
        :param commit: If a commit statement is necessary this should be True.
        """
        cursor = AlternativeBookNamesDB.get_cursor()
        cursor.execute(query, parameters)
        if commit:
            AlternativeBookNamesDB.conn.commit()
        return cursor.fetchall()

    @staticmethod
    def get_book_reference_id(name, language_id=None):
        """
        Return a book_reference_id if the name matches.

        :param name: The name to search the id.
        :param language_id: The language_id for which language should be searched
        """
        log.debug('AlternativeBookNamesDB.get_book_reference_id("%s", "%s")' % (name, language_id))
        if language_id:
            books = AlternativeBookNamesDB.run_sql(
                'SELECT book_reference_id, name FROM alternative_book_names WHERE language_id = ?', (language_id, ))
        else:
            books = AlternativeBookNamesDB.run_sql(
                'SELECT book_reference_id, name FROM alternative_book_names')
        for book in books:
            if book[1].lower() == name.lower():
                return book[0]
        return None

    @staticmethod
    def create_alternative_book_name(name, book_reference_id, language_id):
        """
        Add an alternative book name to the database.

        :param name:  The name of the alternative book name.
        :param book_reference_id: The book_reference_id of the book.
        :param language_id: The language to which the alternative book name belong.
        """
        log.debug('AlternativeBookNamesDB.create_alternative_book_name("%s", "%s", "%s")' %
                  (name, book_reference_id, language_id))
        return AlternativeBookNamesDB.run_sql(
            'INSERT INTO alternative_book_names(book_reference_id, language_id, name) '
            'VALUES (?, ?, ?)', (book_reference_id, language_id, name), True)


class OldBibleDB(QtCore.QObject, Manager):
    """
    This class connects to the old bible databases to reimport them to the new
    database scheme.
    """
    cursor = None

    def __init__(self, parent, **kwargs):
        """
        The constructor loads up the database and creates and initialises the tables if the database doesn't exist.

        **Required keyword arguments:**

        ``path``
            The path to the bible database file.

        ``name``
            The name of the database. This is also used as the file name for SQLite databases.
        """
        log.info('OldBibleDB loaded')
        QtCore.QObject.__init__(self)
        if 'path' not in kwargs:
            raise KeyError('Missing keyword argument "path".')
        if 'file' not in kwargs:
            raise KeyError('Missing keyword argument "file".')
        if 'path' in kwargs:
            self.path = kwargs['path']
        if 'file' in kwargs:
            self.file = kwargs['file']

    def get_cursor(self):
        """
        Return the cursor object. Instantiate one if it doesn't exist yet.
        """
        if self.cursor is None:
            file_path = os.path.join(self.path, self.file)
            self.connection = sqlite3.connect(file_path)
            self.cursor = self.connection.cursor()
        return self.cursor

    def run_sql(self, query, parameters=()):
        """
        Run an SQL query on the database, returning the results.

        :param query: The actual SQL query to run.
        :param parameters: Any variable parameters to add to the query.
        """
        cursor = self.get_cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()

    def get_name(self):
        """
        Returns the version name of the Bible.
        """
        self.name = None
        version_name = self.run_sql('SELECT value FROM metadata WHERE key = "name"')
        if version_name:
            self.name = version_name[0][0]
        else:
            # Fallback to old way of naming
            version_name = self.run_sql('SELECT value FROM metadata WHERE key = "Version"')
            if version_name:
                self.name = version_name[0][0]
        return self.name

    def get_metadata(self):
        """
        Returns the metadata of the Bible.
        """
        metadata = self.run_sql('SELECT key, value FROM metadata ORDER BY rowid')
        if metadata:
            return [{
                'key': str(meta[0]),
                'value': str(meta[1])
            } for meta in metadata]
        else:
            return None

    def get_book(self, name):
        """
        Return a book by name or abbreviation.

        ``name``
            The name or abbreviation of the book.
        """
        if not isinstance(name, str):
            name = str(name)
        books = self.run_sql(
            'SELECT id, testament_id, name, abbreviation FROM book WHERE LOWER(name) = ? OR '
            'LOWER(abbreviation) = ?', (name.lower(), name.lower()))
        if books:
            return {
                'id': books[0][0],
                'testament_id': books[0][1],
                'name': str(books[0][2]),
                'abbreviation': str(books[0][3])
            }
        else:
            return None

    def get_books(self):
        """
        Returns the books of the Bible.
        """
        books = self.run_sql('SELECT name, id FROM book ORDER BY id')
        if books:
            return [{
                'name': str(book[0]),
                'id':int(book[1])
            } for book in books]
        else:
            return None

    def get_verses(self, book_id):
        """
        Returns the verses of the Bible.
        """
        verses = self.run_sql(
            'SELECT book_id, chapter, verse, text FROM verse WHERE book_id = ? ORDER BY id', (book_id, ))
        if verses:
            return [{
                'book_id': int(verse[0]),
                'chapter': int(verse[1]),
                'verse': int(verse[2]),
                'text': str(verse[3])
            } for verse in verses]
        else:
            return None

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
