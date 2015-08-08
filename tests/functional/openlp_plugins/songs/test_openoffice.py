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
This module contains tests for the OpenOffice/LibreOffice importer.
"""
from unittest import TestCase

from openlp.core.common import Registry
from openlp.plugins.songs.lib.importers.openoffice import OpenOfficeImport

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestOpenOfficeImport(TestCase, TestMixin):
    """
    Test the :class:`~openlp.plugins.songs.lib.importer.openoffice.OpenOfficeImport` class
    """

    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    @patch('openlp.plugins.songs.lib.importers.openoffice.SongImport')
    def create_importer_test(self, mocked_songimport):
        """
        Test creating an instance of the OpenOfficeImport file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        mocked_manager = MagicMock()

        # WHEN: An importer object is created
        importer = OpenOfficeImport(mocked_manager, filenames=[])

        # THEN: The importer object should not be None
        self.assertIsNotNone(importer, 'Import should not be none')

    @patch('openlp.plugins.songs.lib.importers.openoffice.SongImport')
    def close_ooo_file_test(self, mocked_songimport):
        """
        Test that close_ooo_file catches raised exceptions
        """
        # GIVEN: A mocked out SongImport class, a mocked out "manager" and a document that raises an exception
        mocked_manager = MagicMock()
        importer = OpenOfficeImport(mocked_manager, filenames=[])
        importer.document = MagicMock()
        importer.document.close = MagicMock(side_effect=Exception())

        # WHEN: Calling close_ooo_file
        importer.close_ooo_file()

        # THEN: The document attribute should be None even if an exception is raised')
        self.assertIsNone(importer.document, 'Document should be None even if an exception is raised')
