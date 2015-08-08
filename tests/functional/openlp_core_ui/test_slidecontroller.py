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
from PyQt4 import QtCore, QtGui

from unittest import TestCase
from openlp.core import Registry
from openlp.core.lib import ServiceItemAction
from openlp.core.ui import SlideController, LiveController, PreviewController
from openlp.core.ui.slidecontroller import InfoLabel, WIDE_MENU, NON_TEXT_MENU

from tests.functional import MagicMock, patch


class TestSlideController(TestCase):

    def initial_slide_controller_test(self):
        """
        Test the initial slide controller state .
        """
        # GIVEN: A new SlideController instance.
        slide_controller = SlideController(None)

        # WHEN: the default controller is built.
        # THEN: The controller should not be a live controller.
        self.assertEqual(slide_controller.is_live, False, 'The base slide controller should not be a live controller')

    def text_service_item_blank_test(self):
        """
        Test that loading a text-based service item into the slide controller sets the correct blank menu
        """
        # GIVEN: A new SlideController instance.
        slide_controller = SlideController(None)
        service_item = MagicMock()
        toolbar = MagicMock()
        toolbar.set_widget_visible = MagicMock()
        slide_controller.toolbar = toolbar
        slide_controller.service_item = service_item

        # WHEN: a text based service item is used
        slide_controller.service_item.is_text = MagicMock(return_value=True)
        slide_controller.set_blank_menu()

        # THEN: the call to set the visible items on the toolbar should be correct
        toolbar.set_widget_visible.assert_called_with(WIDE_MENU, True)

    def non_text_service_item_blank_test(self):
        """
        Test that loading a non-text service item into the slide controller sets the correct blank menu
        """
        # GIVEN: A new SlideController instance.
        slide_controller = SlideController(None)
        service_item = MagicMock()
        toolbar = MagicMock()
        toolbar.set_widget_visible = MagicMock()
        slide_controller.toolbar = toolbar
        slide_controller.service_item = service_item

        # WHEN a non text based service item is used
        slide_controller.service_item.is_text = MagicMock(return_value=False)
        slide_controller.set_blank_menu()

        # THEN: then call set up the toolbar to blank the display screen.
        toolbar.set_widget_visible.assert_called_with(NON_TEXT_MENU, True)

    @patch('openlp.core.ui.slidecontroller.Settings')
    def receive_spin_delay_test(self, MockedSettings):
        """
        Test that the spin box is updated accordingly after a call to receive_spin_delay()
        """
        # GIVEN: A new SlideController instance.
        mocked_value = MagicMock(return_value=1)
        MockedSettings.return_value = MagicMock(value=mocked_value)
        mocked_delay_spin_box = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.delay_spin_box = mocked_delay_spin_box

        # WHEN: The receive_spin_delay() method is called
        slide_controller.receive_spin_delay()

        # THEN: The Settings()value() and delay_spin_box.setValue() methods should have been called correctly
        mocked_value.assert_called_with('core/loop delay')
        mocked_delay_spin_box.setValue.assert_called_with(1)

    def toggle_display_blank_test(self):
        """
        Check that the toggle_display('blank') method calls the on_blank_display() method
        """
        # GIVEN: A new SlideController instance.
        mocked_on_blank_display = MagicMock()
        mocked_on_theme_display = MagicMock()
        mocked_on_hide_display = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = mocked_on_blank_display
        slide_controller.on_theme_display = mocked_on_theme_display
        slide_controller.on_hide_display = mocked_on_hide_display

        # WHEN: toggle_display() is called with an argument of "blank"
        slide_controller.toggle_display('blank')

        # THEN: Only on_blank_display() should have been called with an argument of True
        mocked_on_blank_display.assert_called_once_with(True)
        self.assertEqual(0, mocked_on_theme_display.call_count, 'on_theme_display should not have been called')
        self.assertEqual(0, mocked_on_hide_display.call_count, 'on_hide_display should not have been called')

    def toggle_display_hide_test(self):
        """
        Check that the toggle_display('hide') method calls the on_blank_display() method
        """
        # GIVEN: A new SlideController instance.
        mocked_on_blank_display = MagicMock()
        mocked_on_theme_display = MagicMock()
        mocked_on_hide_display = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = mocked_on_blank_display
        slide_controller.on_theme_display = mocked_on_theme_display
        slide_controller.on_hide_display = mocked_on_hide_display

        # WHEN: toggle_display() is called with an argument of "hide"
        slide_controller.toggle_display('hide')

        # THEN: Only on_blank_display() should have been called with an argument of True
        mocked_on_blank_display.assert_called_once_with(True)
        self.assertEqual(0, mocked_on_theme_display.call_count, 'on_theme_display should not have been called')
        self.assertEqual(0, mocked_on_hide_display.call_count, 'on_hide_display should not have been called')

    def toggle_display_theme_test(self):
        """
        Check that the toggle_display('theme') method calls the on_theme_display() method
        """
        # GIVEN: A new SlideController instance.
        mocked_on_blank_display = MagicMock()
        mocked_on_theme_display = MagicMock()
        mocked_on_hide_display = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = mocked_on_blank_display
        slide_controller.on_theme_display = mocked_on_theme_display
        slide_controller.on_hide_display = mocked_on_hide_display

        # WHEN: toggle_display() is called with an argument of "theme"
        slide_controller.toggle_display('theme')

        # THEN: Only on_theme_display() should have been called with an argument of True
        mocked_on_theme_display.assert_called_once_with(True)
        self.assertEqual(0, mocked_on_blank_display.call_count, 'on_blank_display should not have been called')
        self.assertEqual(0, mocked_on_hide_display.call_count, 'on_hide_display should not have been called')

    def toggle_display_desktop_test(self):
        """
        Check that the toggle_display('desktop') method calls the on_hide_display() method
        """
        # GIVEN: A new SlideController instance.
        mocked_on_blank_display = MagicMock()
        mocked_on_theme_display = MagicMock()
        mocked_on_hide_display = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = mocked_on_blank_display
        slide_controller.on_theme_display = mocked_on_theme_display
        slide_controller.on_hide_display = mocked_on_hide_display

        # WHEN: toggle_display() is called with an argument of "desktop"
        slide_controller.toggle_display('desktop')

        # THEN: Only on_hide_display() should have been called with an argument of True
        mocked_on_hide_display.assert_called_once_with(True)
        self.assertEqual(0, mocked_on_blank_display.call_count, 'on_blank_display should not have been called')
        self.assertEqual(0, mocked_on_theme_display.call_count, 'on_theme_display should not have been called')

    def toggle_display_show_test(self):
        """
        Check that the toggle_display('show') method calls all the on_X_display() methods
        """
        # GIVEN: A new SlideController instance.
        mocked_on_blank_display = MagicMock()
        mocked_on_theme_display = MagicMock()
        mocked_on_hide_display = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = mocked_on_blank_display
        slide_controller.on_theme_display = mocked_on_theme_display
        slide_controller.on_hide_display = mocked_on_hide_display

        # WHEN: toggle_display() is called with an argument of "show"
        slide_controller.toggle_display('show')

        # THEN: All the on_X_display() methods should have been called with an argument of False
        mocked_on_blank_display.assert_called_once_with(False)
        mocked_on_theme_display.assert_called_once_with(False)
        mocked_on_hide_display.assert_called_once_with(False)

    def live_escape_test(self):
        """
        Test that when the live_escape() method is called, the display is set to invisible and any media is stopped
        """
        # GIVEN: A new SlideController instance and mocked out display and media_controller
        mocked_display = MagicMock()
        mocked_media_controller = MagicMock()
        Registry.create()
        Registry().register('media_controller', mocked_media_controller)
        slide_controller = SlideController(None)
        slide_controller.display = mocked_display
        play_slides = MagicMock()
        play_slides.isChecked.return_value = False
        slide_controller.play_slides_loop = play_slides
        slide_controller.play_slides_once = play_slides

        # WHEN: live_escape() is called
        slide_controller.live_escape()

        # THEN: the display should be set to invisible and the media controller stopped
        mocked_display.setVisible.assert_called_once_with(False)
        mocked_media_controller.media_stop.assert_called_once_with(slide_controller)

    def on_go_live_live_controller_test(self):
        """
        Test that when the on_go_live() method is called the message is sent to the live controller and focus is
        set correctly.
        """
        # GIVEN: A new SlideController instance and plugin preview then pressing go live should respond
        mocked_display = MagicMock()
        mocked_live_controller = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_service_item = MagicMock()
        mocked_service_item.from_service = False
        mocked_preview_widget.current_slide_number.return_value = 1
        mocked_preview_widget.slide_count.return_value = 2
        mocked_live_controller.preview_widget = MagicMock()
        Registry.create()
        Registry().register('live_controller', mocked_live_controller)
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_service_item
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller.display = mocked_display

        # WHEN: on_go_live() is called
        slide_controller.on_go_live()

        # THEN: the live controller should have the service item and the focus set to live
        mocked_live_controller.add_service_manager_item.assert_called_once_with(mocked_service_item, 1)
        mocked_live_controller.preview_widget.setFocus.assert_called_once_with()

    def on_go_live_service_manager_test(self):
        """
        Test that when the on_go_live() method is called the message is sent to the live controller and focus is
        set correctly.
        """
        # GIVEN: A new SlideController instance and service manager preview then pressing go live should respond
        mocked_display = MagicMock()
        mocked_service_manager = MagicMock()
        mocked_live_controller = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_service_item = MagicMock()
        mocked_service_item.from_service = True
        mocked_service_item.unique_identifier = 42
        mocked_preview_widget.current_slide_number.return_value = 1
        mocked_preview_widget.slide_count.return_value = 2
        mocked_live_controller.preview_widget = MagicMock()
        Registry.create()
        Registry().register('live_controller', mocked_live_controller)
        Registry().register('service_manager', mocked_service_manager)
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_service_item
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller.display = mocked_display

        # WHEN: on_go_live() is called
        slide_controller.on_go_live()

        # THEN: the service manager should have the service item and the focus set to live
        mocked_service_manager.preview_live.assert_called_once_with(42, 1)
        mocked_live_controller.preview_widget.setFocus.assert_called_once_with()

    def service_previous_test(self):
        """
        Check that calling the service_previous() method adds the previous key to the queue and processes the queue
        """
        # GIVEN: A new SlideController instance.
        mocked_keypress_queue = MagicMock()
        mocked_process_queue = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.keypress_queue = mocked_keypress_queue
        slide_controller._process_queue = mocked_process_queue

        # WHEN: The service_previous() method is called
        slide_controller.service_previous()

        # THEN: The keypress is added to the queue and the queue is processed
        mocked_keypress_queue.append.assert_called_once_with(ServiceItemAction.Previous)
        mocked_process_queue.assert_called_once_with()

    def service_next_test(self):
        """
        Check that calling the service_next() method adds the next key to the queue and processes the queue
        """
        # GIVEN: A new SlideController instance and mocked out methods
        mocked_keypress_queue = MagicMock()
        mocked_process_queue = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.keypress_queue = mocked_keypress_queue
        slide_controller._process_queue = mocked_process_queue

        # WHEN: The service_next() method is called
        slide_controller.service_next()

        # THEN: The keypress is added to the queue and the queue is processed
        mocked_keypress_queue.append.assert_called_once_with(ServiceItemAction.Next)
        mocked_process_queue.assert_called_once_with()

    @patch('openlp.core.ui.slidecontroller.Settings')
    def update_slide_limits_test(self, MockedSettings):
        """
        Test that calling the update_slide_limits() method updates the slide limits
        """
        # GIVEN: A mocked out Settings object, a new SlideController and a mocked out main_window
        mocked_value = MagicMock(return_value=10)
        MockedSettings.return_value = MagicMock(value=mocked_value)
        mocked_main_window = MagicMock(advanced_settings_section='advanced')
        Registry.create()
        Registry().register('main_window', mocked_main_window)
        slide_controller = SlideController(None)

        # WHEN: update_slide_limits() is called
        slide_controller.update_slide_limits()

        # THEN: The value of slide_limits should be 10
        mocked_value.assert_called_once_with('advanced/slide limits')
        self.assertEqual(10, slide_controller.slide_limits, 'Slide limits should have been updated to 10')

    def enable_tool_bar_live_test(self):
        """
        Check that when enable_tool_bar on a live slide controller is called, enable_live_tool_bar is called
        """
        # GIVEN: Mocked out enable methods and a real slide controller which is set to live
        mocked_enable_live_tool_bar = MagicMock()
        mocked_enable_preview_tool_bar = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.is_live = True
        slide_controller.enable_live_tool_bar = mocked_enable_live_tool_bar
        slide_controller.enable_preview_tool_bar = mocked_enable_preview_tool_bar
        mocked_service_item = MagicMock()

        # WHEN: enable_tool_bar() is called
        slide_controller.enable_tool_bar(mocked_service_item)

        # THEN: The enable_live_tool_bar() method is called, not enable_preview_tool_bar()
        mocked_enable_live_tool_bar.assert_called_once_with(mocked_service_item)
        self.assertEqual(0, mocked_enable_preview_tool_bar.call_count, 'The preview method should not have been called')

    def enable_tool_bar_preview_test(self):
        """
        Check that when enable_tool_bar on a preview slide controller is called, enable_preview_tool_bar is called
        """
        # GIVEN: Mocked out enable methods and a real slide controller which is set to live
        mocked_enable_live_tool_bar = MagicMock()
        mocked_enable_preview_tool_bar = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.is_live = False
        slide_controller.enable_live_tool_bar = mocked_enable_live_tool_bar
        slide_controller.enable_preview_tool_bar = mocked_enable_preview_tool_bar
        mocked_service_item = MagicMock()

        # WHEN: enable_tool_bar() is called
        slide_controller.enable_tool_bar(mocked_service_item)

        # THEN: The enable_preview_tool_bar() method is called, not enable_live_tool_bar()
        mocked_enable_preview_tool_bar.assert_called_once_with(mocked_service_item)
        self.assertEqual(0, mocked_enable_live_tool_bar.call_count, 'The live method should not have been called')

    def refresh_service_item_text_test(self):
        """
        Test that the refresh_service_item() method refreshes a text service item
        """
        # GIVEN: A mock service item and a fresh slide controller
        mocked_service_item = MagicMock()
        mocked_service_item.is_text.return_value = True
        mocked_service_item.is_image.return_value = False
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_service_item
        slide_controller._process_item = mocked_process_item
        slide_controller.selected_row = 5

        # WHEN: The refresh_service_item method() is called
        slide_controller.refresh_service_item()

        # THEN: The item should be re-processed
        mocked_service_item.is_text.assert_called_once_with()
        self.assertEqual(0, mocked_service_item.is_image.call_count, 'is_image should not have been called')
        mocked_service_item.render.assert_called_once_with()
        mocked_process_item.assert_called_once_with(mocked_service_item, 5)

    def refresh_service_item_image_test(self):
        """
        Test that the refresh_service_item() method refreshes a image service item
        """
        # GIVEN: A mock service item and a fresh slide controller
        mocked_service_item = MagicMock()
        mocked_service_item.is_text.return_value = False
        mocked_service_item.is_image.return_value = True
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_service_item
        slide_controller._process_item = mocked_process_item
        slide_controller.selected_row = 5

        # WHEN: The refresh_service_item method() is called
        slide_controller.refresh_service_item()

        # THEN: The item should be re-processed
        mocked_service_item.is_text.assert_called_once_with()
        mocked_service_item.is_image.assert_called_once_with()
        mocked_service_item.render.assert_called_once_with()
        mocked_process_item.assert_called_once_with(mocked_service_item, 5)

    def refresh_service_item_not_image_or_text_test(self):
        """
        Test that the refresh_service_item() method does not refresh a service item if it's neither text or an image
        """
        # GIVEN: A mock service item and a fresh slide controller
        mocked_service_item = MagicMock()
        mocked_service_item.is_text.return_value = False
        mocked_service_item.is_image.return_value = False
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_service_item
        slide_controller._process_item = mocked_process_item
        slide_controller.selected_row = 5

        # WHEN: The refresh_service_item method() is called
        slide_controller.refresh_service_item()

        # THEN: The item should be re-processed
        mocked_service_item.is_text.assert_called_once_with()
        mocked_service_item.is_image.assert_called_once_with()
        self.assertEqual(0, mocked_service_item.render.call_count, 'The render() method should not have been called')
        self.assertEqual(0, mocked_process_item.call_count,
                         'The mocked_process_item() method should not have been called')

    def add_service_item_with_song_edit_test(self):
        """
        Test the add_service_item() method when song_edit is True
        """
        # GIVEN: A slide controller and a new item to add
        mocked_item = MagicMock()
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller._process_item = mocked_process_item
        slide_controller.song_edit = True
        slide_controller.selected_row = 2

        # WHEN: The item is added to the service
        slide_controller.add_service_item(mocked_item)

        # THEN: The item is processed, the slide number is correct, and the song is not editable (or something)
        mocked_item.render.assert_called_once_with()
        self.assertFalse(slide_controller.song_edit, 'song_edit should be False')
        mocked_process_item.assert_called_once_with(mocked_item, 2)

    def add_service_item_without_song_edit_test(self):
        """
        Test the add_service_item() method when song_edit is False
        """
        # GIVEN: A slide controller and a new item to add
        mocked_item = MagicMock()
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller._process_item = mocked_process_item
        slide_controller.song_edit = False
        slide_controller.selected_row = 2

        # WHEN: The item is added to the service
        slide_controller.add_service_item(mocked_item)

        # THEN: The item is processed, the slide number is correct, and the song is not editable (or something)
        mocked_item.render.assert_called_once_with()
        self.assertFalse(slide_controller.song_edit, 'song_edit should be False')
        mocked_process_item.assert_called_once_with(mocked_item, 0)

    def replace_service_manager_item_different_items_test(self):
        """
        Test that when the service items are not the same, nothing happens
        """
        # GIVEN: A slide controller and a new item to add
        mocked_item = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller._process_item = mocked_process_item
        slide_controller.service_item = None

        # WHEN: The service item is replaced
        slide_controller.replace_service_manager_item(mocked_item)

        # THEN: The service item should not be processed
        self.assertEqual(0, mocked_process_item.call_count, 'The _process_item() method should not have been called')
        self.assertEqual(0, mocked_preview_widget.current_slide_number.call_count,
                         'The preview_widgetcurrent_slide_number.() method should not have been called')

    def replace_service_manager_item_same_item_test(self):
        """
        Test that when the service item is the same, the service item is reprocessed
        """
        # GIVEN: A slide controller and a new item to add
        mocked_item = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_preview_widget.current_slide_number.return_value = 7
        mocked_process_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller._process_item = mocked_process_item
        slide_controller.service_item = mocked_item

        # WHEN: The service item is replaced
        slide_controller.replace_service_manager_item(mocked_item)

        # THEN: The service item should not be processed
        mocked_preview_widget.current_slide_number.assert_called_with()
        mocked_process_item.assert_called_once_with(mocked_item, 7)

    def on_slide_blank_test(self):
        """
        Test on_slide_blank
        """
        # GIVEN: An instance of SlideController and a mocked on_blank_display
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = MagicMock()

        # WHEN: Calling on_slide_blank
        slide_controller.on_slide_blank()

        # THEN: on_blank_display should have been called with True
        slide_controller.on_blank_display.assert_called_once_with(True)

    def on_slide_unblank_test(self):
        """
        Test on_slide_unblank
        """
        # GIVEN: An instance of SlideController and a mocked on_blank_display
        slide_controller = SlideController(None)
        slide_controller.on_blank_display = MagicMock()

        # WHEN: Calling on_slide_unblank
        slide_controller.on_slide_unblank()

        # THEN: on_blank_display should have been called with False
        slide_controller.on_blank_display.assert_called_once_with(False)

    def on_slide_selected_index_no_service_item_test(self):
        """
        Test that when there is no service item, the on_slide_selected_index() method returns immediately
        """
        # GIVEN: A mocked service item and a slide controller without a service item
        mocked_item = MagicMock()
        slide_controller = SlideController(None)
        slide_controller.service_item = None

        # WHEN: The method is called
        slide_controller.on_slide_selected_index([10])

        # THEN: It should have exited early
        self.assertEqual(0, mocked_item.is_command.call_count, 'The service item should have not been called')

    @patch.object(Registry, 'execute')
    def on_slide_selected_index_service_item_command_test(self, mocked_execute):
        """
        Test that when there is a command service item, the command is executed
        """
        # GIVEN: A mocked service item and a slide controller with a service item
        mocked_item = MagicMock()
        mocked_item.is_command.return_value = True
        mocked_item.name = 'Mocked Item'
        mocked_update_preview = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_slide_selected = MagicMock()
        Registry.create()
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_item
        slide_controller.update_preview = mocked_update_preview
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller.slide_selected = mocked_slide_selected
        slide_controller.is_live = True

        # WHEN: The method is called
        slide_controller.on_slide_selected_index([9])

        # THEN: It should have sent a notification
        mocked_item.is_command.assert_called_once_with()
        mocked_execute.assert_called_once_with('mocked item_slide', [mocked_item, True, 9])
        mocked_update_preview.assert_called_once_with()
        self.assertEqual(0, mocked_preview_widget.change_slide.call_count, 'Change slide should not have been called')
        self.assertEqual(0, mocked_slide_selected.call_count, 'slide_selected should not have been called')

    @patch.object(Registry, 'execute')
    def on_slide_selected_index_service_item_not_command_test(self, mocked_execute):
        """
        Test that when there is a service item but it's not a command, the preview widget is updated
        """
        # GIVEN: A mocked service item and a slide controller with a service item
        mocked_item = MagicMock()
        mocked_item.is_command.return_value = False
        mocked_item.name = 'Mocked Item'
        mocked_update_preview = MagicMock()
        mocked_preview_widget = MagicMock()
        mocked_slide_selected = MagicMock()
        Registry.create()
        slide_controller = SlideController(None)
        slide_controller.service_item = mocked_item
        slide_controller.update_preview = mocked_update_preview
        slide_controller.preview_widget = mocked_preview_widget
        slide_controller.slide_selected = mocked_slide_selected

        # WHEN: The method is called
        slide_controller.on_slide_selected_index([7])

        # THEN: It should have sent a notification
        mocked_item.is_command.assert_called_once_with()
        self.assertEqual(0, mocked_execute.call_count, 'Execute should not have been called')
        self.assertEqual(0, mocked_update_preview.call_count, 'Update preview should not have been called')
        mocked_preview_widget.change_slide.assert_called_once_with(7)
        mocked_slide_selected.assert_called_once_with()


class TestInfoLabel(TestCase):

    def paint_event_text_fits_test(self):
        """
        Test the paintEvent method when text fits the label
        """
        font = QtGui.QFont()
        metrics = QtGui.QFontMetrics(font)

        with patch('openlp.core.ui.slidecontroller.QtGui.QLabel'), \
                patch('openlp.core.ui.slidecontroller.QtGui.QPainter') as mocked_qpainter:

            # GIVEN: An instance of InfoLabel, with mocked text return, width and rect methods
            info_label = InfoLabel()
            test_string = 'Label Text'
            mocked_rect = MagicMock()
            mocked_text = MagicMock()
            mocked_width = MagicMock()
            mocked_text.return_value = test_string
            info_label.rect = mocked_rect
            info_label.text = mocked_text
            info_label.width = mocked_width

            # WHEN: The instance is wider than its text, and the paintEvent method is called
            info_label.width.return_value = metrics.boundingRect(test_string).width() + 10
            info_label.paintEvent(MagicMock())

            # THEN: The text should be drawn centered with the complete test_string
            mocked_qpainter().drawText.assert_called_once_with(mocked_rect(), QtCore.Qt.AlignCenter, test_string)

    def paint_event_text_doesnt_fit_test(self):
        """
        Test the paintEvent method when text fits the label
        """
        font = QtGui.QFont()
        metrics = QtGui.QFontMetrics(font)

        with patch('openlp.core.ui.slidecontroller.QtGui.QLabel'), \
                patch('openlp.core.ui.slidecontroller.QtGui.QPainter') as mocked_qpainter:

            # GIVEN: An instance of InfoLabel, with mocked text return, width and rect methods
            info_label = InfoLabel()
            test_string = 'Label Text'
            mocked_rect = MagicMock()
            mocked_text = MagicMock()
            mocked_width = MagicMock()
            mocked_text.return_value = test_string
            info_label.rect = mocked_rect
            info_label.text = mocked_text
            info_label.width = mocked_width

            # WHEN: The instance is narrower than its text, and the paintEvent method is called
            label_width = metrics.boundingRect(test_string).width() - 10
            info_label.width.return_value = label_width
            info_label.paintEvent(MagicMock())

            # THEN: The text should be drawn aligned left with an elided test_string
            elided_test_string = metrics.elidedText(test_string, QtCore.Qt.ElideRight, label_width)
            mocked_qpainter().drawText.assert_called_once_with(mocked_rect(), QtCore.Qt.AlignLeft, elided_test_string)

    @patch('builtins.super')
    def set_text_test(self, mocked_super):
        """
        Test the reimplemented setText method
        """
        # GIVEN: An instance of InfoLabel and mocked setToolTip method
        info_label = InfoLabel()
        set_tool_tip_mock = MagicMock()
        info_label.setToolTip = set_tool_tip_mock

        # WHEN: Calling the instance method setText
        info_label.setText('Label Text')

        # THEN: The setToolTip and super class setText methods should have been called with the same text
        set_tool_tip_mock.assert_called_once_with('Label Text')
        mocked_super().setText.assert_called_once_with('Label Text')


class TestLiveController(TestCase):

    def initial_live_controller_test(self):
        """
        Test the initial live slide controller state .
        """
        # GIVEN: A new SlideController instance.
        Registry.create()
        live_controller = LiveController(None)

        # WHEN: the default controller is built.
        # THEN: The controller should not be a live controller.
        self.assertEqual(live_controller.is_live, True, 'The slide controller should be a live controller')


class TestPreviewLiveController(TestCase):

    def initial_preview_controller_test(self):
        """
        Test the initial preview slide controller state.
        """
        # GIVEN: A new SlideController instance.
        Registry.create()
        preview_controller = PreviewController(None)

        # WHEN: the default controller is built.
        # THEN: The controller should not be a live controller.
        self.assertEqual(preview_controller.is_live, False, 'The slide controller should be a Preview controller')
