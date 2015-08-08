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
Package to test the openlp.core.lib package.
"""
import os
from unittest import TestCase

from tests.functional import MagicMock, patch
from tests.utils import assert_length, convert_file_service_item

from openlp.core.common import Registry, md5_hash
from openlp.core.lib import ItemCapabilities, ServiceItem, ServiceItemType

VERSE = 'The Lord said to {r}Noah{/r}: \n'\
        'There\'s gonna be a {su}floody{/su}, {sb}floody{/sb}\n'\
        'The Lord said to {g}Noah{/g}:\n'\
        'There\'s gonna be a {st}floody{/st}, {it}floody{/it}\n'\
        'Get those children out of the muddy, muddy \n'\
        '{r}C{/r}{b}h{/b}{bl}i{/bl}{y}l{/y}{g}d{/g}{pk}'\
        'r{/pk}{o}e{/o}{pp}n{/pp} of the Lord\n'
FOOTER = ['Arky Arky (Unknown)', 'Public Domain', 'CCLI 123456']
TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'service'))


class TestServiceItem(TestCase):

    def setUp(self):
        """
        Set up the Registry
        """
        Registry.create()
        mocked_renderer = MagicMock()
        mocked_renderer.format_slide.return_value = [VERSE]
        Registry().register('renderer', mocked_renderer)
        Registry().register('image_manager', MagicMock())

    def service_item_basic_test(self):
        """
        Test the Service Item - basic test
        """
        # GIVEN: A new service item

        # WHEN: A service item is created (without a plugin)
        service_item = ServiceItem(None)

        # THEN: We should get back a valid service item
        self.assertTrue(service_item.is_valid, 'The new service item should be valid')
        self.assertTrue(service_item.missing_frames(), 'There should not be any frames in the service item')

    def service_item_load_custom_from_service_test(self):
        """
        Test the Service Item - adding a custom slide from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: We add a custom from a saved service
        line = convert_file_service_item(TEST_PATH, 'serviceitem_custom_1.osj')
        service_item.set_from_service(line)

        # THEN: We should get back a valid service item
        self.assertTrue(service_item.is_valid, 'The new service item should be valid')
        assert_length(0, service_item._display_frames, 'The service item should have no display frames')
        assert_length(5, service_item.capabilities, 'There should be 5 default custom item capabilities')

        # WHEN: We render the frames of the service item
        service_item.render(True)

        # THEN: The frames should also be valid
        self.assertEqual('Test Custom', service_item.get_display_title(), 'The title should be "Test Custom"')
        self.assertEqual(VERSE[:-1], service_item.get_frames()[0]['text'],
                         'The returned text matches the input, except the last line feed')
        self.assertEqual(VERSE.split('\n', 1)[0], service_item.get_rendered_frame(1),
                         'The first line has been returned')
        self.assertEqual('Slide 1', service_item.get_frame_title(0), '"Slide 1" has been returned as the title')
        self.assertEqual('Slide 2', service_item.get_frame_title(1), '"Slide 2" has been returned as the title')
        self.assertEqual('', service_item.get_frame_title(2), 'Blank has been returned as the title of slide 3')

    def service_item_load_image_from_service_test(self):
        """
        Test the Service Item - adding an image from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        image_name = 'image_1.jpg'
        test_file = os.path.join(TEST_PATH, image_name)
        frame_array = {'path': test_file, 'title': image_name}

        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: adding an image from a saved Service and mocked exists
        line = convert_file_service_item(TEST_PATH, 'serviceitem_image_1.osj')
        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists,\
                patch('openlp.core.lib.serviceitem.create_thumb') as mocked_create_thumb,\
                patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path') as \
                mocked_get_section_data_path:
            mocked_exists.return_value = True
            mocked_get_section_data_path.return_value = os.path.normpath('/path/')
            service_item.set_from_service(line, TEST_PATH)

        # THEN: We should get back a valid service item
        self.assertTrue(service_item.is_valid, 'The new service item should be valid')
        self.assertEqual(os.path.normpath(test_file), os.path.normpath(service_item.get_rendered_frame(0)),
                         'The first frame should match the path to the image')
        self.assertEqual(frame_array, service_item.get_frames()[0],
                         'The return should match frame array1')
        self.assertEqual(test_file, service_item.get_frame_path(0),
                         'The frame path should match the full path to the image')
        self.assertEqual(image_name, service_item.get_frame_title(0),
                         'The frame title should match the image name')
        self.assertEqual(image_name, service_item.get_display_title(),
                         'The display title should match the first image name')
        self.assertTrue(service_item.is_image(), 'This service item should be of an "image" type')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanMaintain),
                        'This service item should be able to be Maintained')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanPreview),
                        'This service item should be able to be be Previewed')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanLoop),
                        'This service item should be able to be run in a can be made to Loop')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanAppend),
                        'This service item should be able to have new items added to it')

    def service_item_load_image_from_local_service_test(self):
        """
        Test the Service Item - adding an image from a saved local service
        """
        # GIVEN: A new service item and a mocked add icon function
        image_name1 = 'image_1.jpg'
        image_name2 = 'image_2.jpg'
        test_file1 = os.path.normpath(os.path.join('/home/openlp', image_name1))
        test_file2 = os.path.normpath(os.path.join('/home/openlp', image_name2))
        frame_array1 = {'path': test_file1, 'title': image_name1}
        frame_array2 = {'path': test_file2, 'title': image_name2}

        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        service_item2 = ServiceItem(None)
        service_item2.add_icon = MagicMock()

        # WHEN: adding an image from a saved Service and mocked exists
        line = convert_file_service_item(TEST_PATH, 'serviceitem_image_2.osj')
        line2 = convert_file_service_item(TEST_PATH, 'serviceitem_image_2.osj', 1)

        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists, \
                patch('openlp.core.lib.serviceitem.create_thumb') as mocked_create_thumb, \
                patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path') as \
                mocked_get_section_data_path:
            mocked_exists.return_value = True
            mocked_get_section_data_path.return_value = os.path.normpath('/path/')
            service_item2.set_from_service(line2)
            service_item.set_from_service(line)

        # THEN: We should get back a valid service item

        # This test is copied from service_item.py, but is changed since to conform to
        # new layout of service item. The layout use in serviceitem_image_2.osd is actually invalid now.
        self.assertTrue(service_item.is_valid, 'The first service item should be valid')
        self.assertTrue(service_item2.is_valid, 'The second service item should be valid')
        # These test will fail on windows due to the difference in folder seperators
        if os.name != 'nt':
            self.assertEqual(test_file1, service_item.get_rendered_frame(0),
                             'The first frame should match the path to the image')
            self.assertEqual(test_file2, service_item2.get_rendered_frame(0),
                             'The Second frame should match the path to the image')
            self.assertEqual(frame_array1, service_item.get_frames()[0], 'The return should match the frame array1')
            self.assertEqual(frame_array2, service_item2.get_frames()[0], 'The return should match the frame array2')
            self.assertEqual(test_file1, service_item.get_frame_path(0),
                             'The frame path should match the full path to the image')
            self.assertEqual(test_file2, service_item2.get_frame_path(0),
                             'The frame path should match the full path to the image')
        self.assertEqual(image_name1, service_item.get_frame_title(0),
                         'The 1st frame title should match the image name')
        self.assertEqual(image_name2, service_item2.get_frame_title(0),
                         'The 2nd frame title should match the image name')
        self.assertEqual(service_item.name, service_item.title.lower(),
                         'The plugin name should match the display title, as there are > 1 Images')
        self.assertTrue(service_item.is_image(), 'This service item should be of an "image" type')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanMaintain),
                        'This service item should be able to be Maintained')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanPreview),
                        'This service item should be able to be be Previewed')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanLoop),
                        'This service item should be able to be run in a can be made to Loop')
        self.assertTrue(service_item.is_capable(ItemCapabilities.CanAppend),
                        'This service item should be able to have new items added to it')

    def add_from_command_for_a_presentation_test(self):
        """
        Test the Service Item - adding a presentation
        """
        # GIVEN: A service item, a mocked icon and presentation data
        service_item = ServiceItem(None)
        presentation_name = 'test.pptx'
        image = MagicMock()
        display_title = 'DisplayTitle'
        notes = 'Note1\nNote2\n'
        frame = {'title': presentation_name, 'image': image, 'path': TEST_PATH,
                 'display_title': display_title, 'notes': notes}

        # WHEN: adding presentation to service_item
        service_item.add_from_command(TEST_PATH, presentation_name, image, display_title, notes)

        # THEN: verify that it is setup as a Command and that the frame data matches
        self.assertEqual(service_item.service_item_type, ServiceItemType.Command, 'It should be a Command')
        self.assertEqual(service_item.get_frames()[0], frame, 'Frames should match')

    def add_from_comamnd_without_display_title_and_notes_test(self):
        """
        Test the Service Item - add from command, but not presentation
        """
        # GIVEN: A new service item, a mocked icon and image data
        service_item = ServiceItem(None)
        image_name = 'test.img'
        image = MagicMock()
        frame = {'title': image_name, 'image': image, 'path': TEST_PATH,
                 'display_title': None, 'notes': None}

        # WHEN: adding image to service_item
        service_item.add_from_command(TEST_PATH, image_name, image)

        # THEN: verify that it is setup as a Command and that the frame data matches
        self.assertEqual(service_item.service_item_type, ServiceItemType.Command, 'It should be a Command')
        self.assertEqual(service_item.get_frames()[0], frame, 'Frames should match')

    @patch('openlp.core.lib.serviceitem.AppLocation.get_section_data_path')
    def add_from_command_for_a_presentation_thumb_test(self, mocked_get_section_data_path):
        """
        Test the Service Item - adding a presentation, and updating the thumb path
        """
        # GIVEN: A service item, a mocked AppLocation and presentation data
        mocked_get_section_data_path.return_value = os.path.join('mocked', 'section', 'path')
        service_item = ServiceItem(None)
        service_item.has_original_files = False
        service_item.name = 'presentations'
        presentation_name = 'test.pptx'
        thumb = os.path.join('tmp', 'test', 'thumb.png')
        display_title = 'DisplayTitle'
        notes = 'Note1\nNote2\n'
        expected_thumb_path = os.path.join('mocked', 'section', 'path', 'thumbnails',
                                           md5_hash(os.path.join(TEST_PATH, presentation_name).encode('utf-8')),
                                           'thumb.png')
        frame = {'title': presentation_name, 'image': expected_thumb_path, 'path': TEST_PATH,
                 'display_title': display_title, 'notes': notes}

        # WHEN: adding presentation to service_item
        service_item.add_from_command(TEST_PATH, presentation_name, thumb, display_title, notes)

        # THEN: verify that it is setup as a Command and that the frame data matches
        self.assertEqual(service_item.service_item_type, ServiceItemType.Command, 'It should be a Command')
        self.assertEqual(service_item.get_frames()[0], frame, 'Frames should match')

    def service_item_load_optical_media_from_service_test(self):
        """
        Test the Service Item - load an optical media item
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: We load a serviceitem with optical media
        line = convert_file_service_item(TEST_PATH, 'serviceitem-dvd.osj')
        with patch('openlp.core.ui.servicemanager.os.path.exists') as mocked_exists:
            mocked_exists.return_value = True
            service_item.set_from_service(line)

        # THEN: We should get back a valid service item with optical media info
        self.assertTrue(service_item.is_valid, 'The service item should be valid')
        self.assertTrue(service_item.is_capable(ItemCapabilities.IsOptical), 'The item should be Optical')
        self.assertEqual(service_item.start_time, 654.375, 'Start time should be 654.375')
        self.assertEqual(service_item.end_time, 672.069, 'End time should be 672.069')
        self.assertEqual(service_item.media_length, 17.694, 'Media length should be 17.694')

    def service_item_load_song_and_audio_from_service_test(self):
        """
        Test the Service Item - adding a song slide from a saved service
        """
        # GIVEN: A new service item and a mocked add icon function
        service_item = ServiceItem(None)
        service_item.add_icon = MagicMock()

        # WHEN: We add a custom from a saved service
        line = convert_file_service_item(TEST_PATH, 'serviceitem-song-linked-audio.osj')
        service_item.set_from_service(line, '/test/')

        # THEN: We should get back a valid service item
        self.assertTrue(service_item.is_valid, 'The new service item should be valid')
        assert_length(0, service_item._display_frames, 'The service item should have no display frames')
        assert_length(7, service_item.capabilities, 'There should be 7 default custom item capabilities')

        # WHEN: We render the frames of the service item
        service_item.render(True)

        # THEN: The frames should also be valid
        self.assertEqual('Amazing Grace', service_item.get_display_title(), 'The title should be "Amazing Grace"')
        self.assertEqual(VERSE[:-1], service_item.get_frames()[0]['text'],
                         'The returned text matches the input, except the last line feed')
        self.assertEqual(VERSE.split('\n', 1)[0], service_item.get_rendered_frame(1),
                         'The first line has been returned')
        self.assertEqual('Amazing Grace! how sweet the s', service_item.get_frame_title(0),
                         '"Amazing Grace! how sweet the s" has been returned as the title')
        self.assertEqual('’Twas grace that taught my hea', service_item.get_frame_title(1),
                         '"’Twas grace that taught my hea" has been returned as the title')
        self.assertEqual('/test/amazing_grace.mp3', service_item.background_audio[0],
                         '"/test/amazing_grace.mp3" should be in the background_audio list')
