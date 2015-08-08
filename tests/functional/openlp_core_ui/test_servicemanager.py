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
Package to test the openlp.core.ui.slidecontroller package.
"""
from unittest import TestCase

from openlp.core.common import Registry, ThemeLevel
from openlp.core.lib import ServiceItem, ServiceItemType, ItemCapabilities
from openlp.core.ui import ServiceManager

from tests.functional import MagicMock


class TestServiceManager(TestCase):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()

    def initial_service_manager_test(self):
        """
        Test the initial of service manager.
        """
        # GIVEN: A new service manager instance.
        ServiceManager(None)
        # WHEN: the default service manager is built.
        # THEN: The the controller should be registered in the registry.
        self.assertNotEqual(Registry().get('service_manager'), None, 'The base service manager should be registered')

    def create_basic_service_test(self):
        """
        Test the create basic service array
        """
        # GIVEN: A new service manager instance.
        service_manager = ServiceManager(None)
        # WHEN: when the basic service array is created.
        service_manager._save_lite = False
        service_manager.service_theme = 'test_theme'
        service = service_manager.create_basic_service()[0]
        # THEN: The controller should be registered in the registry.
        self.assertNotEqual(service, None, 'The base service should be created')
        self.assertEqual(service['openlp_core']['service-theme'], 'test_theme', 'The test theme should be saved')
        self.assertEqual(service['openlp_core']['lite-service'], False, 'The lite service should be saved')

    def supported_suffixes_test(self):
        """
        Test the create basic service array
        """
        # GIVEN: A new service manager instance.
        service_manager = ServiceManager(None)
        # WHEN: a suffix is added as an individual or a list.
        service_manager.supported_suffixes('txt')
        service_manager.supported_suffixes(['pptx', 'ppt'])
        # THEN: The suffixes should be available to test.
        self.assertEqual('txt' in service_manager.suffixes, True, 'The suffix txt should be in the list')
        self.assertEqual('ppt' in service_manager.suffixes, True, 'The suffix ppt should be in the list')
        self.assertEqual('pptx' in service_manager.suffixes, True, 'The suffix pptx should be in the list')

    def build_context_menu_test(self):
        """
        Test the creation of a context menu from a null service item.
        """
        # GIVEN: A new service manager instance and a default service item.
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have been called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have been called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 1,
                          'Should have been called once')

    def build_song_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type text from Songs.
        """
        # GIVEN: A new service manager instance and a default service item.
        mocked_renderer = MagicMock()
        mocked_renderer.theme_level = ThemeLevel.Song
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', mocked_renderer)
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.OnLoadUpdate)
        service_item.add_capability(ItemCapabilities.AddIfNewItem)
        service_item.add_capability(ItemCapabilities.CanSoftBreak)
        service_item.service_item_type = ServiceItemType.Text
        service_item.edit_id = 1
        service_item._display_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        # THEN we add a 2nd display frame
        service_item._display_frames.append(MagicMock())
        service_manager.context_menu(1)
        # THEN the following additional calls should have occurred.
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 1, 'Should have be called once')

    def build_bible_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type text from Bibles.
        """
        # GIVEN: A new service manager instance and a default service item.
        mocked_renderer = MagicMock()
        mocked_renderer.theme_level = ThemeLevel.Song
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', mocked_renderer)
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.NoLineBreaks)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanWordSplit)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.service_item_type = ServiceItemType.Text
        service_item.edit_id = 1
        service_item._display_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        # THEN we add a 2nd display frame
        service_item._display_frames.append(MagicMock())
        service_manager.context_menu(1)
        # THEN the following additional calls should have occurred.
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 1, 'Should have be called once')

    def build_custom_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type text from Custom.
        """
        # GIVEN: A new service manager instance and a default service item.
        mocked_renderer = MagicMock()
        mocked_renderer.theme_level = ThemeLevel.Song
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', mocked_renderer)
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanSoftBreak)
        service_item.add_capability(ItemCapabilities.OnLoadUpdate)
        service_item.service_item_type = ServiceItemType.Text
        service_item.edit_id = 1
        service_item._display_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        # THEN we add a 2nd display frame
        service_item._display_frames.append(MagicMock())
        service_manager.context_menu(1)
        # THEN the following additional calls should have occurred.
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 1, 'Should have be called once')

    def build_image_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type Image from Image.
        """
        # GIVEN: A new service manager instance and a default service item.
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', MagicMock())
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.CanMaintain)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanAppend)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.service_item_type = ServiceItemType.Image
        service_item.edit_id = 1
        service_item._raw_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        # THEN we add a 2nd display frame and regenerate the menu.
        service_item._raw_frames.append(MagicMock())
        service_manager.context_menu(1)
        # THEN the following additional calls should have occurred.
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 2,
                          'Should have be called twice')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 1, 'Should have be called once')

    def build_media_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type Command from Media.
        """
        # GIVEN: A new service manager instance and a default service item.
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', MagicMock())
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.add_capability(ItemCapabilities.RequiresMedia)
        service_item.service_item_type = ServiceItemType.Command
        service_item.edit_id = 1
        service_item._raw_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        # THEN I change the length of the media and regenerate the menu.
        service_item.set_media_length(5)
        service_manager.context_menu(1)
        # THEN the following additional calls should have occurred.
        self.assertEquals(service_manager.time_action.setVisible.call_count, 3, 'Should have be called three times')

    def build_presentation_pdf_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type Command with PDF from Presentation.
        """
        # GIVEN: A new service manager instance and a default service item.
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', MagicMock())
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.CanMaintain)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanAppend)
        service_item.service_item_type = ServiceItemType.Command
        service_item.edit_id = 1
        service_item._raw_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 2, 'Should have be called twice')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')

    def build_presentation_non_pdf_context_menu_test(self):
        """
        Test the creation of a context menu from service item of type Command with Impress from Presentation.
        """
        # GIVEN: A new service manager instance and a default service item.
        Registry().register('plugin_manager', MagicMock())
        Registry().register('renderer', MagicMock())
        service_manager = ServiceManager(None)
        item = MagicMock()
        item.parent.return_value = False
        item.data.return_value = 0
        service_manager.service_manager_list = MagicMock()
        service_manager.service_manager_list.itemAt.return_value = item
        service_item = ServiceItem(None)
        service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
        service_item.service_item_type = ServiceItemType.Command
        service_item.edit_id = 1
        service_item._raw_frames.append(MagicMock())
        service_manager.service_items.insert(1, {'service_item': service_item})
        service_manager.edit_action = MagicMock()
        service_manager.rename_action = MagicMock()
        service_manager.create_custom_action = MagicMock()
        service_manager.maintain_action = MagicMock()
        service_manager.notes_action = MagicMock()
        service_manager.time_action = MagicMock()
        service_manager.auto_start_action = MagicMock()
        service_manager.auto_play_slides_menu = MagicMock()
        service_manager.auto_play_slides_once = MagicMock()
        service_manager.auto_play_slides_loop = MagicMock()
        service_manager.timed_slide_interval = MagicMock()
        service_manager.theme_menu = MagicMock()
        service_manager.menu = MagicMock()
        # WHEN I define a context menu
        service_manager.context_menu(1)
        # THEN the following calls should have occurred.
        self.assertEquals(service_manager.edit_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.rename_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.create_custom_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.maintain_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.notes_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.time_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_start_action.setVisible.call_count, 1, 'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
        self.assertEquals(service_manager.auto_play_slides_once.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.auto_play_slides_loop.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.timed_slide_interval.setChecked.call_count, 0, 'Should not be called')
        self.assertEquals(service_manager.theme_menu.menuAction().setVisible.call_count, 1,
                          'Should have be called once')
