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
import os
import json


def assert_length(expected, iterable, msg=None):
    if len(iterable) != expected:
        if not msg:
            msg = 'Expected length %s, got %s' % (expected, len(iterable))
        raise AssertionError(msg)


def convert_file_service_item(test_path, name, row=0):
    service_file = os.path.join(test_path, name)
    open_file = open(service_file, 'r')
    try:
        items = json.load(open_file)
        first_line = items[row]
    except IOError:
        first_line = ''
    finally:
        open_file.close()
    return first_line
