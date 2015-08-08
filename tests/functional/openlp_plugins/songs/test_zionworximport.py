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
This module contains tests for the ZionWorx song importer.
"""

from unittest import TestCase

from tests.functional import MagicMock, patch
from openlp.plugins.songs.lib.importers.zionworx import ZionWorxImport
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.core.common import Registry


class TestZionWorxImport(TestCase):
    """
    Test the functions in the :mod:`zionworximport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    def create_importer_test(self):
        """
        Test creating an instance of the ZionWorx file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.zionworx.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = ZionWorxImport(mocked_manager, filenames=[])

            # THEN: The importer should be an instance of SongImport
            self.assertIsInstance(importer, SongImport)
