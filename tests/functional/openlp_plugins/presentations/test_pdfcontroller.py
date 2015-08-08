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
This module contains tests for the PdfController
"""
import os
import shutil
from unittest import TestCase, SkipTest
from tempfile import mkdtemp
from PyQt4 import QtCore, QtGui

from openlp.plugins.presentations.lib.pdfcontroller import PdfController, PdfDocument
from tests.functional import MagicMock
from openlp.core.common import Settings
from openlp.core.lib import ScreenList
from tests.utils.constants import TEST_RESOURCES_PATH
from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'presentations/enable_pdf_program': False,
    'presentations/thumbnail_scheme': ''
}

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestPdfController(TestCase, TestMixin):
    """
    Test the PdfController.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        self.setup_application()
        self.build_settings()
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        Settings().extend_default_settings(__default_settings__)
        self.temp_folder = mkdtemp()
        self.thumbnail_folder = mkdtemp()
        self.mock_plugin = MagicMock()
        self.mock_plugin.settings_section = self.temp_folder

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.screens
        self.destroy_settings()
        shutil.rmtree(self.thumbnail_folder)
        shutil.rmtree(self.temp_folder)

    def constructor_test(self):
        """
        Test the Constructor from the PdfController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = PdfController(plugin=self.mock_plugin)

        # THEN: The name of the presentation controller should be correct
        self.assertEqual('Pdf', controller.name, 'The name of the presentation controller should be correct')

    def load_pdf_test(self):
        """
        Test loading of a Pdf using the PdfController
        """
        # GIVEN: A Pdf-file
        test_file = os.path.join(TEST_RESOURCES_PATH, 'presentations', 'pdf_test1.pdf')

        # WHEN: The Pdf is loaded
        controller = PdfController(plugin=self.mock_plugin)
        if not controller.check_available():
            raise SkipTest('Could not detect mudraw or ghostscript, so skipping PDF test')
        controller.temp_folder = self.temp_folder
        controller.thumbnail_folder = self.thumbnail_folder
        document = PdfDocument(controller, test_file)
        loaded = document.load_presentation()

        # THEN: The load should succeed and we should be able to get a pagecount
        self.assertTrue(loaded, 'The loading of the PDF should succeed.')
        self.assertEqual(3, document.get_slide_count(), 'The pagecount of the PDF should be 3.')

    def load_pdf_pictures_test(self):
        """
        Test loading of a Pdf and check size of generate pictures
        """
        # GIVEN: A Pdf-file
        test_file = os.path.join(TEST_RESOURCES_PATH, 'presentations', 'pdf_test1.pdf')

        # WHEN: The Pdf is loaded
        controller = PdfController(plugin=self.mock_plugin)
        if not controller.check_available():
            raise SkipTest('Could not detect mudraw or ghostscript, so skipping PDF test')
        controller.temp_folder = self.temp_folder
        controller.thumbnail_folder = self.thumbnail_folder
        document = PdfDocument(controller, test_file)
        loaded = document.load_presentation()

        # THEN: The load should succeed and pictures should be created and have been scales to fit the screen
        self.assertTrue(loaded, 'The loading of the PDF should succeed.')
        image = QtGui.QImage(os.path.join(self.temp_folder, 'pdf_test1.pdf', 'mainslide001.png'))
        # Based on the converter used the resolution will differ a bit
        if controller.gsbin:
            self.assertEqual(760, image.height(), 'The height should be 760')
            self.assertEqual(537, image.width(), 'The width should be 537')
        else:
            self.assertEqual(768, image.height(), 'The height should be 768')
            self.assertEqual(543, image.width(), 'The width should be 543')
