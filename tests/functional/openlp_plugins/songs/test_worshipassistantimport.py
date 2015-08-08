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
The :mod:`worshipassistantimport` module provides the functionality for importing
WorshipAssistant song files into the current installation database.
"""

import os

from tests.helpers.songfileimport import SongImportTestHelper

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'worshipassistantsongs'))


class TestWorshipAssistantFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'WorshipAssistantImport'
        self.importer_module_name = 'worshipassistant'
        super(TestWorshipAssistantFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an Worship Assistant file works correctly
        """
        self.file_import(os.path.join(TEST_PATH, 'du_herr.csv'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'du_herr.json')))
        self.file_import(os.path.join(TEST_PATH, 'would_you_be_free.csv'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'would_you_be_free.json')))
        self.file_import(os.path.join(TEST_PATH, 'would_you_be_free2.csv'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'would_you_be_free.json')))
        self.file_import(os.path.join(TEST_PATH, 'lift_up_your_heads.csv'),
                         self.load_external_result_data(os.path.join(TEST_PATH, 'lift_up_your_heads.json')))
