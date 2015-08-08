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
Package to test the openlp.core.lib.theme package.
"""
from tests.functional import MagicMock, patch
from unittest import TestCase

from openlp.core.lib.theme import ThemeXML


class TestTheme(TestCase):
    """
    Test the functions in the Theme module
    """
    def setUp(self):
        """
        Create the UI
        """
        pass

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        pass

    def new_theme_test(self):
        """
        Test the theme creation - basic test
        """
        # GIVEN: A new theme

        # WHEN: A theme is created
        default_theme = ThemeXML()

        # THEN: We should get some default behaviours
        self.assertTrue(default_theme.background_border_color == '#000000', 'The theme should have a black border')
        self.assertTrue(default_theme.background_type == 'solid', 'The theme should have a solid backgrounds')
        self.assertTrue(default_theme.display_vertical_align == 0,
                        'The theme should have a display_vertical_align of 0')
        self.assertTrue(default_theme.font_footer_name == "Arial",
                        'The theme should have a font_footer_name of Arial')
        self.assertTrue(default_theme.font_main_bold is False, 'The theme should have a font_main_bold of false')
        self.assertTrue(len(default_theme.__dict__) == 47, 'The theme should have 47 variables')
