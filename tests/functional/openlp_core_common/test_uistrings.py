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
Package to test the openlp.core.lib.uistrings package.
"""
from unittest import TestCase

from openlp.core.common import UiStrings


class TestUiStrings(TestCase):

    def check_same_instance_test(self):
        """
        Test the UiStrings class - we always should have only one instance of the UiStrings class.
        """
        # WHEN: Create two instances of the UiStrings class.
        first_instance = UiStrings()
        second_instance = UiStrings()

        # THEN: Check if the instances are the same.
        self.assertIs(first_instance, second_instance, 'Two UiStrings objects should be the same instance')
