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
The :mod:`openlp.core.utils` module provides the utility libraries for OpenLP.
"""
from datetime import datetime
from distutils.version import LooseVersion
from http.client import HTTPException
import logging
import locale
import os
import platform
import re
import socket
import time
from shutil import which
from subprocess import Popen, PIPE
import sys
import urllib.request
import urllib.error
import urllib.parse
from random import randint

from PyQt4 import QtGui, QtCore

from openlp.core.common import Registry, AppLocation, Settings, is_win, is_macosx


if not is_win() and not is_macosx():
    try:
        from xdg import BaseDirectory
        XDG_BASE_AVAILABLE = True
    except ImportError:
        BaseDirectory = None
        XDG_BASE_AVAILABLE = False

from openlp.core.common import translate

log = logging.getLogger(__name__ + '.__init__')

APPLICATION_VERSION = {}
IMAGES_FILTER = None
ICU_COLLATOR = None
CONTROL_CHARS = re.compile(r'[\x00-\x1F\x7F-\x9F]', re.UNICODE)
INVALID_FILE_CHARS = re.compile(r'[\\/:\*\?"<>\|\+\[\]%]', re.UNICODE)
DIGITS_OR_NONDIGITS = re.compile(r'\d+|\D+', re.UNICODE)
USER_AGENTS = {
    'win32': [
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36'
    ],
    'darwin': [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) '
        'Chrome/26.0.1410.43 Safari/537.31',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.47 Safari/536.11',
    ],
    'linux2': [
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 '
        'Chrome/25.0.1364.160 Safari/537.22',
        'Mozilla/5.0 (X11; CrOS armv7l 2913.260.0) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.99 '
        'Safari/537.11',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.27 (KHTML, like Gecko) Chrome/26.0.1389.0 Safari/537.27'
    ],
    'default': [
        'Mozilla/5.0 (X11; NetBSD amd64; rv:18.0) Gecko/20130120 Firefox/18.0'
    ]
}
CONNECTION_TIMEOUT = 30
CONNECTION_RETRIES = 2


class VersionThread(QtCore.QThread):
    """
    A special Qt thread class to fetch the version of OpenLP from the website.
    This is threaded so that it doesn't affect the loading time of OpenLP.
    """
    def __init__(self, main_window):
        """
        Constructor for the thread class.

        :param main_window: The main window Object.
        """
        log.debug("VersionThread - Initialise")
        super(VersionThread, self).__init__(None)
        self.main_window = main_window

    def run(self):
        """
        Run the thread.
        """
        self.sleep(1)
        log.debug('Version thread - run')
        app_version = get_application_version()
        version = check_latest_version(app_version)
        log.debug("Versions %s and %s " % (LooseVersion(str(version)), LooseVersion(str(app_version['full']))))
        if LooseVersion(str(version)) > LooseVersion(str(app_version['full'])):
            self.main_window.emit(QtCore.SIGNAL('openlp_version_check'), '%s' % version)


class HTTPRedirectHandlerFixed(urllib.request.HTTPRedirectHandler):
    """
    Special HTTPRedirectHandler used to work around http://bugs.python.org/issue22248
    (Redirecting to urls with special chars)
    """
    def redirect_request(self, req, fp, code, msg, headers, new_url):
        #
        """
        Test if the new_url can be decoded to ascii

        :param req:
        :param fp:
        :param code:
        :param msg:
        :param headers:
        :param new_url:
        :return:
        """
        try:
            new_url.encode('latin1').decode('ascii')
            fixed_url = new_url
        except Exception:
            # The url could not be decoded to ascii, so we do some url encoding
            fixed_url = urllib.parse.quote(new_url.encode('latin1').decode('utf-8', 'replace'), safe='/:')
        return super(HTTPRedirectHandlerFixed, self).redirect_request(req, fp, code, msg, headers, fixed_url)


def get_application_version():
    """
    Returns the application version of the running instance of OpenLP::

        {'full': '1.9.4-bzr1249', 'version': '1.9.4', 'build': 'bzr1249'}
    """
    global APPLICATION_VERSION
    if APPLICATION_VERSION:
        return APPLICATION_VERSION
    if '--dev-version' in sys.argv or '-d' in sys.argv:
        # NOTE: The following code is a duplicate of the code in setup.py. Any fix applied here should also be applied
        # there.

        # Get the revision of this tree.
        bzr = Popen(('bzr', 'revno'), stdout=PIPE)
        tree_revision, error = bzr.communicate()
        tree_revision = tree_revision.decode()
        code = bzr.wait()
        if code != 0:
            raise Exception('Error running bzr log')

        # Get all tags.
        bzr = Popen(('bzr', 'tags'), stdout=PIPE)
        output, error = bzr.communicate()
        code = bzr.wait()
        if code != 0:
            raise Exception('Error running bzr tags')
        tags = list(map(bytes.decode, output.splitlines()))
        if not tags:
            tag_version = '0.0.0'
            tag_revision = '0'
        else:
            # Remove any tag that has "?" as revision number. A "?" as revision number indicates, that this tag is from
            # another series.
            tags = [tag for tag in tags if tag.split()[-1].strip() != '?']
            # Get the last tag and split it in a revision and tag name.
            tag_version, tag_revision = tags[-1].split()
        # If they are equal, then this tree is tarball with the source for the release. We do not want the revision
        # number in the full version.
        if tree_revision == tag_revision:
            full_version = tag_version.decode('utf-8')
        else:
            full_version = '%s-bzr%s' % (tag_version.decode('utf-8'), tree_revision.decode('utf-8'))
    else:
        # We're not running the development version, let's use the file.
        file_path = AppLocation.get_directory(AppLocation.VersionDir)
        file_path = os.path.join(file_path, '.version')
        version_file = None
        try:
            version_file = open(file_path, 'r')
            full_version = str(version_file.read()).rstrip()
        except IOError:
            log.exception('Error in version file.')
            full_version = '0.0.0-bzr000'
        finally:
            if version_file:
                version_file.close()
    bits = full_version.split('-')
    APPLICATION_VERSION = {
        'full': full_version,
        'version': bits[0],
        'build': bits[1] if len(bits) > 1 else None
    }
    if APPLICATION_VERSION['build']:
        log.info('Openlp version %s build %s', APPLICATION_VERSION['version'], APPLICATION_VERSION['build'])
    else:
        log.info('Openlp version %s' % APPLICATION_VERSION['version'])
    return APPLICATION_VERSION


def check_latest_version(current_version):
    """
    Check the latest version of OpenLP against the version file on the OpenLP
    site.

    **Rules around versions and version files:**

    * If a version number has a build (i.e. -bzr1234), then it is a nightly.
    * If a version number's minor version is an odd number, it is a development release.
    * If a version number's minor version is an even number, it is a stable release.

    :param current_version: The current version of OpenLP.
    """
    version_string = current_version['full']
    # set to prod in the distribution config file.
    settings = Settings()
    settings.beginGroup('core')
    last_test = settings.value('last version test')
    this_test = str(datetime.now().date())
    settings.setValue('last version test', this_test)
    settings.endGroup()
    if last_test != this_test:
        if current_version['build']:
            req = urllib.request.Request('http://www.openlp.org/files/nightly_version.txt')
        else:
            version_parts = current_version['version'].split('.')
            if int(version_parts[1]) % 2 != 0:
                req = urllib.request.Request('http://www.openlp.org/files/dev_version.txt')
            else:
                req = urllib.request.Request('http://www.openlp.org/files/version.txt')
        req.add_header('User-Agent', 'OpenLP/%s %s/%s; ' % (current_version['full'], platform.system(),
                                                            platform.release()))
        remote_version = None
        retries = 0
        while True:
            try:
                remote_version = str(urllib.request.urlopen(req, None,
                                                            timeout=CONNECTION_TIMEOUT).read().decode()).strip()
            except (urllib.error.URLError, ConnectionError):
                if retries > CONNECTION_RETRIES:
                    log.exception('Failed to download the latest OpenLP version file')
                else:
                    retries += 1
                    time.sleep(0.1)
                    continue
            break
        if remote_version:
            version_string = remote_version
    return version_string


def add_actions(target, actions):
    """
    Adds multiple actions to a menu or toolbar in one command.

    :param target: The menu or toolbar to add actions to
    :param actions: The actions to be added. An action consisting of the keyword ``None``
        will result in a separator being inserted into the target.
    """
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)


def get_filesystem_encoding():
    """
    Returns the name of the encoding used to convert Unicode filenames into system file names.
    """
    encoding = sys.getfilesystemencoding()
    if encoding is None:
        encoding = sys.getdefaultencoding()
    return encoding


def get_images_filter():
    """
    Returns a filter string for a file dialog containing all the supported image formats.
    """
    global IMAGES_FILTER
    if not IMAGES_FILTER:
        log.debug('Generating images filter.')
        formats = list(map(bytes.decode, list(map(bytes, QtGui.QImageReader.supportedImageFormats()))))
        visible_formats = '(*.%s)' % '; *.'.join(formats)
        actual_formats = '(*.%s)' % ' *.'.join(formats)
        IMAGES_FILTER = '%s %s %s' % (translate('OpenLP', 'Image Files'), visible_formats, actual_formats)
    return IMAGES_FILTER


def is_not_image_file(file_name):
    """
    Validate that the file is not an image file.

    :param file_name: File name to be checked.
    """
    if not file_name:
        return True
    else:
        formats = [bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()]
        file_part, file_extension = os.path.splitext(str(file_name))
        if file_extension[1:].lower() in formats and os.path.exists(file_name):
            return False
        return True


def split_filename(path):
    """
    Return a list of the parts in a given path.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return path, ''
    else:
        return os.path.split(path)


def clean_filename(filename):
    """
    Removes invalid characters from the given ``filename``.

    :param filename:  The "dirty" file name to clean.
    """
    if not isinstance(filename, str):
        filename = str(filename, 'utf-8')
    return INVALID_FILE_CHARS.sub('_', CONTROL_CHARS.sub('', filename))


def delete_file(file_path_name):
    """
    Deletes a file from the system.

    :param file_path_name: The file, including path, to delete.
    """
    if not file_path_name:
        return False
    try:
        if os.path.exists(file_path_name):
            os.remove(file_path_name)
        return True
    except (IOError, OSError):
        log.exception("Unable to delete file %s" % file_path_name)
        return False


def _get_user_agent():
    """
    Return a user agent customised for the platform the user is on.
    """
    browser_list = USER_AGENTS.get(sys.platform, None)
    if not browser_list:
        browser_list = USER_AGENTS['default']
    random_index = randint(0, len(browser_list) - 1)
    return browser_list[random_index]


def get_web_page(url, header=None, update_openlp=False):
    """
    Attempts to download the webpage at url and returns that page or None.

    :param url: The URL to be downloaded.
    :param header:  An optional HTTP header to pass in the request to the web server.
    :param update_openlp: Tells OpenLP to update itself if the page is successfully downloaded.
        Defaults to False.
    """
    # TODO: Add proxy usage. Get proxy info from OpenLP settings, add to a
    # proxy_handler, build into an opener and install the opener into urllib2.
    # http://docs.python.org/library/urllib2.html
    if not url:
        return None
    # This is needed to work around http://bugs.python.org/issue22248 and https://bugs.launchpad.net/openlp/+bug/1251437
    opener = urllib.request.build_opener(HTTPRedirectHandlerFixed())
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url)
    if not header or header[0].lower() != 'user-agent':
        user_agent = _get_user_agent()
        req.add_header('User-Agent', user_agent)
    if header:
        req.add_header(header[0], header[1])
    log.debug('Downloading URL = %s' % url)
    retries = 0
    while retries <= CONNECTION_RETRIES:
        retries += 1
        time.sleep(0.1)
        try:
            page = urllib.request.urlopen(req, timeout=CONNECTION_TIMEOUT)
            log.debug('Downloaded page {}'.format(page.geturl()))
        except urllib.error.URLError as err:
            log.exception('URLError on {}'.format(url))
            log.exception('URLError: {}'.format(err.reason))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.timeout:
            log.exception('Socket timeout: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except socket.gaierror:
            log.exception('Socket gaierror: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except ConnectionRefusedError:
            log.exception('ConnectionRefused: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
            break
        except ConnectionError:
            log.exception('Connection error: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except HTTPException:
            log.exception('HTTPException error: {}'.format(url))
            page = None
            if retries > CONNECTION_RETRIES:
                raise
        except:
            # Don't know what's happening, so reraise the original
            raise
    if update_openlp:
        Registry().get('application').process_events()
    if not page:
        log.exception('{} could not be downloaded'.format(url))
        return None
    log.debug(page)
    return page


def get_uno_command(connection_type='pipe'):
    """
    Returns the UNO command to launch an openoffice.org instance.
    """
    for command in ['libreoffice', 'soffice']:
        if which(command):
            break
    else:
        raise FileNotFoundError('Command not found')

    OPTIONS = '--nologo --norestore --minimized --nodefault --nofirststartwizard'
    if connection_type == 'pipe':
        CONNECTION = '"--accept=pipe,name=openlp_pipe;urp;"'
    else:
        CONNECTION = '"--accept=socket,host=localhost,port=2002;urp;"'
    return '%s %s %s' % (command, OPTIONS, CONNECTION)


def get_uno_instance(resolver, connection_type='pipe'):
    """
    Returns a running openoffice.org instance.

    :param resolver: The UNO resolver to use to find a running instance.
    """
    log.debug('get UNO Desktop Openoffice - resolve')
    if connection_type == 'pipe':
        return resolver.resolve('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')
    else:
        return resolver.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')


def format_time(text, local_time):
    """
    Workaround for Python built-in time formatting function time.strftime().

    time.strftime() accepts only ascii characters. This function accepts
    unicode string and passes individual % placeholders to time.strftime().
    This ensures only ascii characters are passed to time.strftime().

    :param text:  The text to be processed.
    :param local_time: The time to be used to add to the string.  This is a time object
    """
    def match_formatting(match):
        """
        Format the match
        """
        return local_time.strftime(match.group())
    return re.sub('\%[a-zA-Z]', match_formatting, text)


def get_locale_key(string):
    """
    Creates a key for case insensitive, locale aware string sorting.

    :param string: The corresponding string.
    """
    string = string.lower()
    # ICU is the prefered way to handle locale sort key, we fallback to locale.strxfrm which will work in most cases.
    global ICU_COLLATOR
    try:
        if ICU_COLLATOR is None:
            import icu
            from .languagemanager import LanguageManager
            language = LanguageManager.get_language()
            icu_locale = icu.Locale(language)
            ICU_COLLATOR = icu.Collator.createInstance(icu_locale)
        return ICU_COLLATOR.getSortKey(string)
    except:
        return locale.strxfrm(string).encode()


def get_natural_key(string):
    """
    Generate a key for locale aware natural string sorting.
    Returns a list of string compare keys and integers.
    """
    key = DIGITS_OR_NONDIGITS.findall(string)
    key = [int(part) if part.isdigit() else get_locale_key(part) for part in key]
    # Python 3 does not support comparison of different types anymore. So make sure, that we do not compare str
    # and int.
    if string[0].isdigit():
        return [b''] + key
    return key


from .languagemanager import LanguageManager
from .actions import ActionList


__all__ = ['ActionList', 'LanguageManager', 'get_application_version', 'check_latest_version',
           'add_actions', 'get_filesystem_encoding', 'get_web_page', 'get_uno_command', 'get_uno_instance',
           'delete_file', 'clean_filename', 'format_time', 'get_locale_key', 'get_natural_key']
