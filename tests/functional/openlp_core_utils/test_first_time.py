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
Package to test the openlp.core.utils.__init__ package.
"""

from unittest import TestCase
import urllib.request
import urllib.error
import urllib.parse

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin

from openlp.core.utils import CONNECTION_TIMEOUT, CONNECTION_RETRIES, get_web_page


class TestFirstTimeWizard(TestMixin, TestCase):
    """
    Test First Time Wizard import functions
    """
    def webpage_connection_retry_test(self):
        """
        Test get_web_page will attempt CONNECTION_RETRIES+1 connections - bug 1409031
        """
        # GIVEN: Initial settings and mocks
        with patch.object(urllib.request, 'urlopen') as mocked_urlopen:
            mocked_urlopen.side_effect = ConnectionError

            # WHEN: A webpage is requested
            try:
                get_web_page(url='http://localhost')
            except:
                pass

            # THEN: urlopen should have been called CONNECTION_RETRIES + 1 count
            self.assertEquals(mocked_urlopen.call_count, CONNECTION_RETRIES + 1,
                              'get_web_page() should have tried {} times'.format(CONNECTION_RETRIES))
