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
The :mod:`db` module provides the database and schema that is the backend for
the Songs plugin
"""

from sqlalchemy import Column, ForeignKey, Table, types
from sqlalchemy.orm import mapper, relation, reconstructor
from sqlalchemy.sql.expression import func, text

from openlp.core.lib.db import BaseModel, init_db
from openlp.core.utils import get_natural_key
from openlp.core.lib import translate


class Author(BaseModel):
    """
    Author model
    """
    def get_display_name(self, author_type=None):
        if author_type:
            return "%s (%s)" % (self.display_name, AuthorType.Types[author_type])
        return self.display_name


class AuthorSong(BaseModel):
    """
    Relationship between Authors and Songs (many to many).
    Need to define this relationship table explicit to get access to the
    Association Object (author_type).
    http://docs.sqlalchemy.org/en/latest/orm/relationships.html#association-object
    """
    pass


class AuthorType(object):
    """
    Enumeration for Author types.
    They are defined by OpenLyrics: http://openlyrics.info/dataformat.html#authors

    The 'words+music' type is not an official type, but is provided for convenience.
    """
    NoType = ''
    Words = 'words'
    Music = 'music'
    WordsAndMusic = 'words+music'
    Translation = 'translation'
    Types = {
        NoType: '',
        Words: translate('SongsPlugin.AuthorType', 'Words', 'Author who wrote the lyrics of a song'),
        Music: translate('SongsPlugin.AuthorType', 'Music', 'Author who wrote the music of a song'),
        WordsAndMusic: translate('SongsPlugin.AuthorType', 'Words and Music',
                                 'Author who wrote both lyrics and music of a song'),
        Translation: translate('SongsPlugin.AuthorType', 'Translation', 'Author who translated the song')
    }
    SortedTypes = [
        NoType,
        Words,
        Music,
        WordsAndMusic,
        Translation
    ]
    TranslatedTypes = [
        Types[NoType],
        Types[Words],
        Types[Music],
        Types[WordsAndMusic],
        Types[Translation]
    ]

    @staticmethod
    def from_translated_text(translated_type):
        """
        Get the AuthorType from a translated string.
        :param translated_type: Translated Author type.
        """
        for key, value in AuthorType.Types.items():
            if value == translated_type:
                return key
        return AuthorType.NoType


class Book(BaseModel):
    """
    Book model
    """
    def __repr__(self):
        return '<Book id="%s" name="%s" publisher="%s" />' % (str(self.id), self.name, self.publisher)


class MediaFile(BaseModel):
    """
    MediaFile model
    """
    pass


class Song(BaseModel):
    """
    Song model
    """

    def __init__(self):
        self.sort_key = []

    @reconstructor
    def init_on_load(self):
        """
        Precompute a natural sorting, locale aware sorting key.

        Song sorting is performance sensitive operation.
        To get maximum speed lets precompute the sorting key.
        """
        self.sort_key = get_natural_key(self.title)

    def add_author(self, author, author_type=None):
        """
        Add an author to the song if it not yet exists

        :param author: Author object
        :param author_type: AuthorType constant or None
        """
        for author_song in self.authors_songs:
            if author_song.author == author and author_song.author_type == author_type:
                return
        new_author_song = AuthorSong()
        new_author_song.author = author
        new_author_song.author_type = author_type
        self.authors_songs.append(new_author_song)

    def remove_author(self, author, author_type=None):
        """
        Remove an existing author from the song

        :param author: Author object
        :param author_type: AuthorType constant or None
        """
        for author_song in self.authors_songs:
            if author_song.author == author and author_song.author_type == author_type:
                self.authors_songs.remove(author_song)
                return


class Topic(BaseModel):
    """
    Topic model
    """
    pass


def init_schema(url):
    """
    Setup the songs database connection and initialise the database schema.

    :param url: The database to setup
    The song database contains the following tables:

        * authors
        * authors_songs
        * media_files
        * media_files_songs
        * song_books
        * songs
        * songs_topics
        * topics

    **authors** Table
        This table holds the names of all the authors. It has the following
        columns:

        * id
        * first_name
        * last_name
        * display_name

    **authors_songs Table**
        This is a bridging table between the *authors* and *songs* tables, which
        serves to create a many-to-many relationship between the two tables. It
        has the following columns:

        * author_id
        * song_id
        * author_type

    **media_files Table**
        * id
        * file_name
        * type

    **song_books Table**
        The *song_books* table holds a list of books that a congregation gets
        their songs from, or old hymnals now no longer used. This table has the
        following columns:

        * id
        * name
        * publisher

    **songs Table**
        This table contains the songs, and each song has a list of attributes.
        The *songs* table has the following columns:

        * id
        * song_book_id
        * title
        * alternate_title
        * lyrics
        * verse_order
        * copyright
        * comments
        * ccli_number
        * song_number
        * theme_name
        * search_title
        * search_lyrics

    **songs_topics Table**
        This is a bridging table between the *songs* and *topics* tables, which
        serves to create a many-to-many relationship between the two tables. It
        has the following columns:

        * song_id
        * topic_id

    **topics Table**
        The topics table holds a selection of topics that songs can cover. This
        is useful when a worship leader wants to select songs with a certain
        theme. This table has the following columns:

        * id
        * name
    """
    session, metadata = init_db(url)

    # Definition of the "authors" table
    authors_table = Table(
        'authors', metadata,
        Column('id', types.Integer(), primary_key=True),
        Column('first_name', types.Unicode(128)),
        Column('last_name', types.Unicode(128)),
        Column('display_name', types.Unicode(255), index=True, nullable=False)
    )

    # Definition of the "media_files" table
    media_files_table = Table(
        'media_files', metadata,
        Column('id', types.Integer(), primary_key=True),
        Column('song_id', types.Integer(), ForeignKey('songs.id'), default=None),
        Column('file_name', types.Unicode(255), nullable=False),
        Column('type', types.Unicode(64), nullable=False, default='audio'),
        Column('weight', types.Integer(), default=0)
    )

    # Definition of the "song_books" table
    song_books_table = Table(
        'song_books', metadata,
        Column('id', types.Integer(), primary_key=True),
        Column('name', types.Unicode(128), nullable=False),
        Column('publisher', types.Unicode(128))
    )

    # Definition of the "songs" table
    songs_table = Table(
        'songs', metadata,
        Column('id', types.Integer(), primary_key=True),
        Column('song_book_id', types.Integer(), ForeignKey('song_books.id'), default=None),
        Column('title', types.Unicode(255), nullable=False),
        Column('alternate_title', types.Unicode(255)),
        Column('lyrics', types.UnicodeText, nullable=False),
        Column('verse_order', types.Unicode(128)),
        Column('copyright', types.Unicode(255)),
        Column('comments', types.UnicodeText),
        Column('ccli_number', types.Unicode(64)),
        Column('song_number', types.Unicode(64)),
        Column('theme_name', types.Unicode(128)),
        Column('search_title', types.Unicode(255), index=True, nullable=False),
        Column('search_lyrics', types.UnicodeText, nullable=False),
        Column('create_date', types.DateTime(), default=func.now()),
        Column('last_modified', types.DateTime(), default=func.now(), onupdate=func.now()),
        Column('temporary', types.Boolean(), default=False)
    )

    # Definition of the "topics" table
    topics_table = Table(
        'topics', metadata,
        Column('id', types.Integer(), primary_key=True),
        Column('name', types.Unicode(128), index=True, nullable=False)
    )

    # Definition of the "authors_songs" table
    authors_songs_table = Table(
        'authors_songs', metadata,
        Column('author_id', types.Integer(), ForeignKey('authors.id'), primary_key=True),
        Column('song_id', types.Integer(), ForeignKey('songs.id'), primary_key=True),
        Column('author_type', types.Unicode(255), primary_key=True, nullable=False, server_default=text('""'))
    )

    # Definition of the "songs_topics" table
    songs_topics_table = Table(
        'songs_topics', metadata,
        Column('song_id', types.Integer(), ForeignKey('songs.id'), primary_key=True),
        Column('topic_id', types.Integer(), ForeignKey('topics.id'), primary_key=True)
    )

    mapper(Author, authors_table, properties={
        'songs': relation(Song, secondary=authors_songs_table, viewonly=True)
    })
    mapper(AuthorSong, authors_songs_table, properties={
        'author': relation(Author)
    })
    mapper(Book, song_books_table)
    mapper(MediaFile, media_files_table)
    mapper(Song, songs_table, properties={
        # Use the authors_songs relation when you need access to the 'author_type' attribute
        # or when creating new relations
        'authors_songs': relation(AuthorSong, cascade="all, delete-orphan"),
        # Use lazy='joined' to always load authors when the song is fetched from the database (bug 1366198)
        'authors': relation(Author, secondary=authors_songs_table, viewonly=True, lazy='joined'),
        'book': relation(Book, backref='songs'),
        'media_files': relation(MediaFile, backref='songs', order_by=media_files_table.c.weight),
        'topics': relation(Topic, backref='songs', secondary=songs_topics_table)
    })
    mapper(Topic, topics_table)

    metadata.create_all(checkfirst=True)
    return session
