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
This script is used to check dependencies of OpenLP. It checks availability
of required python modules and their version. To verify availability of Python
modules, simply run this script::

    @:~$ ./check_dependencies.py

"""
import os
import sys
from distutils.version import LooseVersion

# If we try to import uno before nose this will create a warning. Just try to import nose first to suppress the warning.
try:
    import nose
except ImportError:
    nose = None

IS_WIN = sys.platform.startswith('win')
IS_LIN = sys.platform.startswith('lin')


VERS = {
    'Python': '3.0',
    'PyQt4': '4.6',
    'Qt4': '4.6',
    'sqlalchemy': '0.5',
    # pyenchant 1.6 required on Windows
    'enchant': '1.6' if IS_WIN else '1.3'
}

# pywin32
WIN32_MODULES = [
    'win32com',
    'win32ui',
    'pywintypes',
    'pyodbc',
    'icu',
]

LINUX_MODULES = [
    # Optical drive detection.
    'dbus',
]


MODULES = [
    'PyQt4',
    'PyQt4.QtCore',
    'PyQt4.QtGui',
    'PyQt4.QtNetwork',
    'PyQt4.QtOpenGL',
    'PyQt4.QtSvg',
    'PyQt4.QtTest',
    'PyQt4.QtWebKit',
    'PyQt4.phonon',
    'sqlalchemy',
    'alembic',
    'sqlite3',
    'lxml',
    'chardet',
    'enchant',
    'bs4',
    'mako',
    'uno',
]


OPTIONAL_MODULES = [
    ('mysql.connector', '(MySQL support)', True),
    ('psycopg2', '(PostgreSQL support)', True),
    ('nose', '(testing framework)', True),
    ('mock',  '(testing module)', sys.version_info[1] < 3),
    ('jenkins', '(access jenkins api - package name: jenkins-webapi)', True),
]

w = sys.stdout.write


def check_vers(version, required, text):
    """
    Check the version of a dependency. Returns ``True`` if the version is greater than or equal, or False if less than.

    ``version``
        The actual version of the dependency

    ``required``
        The required version of the dependency

    ``text``
        The dependency's name
    """
    space = (27 - len(required) - len(text)) * ' '
    if not isinstance(version, str):
        version = '.'.join(map(str, version))
    if not isinstance(required, str):
        required = '.'.join(map(str, required))
    w('  %s >= %s ...  ' % (text, required) + space)
    if LooseVersion(version) >= LooseVersion(required):
        w(version + os.linesep)
        return True
    else:
        w('FAIL' + os.linesep)
        return False


def check_module(mod, text='', indent='  '):
    """
    Check that a module is installed.

    ``mod``
        The module to check for.

    ``text``
        The text to display.

    ``indent``
        How much to indent the text by.
    """
    space = (31 - len(mod) - len(text)) * ' '
    w(indent + '%s %s...  ' % (mod, text) + space)
    try:
        __import__(mod)
        w('OK')
    except ImportError:
        w('FAIL')
    w(os.linesep)


def print_vers_fail(required, text):
    print('  %s >= %s ...    FAIL' % (text, required))


def verify_python():
    if not check_vers(list(sys.version_info), VERS['Python'], text='Python'):
        exit(1)


def verify_versions():
    print('Verifying version of modules...')
    try:
        from PyQt4 import QtCore
        check_vers(QtCore.PYQT_VERSION_STR, VERS['PyQt4'], 'PyQt4')
        check_vers(QtCore.qVersion(), VERS['Qt4'], 'Qt4')
    except ImportError:
        print_vers_fail(VERS['PyQt4'], 'PyQt4')
        print_vers_fail(VERS['Qt4'], 'Qt4')
    try:
        import sqlalchemy
        check_vers(sqlalchemy.__version__, VERS['sqlalchemy'], 'sqlalchemy')
    except ImportError:
        print_vers_fail(VERS['sqlalchemy'], 'sqlalchemy')
    try:
        import enchant
        check_vers(enchant.__version__, VERS['enchant'], 'enchant')
    except ImportError:
        print_vers_fail(VERS['enchant'], 'enchant')


def print_enchant_backends_and_languages():
    """
    Check if PyEnchant is installed.
    """
    w('Enchant (spell checker)... ')
    try:
        import enchant
        w(os.linesep)
        backends = ', '.join([x.name for x in enchant.Broker().describe()])
        print('  available backends: %s' % backends)
        langs = ', '.join(enchant.list_languages())
        print('  available languages: %s' % langs)
    except ImportError:
        w('FAIL' + os.linesep)


def print_qt_image_formats():
    """
    Print out the image formats that Qt4 supports.
    """
    w('Qt4 image formats... ')
    try:
        from PyQt4 import QtGui
        read_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()])
        write_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageWriter.supportedImageFormats()])
        w(os.linesep)
        print('  read: %s' % read_f)
        print('  write: %s' % write_f)
    except ImportError:
        w('FAIL' + os.linesep)


def main():
    """
    Run the dependency checker.
    """
    print('Checking Python version...')
    verify_python()
    print('Checking for modules...')
    for m in MODULES:
        check_module(m)
    print('Checking for optional modules...')
    for m in OPTIONAL_MODULES:
        if m[2]:
            check_module(m[0], text=m[1])
    if IS_WIN:
        print('Checking for Windows specific modules...')
        for m in WIN32_MODULES:
            check_module(m)
    elif IS_LIN:
        print('Checking for Linux specific modules...')
        for m in LINUX_MODULES:
            check_module(m)
    verify_versions()
    print_qt_image_formats()
    print_enchant_backends_and_languages()

if __name__ == '__main__':
    main()
