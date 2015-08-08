#!/usr/bin/env python3
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
This script is used to maintain the translation files in OpenLP. It downloads
the latest translation files from the Transifex translation server, updates the
local translation files from both the source code and the files from Transifex,
and can also generate the compiled translation files.

Create New Language
-------------------

To create a new language, simply run this script with the ``-c`` command line
option::

    @:~$ ./translation_utils.py -c

Update Translation Files
------------------------

The best way to update the translations is to download the files from Transifex,
and then update the local files using both the downloaded files and the source.
This is done easily via the ``-d``, ``-p`` and ``-u`` options::

    @:~$ ./translation_utils.py -dpu

"""
import os
import urllib.request
import urllib.error
import urllib.parse
from getpass import getpass
import base64
import json
import webbrowser
import glob

from lxml import etree, objectify
from optparse import OptionParser
from PyQt4 import QtCore

SERVER_URL = 'http://www.transifex.net/api/2/project/openlp/resource/openlp-22x/'
IGNORED_PATHS = ['scripts']
IGNORED_FILES = ['setup.py']

verbose_mode = False
quiet_mode = False
username = ''
password = ''


class Command(object):
    """
    Provide an enumeration of commands.
    """
    Download = 1
    Create = 2
    Prepare = 3
    Update = 4
    Generate = 5
    Check = 6


class CommandStack(object):
    """
    This class provides an iterable stack.
    """
    def __init__(self):
        self.current_index = 0
        self.data = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        if index not in self.data:
            return None
        elif self.data[index].get('arguments'):
            return self.data[index]['command'], self.data[index]['arguments']
        else:
            return self.data[index]['command']

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index == len(self.data):
            raise StopIteration
        else:
            current_item = self.data[self.current_index]['command']
            self.current_index += 1
            return current_item

    def append(self, command, **kwargs):
        data = {'command': command}
        if 'arguments' in kwargs:
            data['arguments'] = kwargs['arguments']
        self.data.append(data)

    def reset(self):
        self.current_index = 0

    def arguments(self):
        if self.data[self.current_index - 1].get('arguments'):
            return self.data[self.current_index - 1]['arguments']
        else:
            return []

    def __repr__(self):
        results = []
        for item in self.data:
            if item.get('arguments'):
                results.append(str((item['command'], item['arguments'])))
            else:
                results.append(str((item['command'], )))
        return '[%s]' % ', '.join(results)


def print_quiet(text, linefeed=True):
    """
    This method checks to see if we are in quiet mode, and if not prints ``text`` out.

    :param text: The text to print.
    :param linefeed: Linefeed required
    """
    global quiet_mode
    if not quiet_mode:
        if linefeed:
            print(text)
        else:
            print(text, end=' ')


def print_verbose(text):
    """
    This method checks to see if we are in verbose mode, and if so prints  ``text`` out.

    :param text: The text to print.
    """
    global verbose_mode, quiet_mode
    if not quiet_mode and verbose_mode:
        print('    %s' % text)


def run(command):
    """
    This method runs an external application.

    :param command: The command to run.
    """
    print_verbose(command)
    process = QtCore.QProcess()
    process.start(command)
    while process.waitForReadyRead():
        print_verbose('ReadyRead: %s' % process.readAll())
    print_verbose('Error(s):\n%s' % process.readAllStandardError())
    print_verbose('Output:\n%s' % process.readAllStandardOutput())


def download_translations():
    """
    This method downloads the translation files from the Pootle server.

    **Note:** URLs and headers need to remain strings, not unicode.
    """
    global username, password
    print_quiet('Download translation files from Transifex')
    if not username:
        username = input('   Transifex username: ')
    if not password:
        password = getpass('   Transifex password: ')
    # First get the list of languages
    base64string = base64.encodebytes(('%s:%s' % (username, password)).encode())[:-1]
    auth_header = 'Basic %s' % base64string.decode()
    request = urllib.request.Request(SERVER_URL + '?details')
    request.add_header('Authorization', auth_header)
    print_verbose('Downloading list of languages from: %s' % SERVER_URL)
    try:
        json_response = urllib.request.urlopen(request)
    except urllib.error.HTTPError:
        print_quiet('Username or password incorrect.')
        return False
    json_dict = json.loads(json_response.read().decode())
    languages = [lang['code'] for lang in json_dict['available_languages']]
    for language in languages:
        lang_url = SERVER_URL + 'translation/%s/?file' % language
        request = urllib.request.Request(lang_url)
        request.add_header('Authorization', auth_header)
        filename = os.path.join(os.path.abspath('..'), 'resources', 'i18n', language + '.ts')
        print_verbose('Get Translation File: %s' % filename)
        response = urllib.request.urlopen(request)
        fd = open(filename, 'wb')
        fd.write(response.read())
        fd.close()
    print_quiet('   Done.')
    return True


def prepare_project():
    """
    This method creates the project file needed to update the translation files and compile them into .qm files.
    """
    print_quiet('Generating the openlp.pro file')
    lines = []
    start_dir = os.path.abspath('..')
    start_dir = start_dir + os.sep
    print_verbose('Starting directory: %s' % start_dir)
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            path = root.replace(start_dir, '').replace('\\', '/')
            if file.startswith('hook-') or file.startswith('test_'):
                continue
            ignore = False
            for ignored_path in IGNORED_PATHS:
                if path.startswith(ignored_path):
                    ignore = True
                    break
            if ignore:
                continue
            ignore = False
            for ignored_file in IGNORED_FILES:
                if file == ignored_file:
                    ignore = True
                    break
            if ignore:
                continue
            if file.endswith('.py') or file.endswith('.pyw'):
                if path:
                    line = '%s/%s' % (path, file)
                else:
                    line = file
                print_verbose('Parsing "%s"' % line)
                lines.append('SOURCES      += %s' % line)
            elif file.endswith('.ts'):
                line = '%s/%s' % (path, file)
                print_verbose('Parsing "%s"' % line)
                lines.append('TRANSLATIONS += %s' % line)
    lines.sort()
    file = open(os.path.join(start_dir, 'openlp.pro'), 'w')
    file.write('\n'.join(lines))
    file.close()
    print_quiet('   Done.')


def update_translations():
    print_quiet('Update the translation files')
    if not os.path.exists(os.path.join(os.path.abspath('..'), 'openlp.pro')):
        print('You have not generated a project file yet, please run this script with the -p option.')
        return
    else:
        os.chdir(os.path.abspath('..'))
        run('pylupdate4 -verbose -noobsolete openlp.pro')
        os.chdir(os.path.abspath('scripts'))


def generate_binaries():
    print_quiet('Generate the related *.qm files')
    if not os.path.exists(os.path.join(os.path.abspath('..'), 'openlp.pro')):
        print('You have not generated a project file yet, please run this script with the -p option. It is also ' +
              'recommended that you this script with the -u option to update the translation files as well.')
        return
    else:
        os.chdir(os.path.abspath('..'))
        run('lrelease openlp.pro')
        print_quiet('   Done.')


def create_translation():
    """
    This method opens a browser to the OpenLP project page at Transifex so
    that the user can request a new language.
    """
    print_quiet('Please request a new language at the OpenLP project on Transifex.')
    webbrowser.open('https://www.transifex.net/projects/p/openlp/resource/ents/')
    print_quiet('Opening browser to OpenLP project...')


def check_format_strings():
    """
    This method runs through the ts-files and looks for mismatches between format strings in the original text
    and in the translations.
    """
    path = os.path.join(os.path.abspath('..'), 'resources', 'i18n', '*.ts')
    file_list = glob.glob(path)
    for filename in file_list:
        print_quiet('Checking %s' % filename)
        file = open(filename, 'rb')
        tree = objectify.parse(file)
        root = tree.getroot()
        for tag in root.iter('message'):
            location = tag.location.get('filename')
            line = tag.location.get('line')
            org_text = tag.source.text
            translation = tag.translation.text
            if not translation:
                for num in tag.iter('numerusform'):
                    print_verbose('parsed numerusform: location: %s, source: %s, translation: %s' % (
                                  location, org_text, num.text))
                    if num and org_text.count('%') != num.text.count('%'):
                        print_quiet(
                            'ERROR: Translation from %s at line %s has a mismatch of format input:\n%s\n%s\n' % (
                                location, line, org_text, num.text))
            else:
                print_verbose('parsed: location: %s, source: %s, translation: %s' % (location, org_text, translation))
                if org_text.count('%') != translation.count('%'):
                    print_quiet('ERROR: Translation from %s at line %s has a mismatch of format input:\n%s\n%s\n' % (
                                location, line, org_text, translation))


def process_stack(command_stack):
    """
    This method looks at the commands in the command stack, and processes them
    in the order they are in the stack.

    ``command_stack``
        The command stack to process.
    """
    if command_stack:
        print_quiet('Processing %d commands...' % len(command_stack))
        for command in command_stack:
            print_quiet('%d.' % (command_stack.current_index), False)
            if command == Command.Download:
                if not download_translations():
                    return
            elif command == Command.Prepare:
                prepare_project()
            elif command == Command.Update:
                update_translations()
            elif command == Command.Generate:
                generate_binaries()
            elif command == Command.Create:
                create_translation()
            elif command == Command.Check:
                check_format_strings()
        print_quiet('Finished processing commands.')
    else:
        print_quiet('No commands to process.')


def main():
    global verbose_mode, quiet_mode, username, password
    # Set up command line options.
    usage = '%prog [options]\nOptions are parsed in the order they are ' + \
        'listed below. If no options are given, "-dpug" will be used.\n\n' + \
        'This script is used to manage OpenLP\'s translation files.'
    parser = OptionParser(usage=usage)
    parser.add_option('-U', '--username', dest='username', metavar='USERNAME',
                      help='Transifex username, used for authentication')
    parser.add_option('-P', '--password', dest='password', metavar='PASSWORD',
                      help='Transifex password, used for authentication')
    parser.add_option('-d', '--download-ts', dest='download',
                      action='store_true', help='download language files from Transifex')
    parser.add_option('-c', '--create', dest='create', action='store_true',
                      help='go to Transifex to request a new translation file')
    parser.add_option('-p', '--prepare', dest='prepare', action='store_true',
                      help='generate a project file, used to update the translations')
    parser.add_option('-u', '--update', action='store_true', dest='update',
                      help='update translation files (needs a project file)')
    parser.add_option('-g', '--generate', dest='generate', action='store_true',
                      help='compile .ts files into .qm files')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help='show extra information while processing translations')
    parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                      help='suppress all output other than errors')
    parser.add_option('-f', '--check-format-strings', dest='check', action='store_true',
                      help='check that format strings are matching in translations')
    (options, args) = parser.parse_args()
    # Create and populate the command stack
    command_stack = CommandStack()
    if options.download:
        command_stack.append(Command.Download)
    if options.create:
        command_stack.append(Command.Create, arguments=[options.create])
    if options.prepare:
        command_stack.append(Command.Prepare)
    if options.update:
        command_stack.append(Command.Update)
    if options.generate:
        command_stack.append(Command.Generate)
    if options.check:
        command_stack.append(Command.Check)
    verbose_mode = options.verbose
    quiet_mode = options.quiet
    if options.username:
        username = options.username
    if options.password:
        password = options.password
    if not command_stack:
        command_stack.append(Command.Download)
        command_stack.append(Command.Prepare)
        command_stack.append(Command.Update)
        command_stack.append(Command.Generate)
    # Process the commands
    process_stack(command_stack)

if __name__ == '__main__':
    if os.path.split(os.path.abspath('.'))[1] != 'scripts':
        print('You need to run this script from the scripts directory.')
    else:
        main()
