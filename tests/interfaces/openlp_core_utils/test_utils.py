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
Functional tests to test the AppLocation class and related methods.
"""
import os
from unittest import TestCase

from openlp.core.utils import is_not_image_file
from tests.utils.constants import TEST_RESOURCES_PATH
from tests.helpers.testmixin import TestMixin


class TestUtils(TestCase, TestMixin):
    """
    A test suite to test out various methods around the Utils functions.
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        self.setup_application()

    def is_not_image_empty_test(self):
        """
        Test the method handles an empty string
        """
        # Given and empty string
        file_name = ""

        # WHEN testing for it
        result = is_not_image_file(file_name)

        # THEN the result is false
        assert result is True, 'The missing file test should return True'

    def is_not_image_with_image_file_test(self):
        """
        Test the method handles an image file
        """
        # Given and empty string
        file_name = os.path.join(TEST_RESOURCES_PATH, 'church.jpg')

        # WHEN testing for it
        result = is_not_image_file(file_name)

        # THEN the result is false
        assert result is False, 'The file is present so the test should return False'

    def is_not_image_with_none_image_file_test(self):
        """
        Test the method handles a non image file
        """
        # Given and empty string
        file_name = os.path.join(TEST_RESOURCES_PATH, 'serviceitem_custom_1.osj')

        # WHEN testing for it
        result = is_not_image_file(file_name)

        # THEN the result is false
        assert result is True, 'The file is not an image file so the test should return True'
