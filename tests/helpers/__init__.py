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
The :mod:`~tests.helpers` module provides helper classes for use in the tests.
"""
from datetime import datetime


class MockDateTime(object):
    return_values = [datetime(2015, 4, 15, 18, 35, 21, 0)]
    call_counter = 0

    @classmethod
    def revert(cls):
        cls.return_values = [datetime(2015, 4, 15, 18, 35, 21, 0)]
        cls.call_counter = 0

    @classmethod
    def now(cls):
        if len(cls.return_values) > cls.call_counter:
            mocked_datetime = cls.return_values[cls.call_counter]
        else:
            mocked_datetime = cls.return_values[-1]
        cls.call_counter += 1
        return mocked_datetime
