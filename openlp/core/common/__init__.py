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
The :mod:`common` module contains most of the components and libraries that make
OpenLP work.
"""
import hashlib
import re
import os
import logging
import sys
import traceback
from ipaddress import IPv4Address, IPv6Address, AddressValueError
from codecs import decode, encode

from PyQt4 import QtCore
from PyQt4.QtCore import QCryptographicHash as QHash

log = logging.getLogger(__name__ + '.__init__')


FIRST_CAMEL_REGEX = re.compile('(.)([A-Z][a-z]+)')
SECOND_CAMEL_REGEX = re.compile('([a-z0-9])([A-Z])')


def trace_error_handler(logger):
    """
    Log the calling path of an exception

    :param logger: logger to use so traceback is logged to correct class
    """
    log_string = "OpenLP Error trace"
    for tb in traceback.extract_stack():
        log_string = '%s\n   File %s at line %d \n\t called %s' % (log_string, tb[0], tb[1], tb[3])
    logger.error(log_string)


def check_directory_exists(directory, do_not_log=False):
    """
    Check a theme directory exists and if not create it

    :param directory: The directory to make sure exists
    :param do_not_log: To not log anything. This is need for the start up, when the log isn't ready.
    """
    if not do_not_log:
        log.debug('check_directory_exists %s' % directory)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except IOError as e:
        if not do_not_log:
            log.exception('failed to check if directory exists or create directory')


def get_frozen_path(frozen_option, non_frozen_option):
    """
    Return a path based on the system status.

    :param frozen_option:
    :param non_frozen_option:
    """
    if hasattr(sys, 'frozen') and sys.frozen == 1:
        return frozen_option
    return non_frozen_option


class ThemeLevel(object):
    """
    Provides an enumeration for the level a theme applies to
    """
    Global = 1
    Service = 2
    Song = 3


def translate(context, text, comment=None, encoding=QtCore.QCoreApplication.CodecForTr, n=-1,
              qt_translate=QtCore.QCoreApplication.translate):
    """
    A special shortcut method to wrap around the Qt4 translation functions. This abstracts the translation procedure so
    that we can change it if at a later date if necessary, without having to redo the whole of OpenLP.

    :param context: The translation context, used to give each string a context or a namespace.
    :param text: The text to put into the translation tables for translation.
    :param comment: An identifying string for when the same text is used in different roles within the same context.
    :param encoding:
    :param n:
    :param qt_translate:
    """
    return qt_translate(context, text, comment, encoding, n)


class SlideLimits(object):
    """
    Provides an enumeration for behaviour of OpenLP at the end limits of each service item when pressing the up/down
    arrow keys
    """
    End = 1
    Wrap = 2
    Next = 3


def de_hump(name):
    """
    Change any Camel Case string to python string
    """
    sub_name = FIRST_CAMEL_REGEX.sub(r'\1_\2', name)
    return SECOND_CAMEL_REGEX.sub(r'\1_\2', sub_name).lower()


def is_win():
    """
    Returns true if running on a system with a nt kernel e.g. Windows, Wine

    :return: True if system is running a nt kernel false otherwise
    """
    return os.name.startswith('nt')


def is_macosx():
    """
    Returns true if running on a system with a darwin kernel e.g. Mac OS X

    :return: True if system is running a darwin kernel false otherwise
    """
    return sys.platform.startswith('darwin')


def is_linux():
    """
    Returns true if running on a system with a linux kernel e.g. Ubuntu, Debian, etc

    :return: True if system is running a linux kernel false otherwise
    """
    return sys.platform.startswith('linux')


def verify_ipv4(addr):
    """
    Validate an IPv4 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        valid = IPv4Address(addr)
        return True
    except AddressValueError:
        return False


def verify_ipv6(addr):
    """
    Validate an IPv6 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        valid = IPv6Address(addr)
        return True
    except AddressValueError:
        return False


def verify_ip_address(addr):
    """
    Validate an IP address as either IPv4 or IPv6

    :param addr: Address to validate
    :returns: bool
    """
    return True if verify_ipv4(addr) else verify_ipv6(addr)


def md5_hash(salt, data=None):
    """
    Returns the hashed output of md5sum on salt,data
    using Python3 hashlib

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: str
    """
    log.debug('md5_hash(salt="%s")' % salt)
    hash_obj = hashlib.new('md5')
    hash_obj.update(salt)
    if data:
        hash_obj.update(data)
    hash_value = hash_obj.hexdigest()
    log.debug('md5_hash() returning "%s"' % hash_value)
    return hash_value


def qmd5_hash(salt, data=None):
    """
    Returns the hashed output of MD5Sum on salt, data
    using PyQt4.QCryptographicHash.

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: str
    """
    log.debug('qmd5_hash(salt="%s"' % salt)
    hash_obj = QHash(QHash.Md5)
    hash_obj.addData(salt)
    hash_obj.addData(data)
    hash_value = hash_obj.result().toHex()
    log.debug('qmd5_hash() returning "%s"' % hash_value)
    return hash_value.data()


def clean_button_text(button_text):
    """
    Clean the & and other characters out of button text

    :param button_text: The text to clean
    """
    return button_text.replace('&', '').replace('< ', '').replace(' >', '')


from .openlpmixin import OpenLPMixin
from .registry import Registry
from .registrymixin import RegistryMixin
from .registryproperties import RegistryProperties
from .uistrings import UiStrings
from .settings import Settings
from .applocation import AppLocation
from .historycombobox import HistoryComboBox
