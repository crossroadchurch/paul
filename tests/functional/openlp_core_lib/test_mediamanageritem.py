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
Package to test the openlp.core.lib.mediamanageritem package.
"""
from unittest import TestCase

from openlp.core.lib import MediaManagerItem

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMediaManagerItem(TestCase, TestMixin):
    """
    Test the MediaManagerItem class
    """
    def setUp(self):
        """
        Mock out stuff for all the tests
        """
        self.setup_patcher = patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup')
        self.mocked_setup = self.setup_patcher.start()
        self.addCleanup(self.setup_patcher.stop)

    @patch(u'openlp.core.lib.mediamanageritem.Settings')
    @patch(u'openlp.core.lib.mediamanageritem.MediaManagerItem.on_preview_click')
    def on_double_clicked_test(self, mocked_on_preview_click, MockedSettings):
        """
        Test that when an item is double-clicked then the item is previewed
        """
        # GIVEN: A setting to enable "Double-click to go live" and a media manager item
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockedSettings.return_value = mocked_settings
        mmi = MediaManagerItem(None)

        # WHEN: on_double_clicked() is called
        mmi.on_double_clicked()

        # THEN: on_preview_click() should have been called
        mocked_on_preview_click.assert_called_with()

    @patch(u'openlp.core.lib.mediamanageritem.Settings')
    @patch(u'openlp.core.lib.mediamanageritem.MediaManagerItem.on_live_click')
    def on_double_clicked_go_live_test(self, mocked_on_live_click, MockedSettings):
        """
        Test that when "Double-click to go live" is enabled that the item goes live
        """
        # GIVEN: A setting to enable "Double-click to go live" and a media manager item
        mocked_settings = MagicMock()
        mocked_settings.value.side_effect = lambda x: x == 'advanced/double click live'
        MockedSettings.return_value = mocked_settings
        mmi = MediaManagerItem(None)

        # WHEN: on_double_clicked() is called
        mmi.on_double_clicked()

        # THEN: on_live_click() should have been called
        mocked_on_live_click.assert_called_with()

    @patch(u'openlp.core.lib.mediamanageritem.Settings')
    @patch(u'openlp.core.lib.mediamanageritem.MediaManagerItem.on_live_click')
    @patch(u'openlp.core.lib.mediamanageritem.MediaManagerItem.on_preview_click')
    def on_double_clicked_single_click_preview_test(self, mocked_on_preview_click, mocked_on_live_click,
                                                    MockedSettings):
        """
        Test that when "Single-click preview" is enabled then nothing happens on double-click
        """
        # GIVEN: A setting to enable "Double-click to go live" and a media manager item
        mocked_settings = MagicMock()
        mocked_settings.value.side_effect = lambda x: x == 'advanced/single click preview'
        MockedSettings.return_value = mocked_settings
        mmi = MediaManagerItem(None)

        # WHEN: on_double_clicked() is called
        mmi.on_double_clicked()

        # THEN: on_live_click() should have been called
        self.assertEqual(0, mocked_on_live_click.call_count, u'on_live_click() should not have been called')
        self.assertEqual(0, mocked_on_preview_click.call_count, u'on_preview_click() should not have been called')
