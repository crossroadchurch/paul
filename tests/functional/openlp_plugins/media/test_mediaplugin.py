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
Test the media plugin
"""
from unittest import TestCase

from openlp.core import Registry
from openlp.plugins.media.mediaplugin import MediaPlugin

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class MediaPluginTest(TestCase, TestMixin):
    """
    Test the media plugin
    """
    def setUp(self):
        Registry.create()

    @patch(u'openlp.plugins.media.mediaplugin.Plugin.initialise')
    @patch(u'openlp.plugins.media.mediaplugin.Settings')
    def initialise_test(self, MockedSettings, mocked_initialise):
        """
        Test that the initialise() method overwrites the built-in one, but still calls it
        """
        # GIVEN: A media plugin instance and a mocked settings object
        media_plugin = MediaPlugin()
        mocked_settings = MagicMock()
        mocked_settings.get_files_from_config.return_value = True  # Not the real value, just need something "true-ish"
        MockedSettings.return_value = mocked_settings

        # WHEN: initialise() is called
        media_plugin.initialise()

        # THEN: The settings should be upgraded and the base initialise() method should be called
        mocked_settings.get_files_from_config.assert_called_with(media_plugin)
        mocked_settings.setValue.assert_called_with('media/media files', True)
        mocked_initialise.assert_called_with()
