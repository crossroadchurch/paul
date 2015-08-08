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
The :mod:`osdinteraction` provides miscellaneous functions for interacting with
OSD files.
"""
import os
import json

from tests.utils.constants import TEST_RESOURCES_PATH


def read_service_from_file(file_name):
    """
    Reads an OSD file and returns the first service item found therein.
    @param file_name: File name of an OSD file residing in the tests/resources folder.
    @return: The service contained in the file.
    """
    service_file = os.path.join(TEST_RESOURCES_PATH, 'service', file_name)
    with open(service_file, 'r') as open_file:
        service = json.load(open_file)
    return service
