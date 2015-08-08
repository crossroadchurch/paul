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
The :mod:`~openlp.plugins.songs.lib.songselect` module contains the SongSelect importer itself.
"""
import logging
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, URLError, build_opener
from html.parser import HTMLParser


from bs4 import BeautifulSoup, NavigableString

from openlp.plugins.songs.lib import Song, VerseType, clean_song, Author
from openlp.plugins.songs.lib.openlyricsxml import SongXML

USER_AGENT = 'Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; GT-I9000 ' \
             'Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 ' \
             'Mobile Safari/534.30'
BASE_URL = 'https://mobile.songselect.com'
LOGIN_URL = BASE_URL + '/account/login'
LOGOUT_URL = BASE_URL + '/account/logout'
SEARCH_URL = BASE_URL + '/search/results'

log = logging.getLogger(__name__)


class SongSelectImport(object):
    """
    The :class:`~openlp.plugins.songs.lib.songselect.SongSelectImport` class contains all the code which interfaces
    with CCLI's SongSelect service and downloads the songs.
    """
    def __init__(self, db_manager):
        """
        Set up the song select importer

        :param db_manager: The song database manager
        """
        self.db_manager = db_manager
        self.html_parser = HTMLParser()
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.opener.addheaders = [('User-Agent', USER_AGENT)]

    def login(self, username, password, callback=None):
        """
        Log the user into SongSelect. This method takes a username and password, and runs ``callback()`` at various
        points which can be used to give the user some form of feedback.

        :param username: SongSelect username
        :param password: SongSelect password
        :param callback: Method to notify of progress.
        :return: True on success, False on failure.
        """
        if callback:
            callback()
        try:
            login_page = BeautifulSoup(self.opener.open(LOGIN_URL).read(), 'lxml')
        except (TypeError, URLError) as e:
            log.exception('Could not login to SongSelect, %s', e)
            return False
        if callback:
            callback()
        token_input = login_page.find('input', attrs={'name': '__RequestVerificationToken'})
        data = urlencode({
            '__RequestVerificationToken': token_input['value'],
            'UserName': username,
            'Password': password,
            'RememberMe': 'false'
        })
        try:
            posted_page = BeautifulSoup(self.opener.open(LOGIN_URL, data.encode('utf-8')).read(), 'lxml')
        except (TypeError, URLError) as e:
            log.exception('Could not login to SongSelect, %s', e)
            return False
        if callback:
            callback()
        return not posted_page.find('input', attrs={'name': '__RequestVerificationToken'})

    def logout(self):
        """
        Log the user out of SongSelect
        """
        try:
            self.opener.open(LOGOUT_URL)
        except (TypeError, URLError) as e:
            log.exception('Could not log of SongSelect, %s', e)

    def search(self, search_text, max_results, callback=None):
        """
        Set up a search.

        :param search_text: The text to search for.
        :param max_results: Maximum number of results to fetch.
        :param callback: A method which is called when each song is found, with the song as a parameter.
        :return: List of songs
        """
        params = {'allowredirect': 'false', 'SearchTerm': search_text}
        current_page = 1
        songs = []
        while True:
            if current_page > 1:
                params['page'] = current_page
            try:
                results_page = BeautifulSoup(self.opener.open(SEARCH_URL + '?' + urlencode(params)).read(), 'lxml')
                search_results = results_page.find_all('li', 'result pane')
            except (TypeError, URLError) as e:
                log.exception('Could not search SongSelect, %s', e)
                search_results = None
            if not search_results:
                break
            for result in search_results:
                song = {
                    'title': self.html_parser.unescape(result.find('h3').string),
                    'authors': [self.html_parser.unescape(author.string) for author in result.find_all('li')],
                    'link': BASE_URL + result.find('a')['href']
                }
                if callback:
                    callback(song)
                songs.append(song)
                if len(songs) >= max_results:
                    break
            current_page += 1
        return songs

    def get_song(self, song, callback=None):
        """
        Get the full song from SongSelect

        :param song: The song dictionary to update
        :param callback: A callback which can be used to indicate progress
        :return: The updated song dictionary
        """
        if callback:
            callback()
        try:
            song_page = BeautifulSoup(self.opener.open(song['link']).read(), 'lxml')
        except (TypeError, URLError) as e:
            log.exception('Could not get song from SongSelect, %s', e)
            return None
        if callback:
            callback()
        try:
            lyrics_page = BeautifulSoup(self.opener.open(song['link'] + '/lyrics').read(), 'lxml')
        except (TypeError, URLError):
            log.exception('Could not get lyrics from SongSelect')
            return None
        if callback:
            callback()
        song['copyright'] = '/'.join([li.string for li in song_page.find('ul', 'copyright').find_all('li')])
        song['copyright'] = self.html_parser.unescape(song['copyright'])
        song['ccli_number'] = song_page.find('ul', 'info').find('li').string.split(':')[1].strip()
        song['verses'] = []
        verses = lyrics_page.find('section', 'lyrics').find_all('p')
        verse_labels = lyrics_page.find('section', 'lyrics').find_all('h3')
        for counter in range(len(verses)):
            verse = {'label': verse_labels[counter].string, 'lyrics': ''}
            for v in verses[counter].contents:
                if isinstance(v, NavigableString):
                    verse['lyrics'] = verse['lyrics'] + v.string
                else:
                    verse['lyrics'] += '\n'
            verse['lyrics'] = verse['lyrics'].strip(' \n\r\t')
            song['verses'].append(self.html_parser.unescape(verse))
        for counter, author in enumerate(song['authors']):
            song['authors'][counter] = self.html_parser.unescape(author)
        return song

    def save_song(self, song):
        """
        Save a song to the database, using the db_manager

        :param song:
        :return:
        """
        db_song = Song.populate(title=song['title'], copyright=song['copyright'], ccli_number=song['ccli_number'])
        song_xml = SongXML()
        verse_order = []
        for verse in song['verses']:
            verse_type, verse_number = verse['label'].split(' ')[:2]
            verse_type = VerseType.from_loose_input(verse_type)
            verse_number = int(verse_number)
            song_xml.add_verse_to_lyrics(VerseType.tags[verse_type], verse_number, verse['lyrics'])
            verse_order.append('%s%s' % (VerseType.tags[verse_type], verse_number))
        db_song.verse_order = ' '.join(verse_order)
        db_song.lyrics = song_xml.extract_xml()
        clean_song(self.db_manager, db_song)
        self.db_manager.save_object(db_song)
        db_song.authors_songs = []
        for author_name in song['authors']:
            author = self.db_manager.get_object_filtered(Author, Author.display_name == author_name)
            if not author:
                author = Author.populate(first_name=author_name.rsplit(' ', 1)[0],
                                         last_name=author_name.rsplit(' ', 1)[1],
                                         display_name=author_name)
            db_song.add_author(author)
        self.db_manager.save_object(db_song)
        return db_song
