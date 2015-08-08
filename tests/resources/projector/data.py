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
The :mod:`tests.resources.projector.data file contains test data
"""

import os
from openlp.core.lib.projector.db import Projector

# Test data
TEST_DB = os.path.join('tmp', 'openlp-test-projectordb.sql')

TEST1_DATA = Projector(ip='111.111.111.111',
                       port='1111',
                       pin='1111',
                       name='___TEST_ONE___',
                       location='location one',
                       notes='notes one')

TEST2_DATA = Projector(ip='222.222.222.222',
                       port='2222',
                       pin='2222',
                       name='___TEST_TWO___',
                       location='location two',
                       notes='notes two')

TEST3_DATA = Projector(ip='333.333.333.333',
                       port='3333',
                       pin='3333',
                       name='___TEST_THREE___',
                       location='location three',
                       notes='notes three')
