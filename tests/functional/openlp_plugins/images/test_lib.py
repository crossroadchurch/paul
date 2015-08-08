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
This module contains tests for the lib submodule of the Images plugin.
"""
from unittest import TestCase

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry
from openlp.plugins.images.lib.db import ImageFilenames, ImageGroups
from openlp.plugins.images.lib.mediaitem import ImageMediaItem
from tests.functional import ANY, MagicMock, patch


class TestImageMediaItem(TestCase):
    """
    This is a test case to test various methods in the ImageMediaItem class.
    """

    def setUp(self):
        self.mocked_main_window = MagicMock()
        Registry.create()
        Registry().register('application', MagicMock())
        Registry().register('service_list', MagicMock())
        Registry().register('main_window', self.mocked_main_window)
        Registry().register('live_controller', MagicMock())
        mocked_plugin = MagicMock()
        with patch('openlp.plugins.images.lib.mediaitem.MediaManagerItem._setup'), \
                patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.setup_item'):
            self.media_item = ImageMediaItem(None, mocked_plugin)
            self.media_item.settings_section = 'images'

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_list')
    @patch('openlp.plugins.images.lib.mediaitem.Settings')
    def validate_and_load_test(self, mocked_settings, mocked_load_list):
        """
        Test that the validate_and_load_test() method when called without a group
        """
        # GIVEN: A list of files
        file_list = ['/path1/image1.jpg', '/path2/image2.jpg']

        # WHEN: Calling validate_and_load with the list of files
        self.media_item.validate_and_load(file_list)

        # THEN: load_list should have been called with the file list and None,
        #       the directory should have been saved to the settings
        mocked_load_list.assert_called_once_with(file_list, None)
        mocked_settings().setValue.assert_called_once_with(ANY, '/path1')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_list')
    @patch('openlp.plugins.images.lib.mediaitem.Settings')
    def validate_and_load_group_test(self, mocked_settings, mocked_load_list):
        """
        Test that the validate_and_load_test() method when called with a group
        """
        # GIVEN: A list of files
        file_list = ['/path1/image1.jpg', '/path2/image2.jpg']

        # WHEN: Calling validate_and_load with the list of files and a group
        self.media_item.validate_and_load(file_list, 'group')

        # THEN: load_list should have been called with the file list and the group name,
        #       the directory should have been saved to the settings
        mocked_load_list.assert_called_once_with(file_list, 'group')
        mocked_settings().setValue.assert_called_once_with(ANY, '/path1')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_full_list')
    def save_new_images_list_empty_list_test(self, mocked_load_full_list):
        """
        Test that the save_new_images_list() method handles empty lists gracefully
        """
        # GIVEN: An empty image_list
        image_list = []
        self.media_item.manager = MagicMock()

        # WHEN: We run save_new_images_list with the empty list
        self.media_item.save_new_images_list(image_list)

        # THEN: The save_object() method should not have been called
        self.assertEquals(self.media_item.manager.save_object.call_count, 0,
                          'The save_object() method should not have been called')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_full_list')
    def save_new_images_list_single_image_with_reload_test(self, mocked_load_full_list):
        """
        Test that the save_new_images_list() calls load_full_list() when reload_list is set to True
        """
        # GIVEN: A list with 1 image and a mocked out manager
        image_list = ['test_image.jpg']
        ImageFilenames.filename = ''
        self.media_item.manager = MagicMock()

        # WHEN: We run save_new_images_list with reload_list=True
        self.media_item.save_new_images_list(image_list, reload_list=True)

        # THEN: load_full_list() should have been called
        self.assertEquals(mocked_load_full_list.call_count, 1, 'load_full_list() should have been called')

        # CLEANUP: Remove added attribute from ImageFilenames
        delattr(ImageFilenames, 'filename')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_full_list')
    def save_new_images_list_single_image_without_reload_test(self, mocked_load_full_list):
        """
        Test that the save_new_images_list() doesn't call load_full_list() when reload_list is set to False
        """
        # GIVEN: A list with 1 image and a mocked out manager
        image_list = ['test_image.jpg']
        self.media_item.manager = MagicMock()

        # WHEN: We run save_new_images_list with reload_list=False
        self.media_item.save_new_images_list(image_list, reload_list=False)

        # THEN: load_full_list() should not have been called
        self.assertEquals(mocked_load_full_list.call_count, 0, 'load_full_list() should not have been called')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_full_list')
    def save_new_images_list_multiple_images_test(self, mocked_load_full_list):
        """
        Test that the save_new_images_list() saves all images in the list
        """
        # GIVEN: A list with 3 images
        image_list = ['test_image_1.jpg', 'test_image_2.jpg', 'test_image_3.jpg']
        self.media_item.manager = MagicMock()

        # WHEN: We run save_new_images_list with the list of 3 images
        self.media_item.save_new_images_list(image_list, reload_list=False)

        # THEN: load_full_list() should not have been called
        self.assertEquals(self.media_item.manager.save_object.call_count, 3,
                          'load_full_list() should have been called three times')

    @patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.load_full_list')
    def save_new_images_list_other_objects_in_list_test(self, mocked_load_full_list):
        """
        Test that the save_new_images_list() ignores everything in the provided list except strings
        """
        # GIVEN: A list with images and objects
        image_list = ['test_image_1.jpg', None, True, ImageFilenames(), 'test_image_2.jpg']
        self.media_item.manager = MagicMock()

        # WHEN: We run save_new_images_list with the list of images and objects
        self.media_item.save_new_images_list(image_list, reload_list=False)

        # THEN: load_full_list() should not have been called
        self.assertEquals(self.media_item.manager.save_object.call_count, 2,
                          'load_full_list() should have been called only once')

    def on_reset_click_test(self):
        """
        Test that on_reset_click() actually resets the background
        """
        # GIVEN: A mocked version of reset_action
        self.media_item.reset_action = MagicMock()

        # WHEN: on_reset_click is called
        self.media_item.on_reset_click()

        # THEN: the reset_action should be set visible, and the image should be reset
        self.media_item.reset_action.setVisible.assert_called_with(False)
        self.media_item.live_controller.display.reset_image.assert_called_with()

    @patch('openlp.plugins.images.lib.mediaitem.delete_file')
    def recursively_delete_group_test(self, mocked_delete_file):
        """
        Test that recursively_delete_group() works
        """
        # GIVEN: An ImageGroups object and mocked functions
        ImageFilenames.group_id = 1
        ImageGroups.parent_id = 1
        self.media_item.manager = MagicMock()
        self.media_item.manager.get_all_objects.side_effect = self._recursively_delete_group_side_effect
        self.media_item.service_path = ''
        test_group = ImageGroups()
        test_group.id = 1

        # WHEN: recursively_delete_group() is called
        self.media_item.recursively_delete_group(test_group)

        # THEN: delete_file() should have been called 12 times and manager.delete_object() 7 times.
        self.assertEquals(mocked_delete_file.call_count, 12, 'delete_file() should have been called 12 times')
        self.assertEquals(self.media_item.manager.delete_object.call_count, 7,
                          'manager.delete_object() should be called exactly 7 times')

        # CLEANUP: Remove added attribute from Image Filenames and ImageGroups
        delattr(ImageFilenames, 'group_id')
        delattr(ImageGroups, 'parent_id')

    def _recursively_delete_group_side_effect(*args, **kwargs):
        """
        Side effect method that creates custom return values for the recursively_delete_group method
        """
        if args[1] == ImageFilenames and args[2]:
            # Create some fake objects that should be removed
            returned_object1 = ImageFilenames()
            returned_object1.id = 1
            returned_object1.filename = '/tmp/test_file_1.jpg'
            returned_object2 = ImageFilenames()
            returned_object2.id = 2
            returned_object2.filename = '/tmp/test_file_2.jpg'
            returned_object3 = ImageFilenames()
            returned_object3.id = 3
            returned_object3.filename = '/tmp/test_file_3.jpg'
            return [returned_object1, returned_object2, returned_object3]
        if args[1] == ImageGroups and args[2]:
            # Change the parent_id that is matched so we don't get into an endless loop
            ImageGroups.parent_id = 0
            # Create a fake group that will be used in the next run
            returned_object1 = ImageGroups()
            returned_object1.id = 1
            return [returned_object1]
        return []

    @patch('openlp.plugins.images.lib.mediaitem.delete_file')
    @patch('openlp.plugins.images.lib.mediaitem.check_item_selected')
    def on_delete_click_test(self, mocked_check_item_selected, mocked_delete_file):
        """
        Test that on_delete_click() works
        """
        # GIVEN: An ImageGroups object and mocked functions
        mocked_check_item_selected.return_value = True
        test_image = ImageFilenames()
        test_image.id = 1
        test_image.group_id = 1
        test_image.filename = 'imagefile.png'
        self.media_item.manager = MagicMock()
        self.media_item.service_path = ''
        self.media_item.list_view = MagicMock()
        mocked_row_item = MagicMock()
        mocked_row_item.data.return_value = test_image
        mocked_row_item.text.return_value = ''
        self.media_item.list_view.selectedItems.return_value = [mocked_row_item]

        # WHEN: Calling on_delete_click
        self.media_item.on_delete_click()

        # THEN: delete_file should have been called twice
        self.assertEquals(mocked_delete_file.call_count, 2, 'delete_file() should have been called twice')

    def create_item_from_id_test(self):
        """
        Test that the create_item_from_id() method returns a valid QTreeWidgetItem with a pre-created ImageFilenames
        """
        # GIVEN: An ImageFilenames that already exists in the database
        image_file = ImageFilenames()
        image_file.id = 1
        image_file.filename = '/tmp/test_file_1.jpg'
        self.media_item.manager = MagicMock()
        self.media_item.manager.get_object_filtered.return_value = image_file
        ImageFilenames.filename = ''

        # WHEN: create_item_from_id() is called
        item = self.media_item.create_item_from_id(1)

        # THEN: A QTreeWidgetItem should be created with the above model object as it's data
        self.assertIsInstance(item, QtGui.QTreeWidgetItem)
        self.assertEqual('test_file_1.jpg', item.text(0))
        item_data = item.data(0, QtCore.Qt.UserRole)
        self.assertIsInstance(item_data, ImageFilenames)
        self.assertEqual(1, item_data.id)
        self.assertEqual('/tmp/test_file_1.jpg', item_data.filename)
