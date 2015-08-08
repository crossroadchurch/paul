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
Package to test the openlp.core.ui.listpreviewwidget package.
"""
from unittest import TestCase
from openlp.core.ui.listpreviewwidget import ListPreviewWidget

from tests.functional import patch


class TestListPreviewWidget(TestCase):

    def setUp(self):
        """
        Mock out stuff for all the tests
        """
        self.setup_patcher = patch('openlp.core.ui.listpreviewwidget.ListPreviewWidget._setup')
        self.mocked_setup = self.setup_patcher.start()
        self.addCleanup(self.setup_patcher.stop)

    def new_list_preview_widget_test(self):
        """
        Test that creating an instance of ListPreviewWidget works
        """
        # GIVEN: A ListPreviewWidget class

        # WHEN: An object is created
        list_preview_widget = ListPreviewWidget(None, 1)

        # THEN: The object is not None, and the _setup() method was called.
        self.assertIsNotNone(list_preview_widget, 'The ListPreviewWidget object should not be None')
        self.mocked_setup.assert_called_with(1)
