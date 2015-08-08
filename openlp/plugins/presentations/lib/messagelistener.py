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

import logging
import copy
import os

from PyQt4 import QtCore

from openlp.core.common import Registry
from openlp.core.ui import HideMode
from openlp.core.lib import ServiceItemContext, ServiceItem
from openlp.plugins.presentations.lib.pdfcontroller import PDF_CONTROLLER_FILETYPES

log = logging.getLogger(__name__)


class Controller(object):
    """
    This is the Presentation listener who acts on events from the slide controller and passes the messages on the the
    correct presentation handlers.
    """
    log.info('Controller loaded')

    def __init__(self, live):
        """
        Constructor
        """
        self.is_live = live
        self.doc = None
        self.hide_mode = None
        log.info('%s controller loaded' % live)

    def add_handler(self, controller, file, hide_mode, slide_no):
        """
        Add a handler, which is an instance of a presentation and slidecontroller combination. If the slidecontroller
        has a display then load the presentation.
        """
        log.debug('Live = %s, add_handler %s' % (self.is_live, file))
        self.controller = controller
        if self.doc is not None:
            self.shutdown()
        self.doc = self.controller.add_document(file)
        if not self.doc.load_presentation():
            # Display error message to user
            # Inform slidecontroller that the action failed?
            return
        self.doc.slidenumber = slide_no
        self.hide_mode = hide_mode
        log.debug('add_handler, slide_number: %d' % slide_no)
        if self.is_live:
            if hide_mode == HideMode.Screen:
                Registry().execute('live_display_hide', HideMode.Screen)
                self.stop()
            elif hide_mode == HideMode.Theme:
                self.blank(hide_mode)
            elif hide_mode == HideMode.Blank:
                self.blank(hide_mode)
            else:
                self.doc.start_presentation()
                Registry().execute('live_display_hide', HideMode.Screen)
                self.doc.slidenumber = 1
                if slide_no > 1:
                    self.slide(slide_no)

    def activate(self):
        """
        Active the presentation, and show it on the screen. Use the last slide number.
        """
        log.debug('Live = %s, activate' % self.is_live)
        if not self.doc:
            return False
        if self.doc.is_active():
            return True
        if not self.doc.is_loaded():
            if not self.doc.load_presentation():
                log.warning('Failed to activate %s' % self.doc.file_path)
                return False
        if self.is_live:
            self.doc.start_presentation()
            if self.doc.slidenumber > 1:
                if self.doc.slidenumber > self.doc.get_slide_count():
                    self.doc.slidenumber = self.doc.get_slide_count()
                self.doc.goto_slide(self.doc.slidenumber)
        if self.doc.is_active():
            return True
        else:
            log.warning('Failed to activate %s' % self.doc.file_path)
            return False

    def slide(self, slide):
        """
        Go to a specific slide
        """
        log.debug('Live = %s, slide' % self.is_live)
        if not self.doc:
            return
        if not self.is_live:
            return
        if self.hide_mode:
            self.doc.slidenumber = int(slide) + 1
            self.poll()
            return
        if not self.activate():
            return
        self.doc.goto_slide(int(slide) + 1)
        self.poll()

    def first(self):
        """
        Based on the handler passed at startup triggers the first slide.
        """
        log.debug('Live = %s, first' % self.is_live)
        if not self.doc:
            return
        if not self.is_live:
            return
        if self.hide_mode:
            self.doc.slidenumber = 1
            self.poll()
            return
        if not self.activate():
            return
        self.doc.start_presentation()
        self.poll()

    def last(self):
        """
        Based on the handler passed at startup triggers the last slide.
        """
        log.debug('Live = %s, last' % self.is_live)
        if not self.doc:
            return
        if not self.is_live:
            return
        if self.hide_mode:
            self.doc.slidenumber = self.doc.get_slide_count()
            self.poll()
            return
        if not self.activate():
            return
        self.doc.goto_slide(self.doc.get_slide_count())
        self.poll()

    def next(self):
        """
        Based on the handler passed at startup triggers the next slide event.
        """
        log.debug('Live = %s, next' % self.is_live)
        if not self.doc:
            return
        if not self.is_live:
            return
        if self.hide_mode:
            if not self.doc.is_active():
                return
            if self.doc.slidenumber < self.doc.get_slide_count():
                self.doc.slidenumber += 1
                self.poll()
            return
        if not self.activate():
            return
        # The "End of slideshow" screen is after the last slide. Note, we can't just stop on the last slide, since it
        # may contain animations that need to be stepped through.
        if self.doc.slidenumber > self.doc.get_slide_count():
            return
        self.doc.next_step()
        self.poll()

    def previous(self):
        """
        Based on the handler passed at startup triggers the previous slide event.
        """
        log.debug('Live = %s, previous' % self.is_live)
        if not self.doc:
            return
        if not self.is_live:
            return
        if self.hide_mode:
            if not self.doc.is_active():
                return
            if self.doc.slidenumber > 1:
                self.doc.slidenumber -= 1
                self.poll()
            return
        if not self.activate():
            return
        self.doc.previous_step()
        self.poll()

    def shutdown(self):
        """
        Based on the handler passed at startup triggers slide show to shut down.
        """
        log.debug('Live = %s, shutdown' % self.is_live)
        if not self.doc:
            return
        self.doc.close_presentation()
        self.doc = None

    def blank(self, hide_mode):
        """
        Instruct the controller to blank the presentation.
        """
        log.debug('Live = %s, blank' % self.is_live)
        self.hide_mode = hide_mode
        if not self.doc:
            return
        if not self.is_live:
            return
        if hide_mode == HideMode.Theme:
            if not self.doc.is_loaded():
                return
            if not self.doc.is_active():
                return
            Registry().execute('live_display_hide', HideMode.Theme)
        elif hide_mode == HideMode.Blank:
            if not self.activate():
                return
            self.doc.blank_screen()

    def stop(self):
        """
        Instruct the controller to stop and hide the presentation.
        """
        log.debug('Live = %s, stop' % self.is_live)
        # The document has not been loaded yet, so don't do anything. This can happen when going live with a
        # presentation while blanked to desktop.
        if not self.doc:
            return
        # Save the current slide number to be able to return to this slide if the presentation is activated again.
        if self.doc.is_active():
            self.doc.slidenumber = self.doc.get_slide_number()
        self.hide_mode = HideMode.Screen
        if not self.doc:
            return
        if not self.is_live:
            return
        if not self.doc.is_loaded():
            return
        if not self.doc.is_active():
            return
        self.doc.stop_presentation()

    def unblank(self):
        """
        Instruct the controller to unblank the presentation.
        """
        log.debug('Live = %s, unblank' % self.is_live)
        self.hide_mode = None
        if not self.doc:
            return
        if not self.is_live:
            return
        if not self.activate():
            return
        self.doc.unblank_screen()
        Registry().execute('live_display_hide', HideMode.Screen)

    def poll(self):
        if not self.doc:
            return
        self.doc.poll_slidenumber(self.is_live, self.hide_mode)


class MessageListener(object):
    """
    This is the Presentation listener who acts on events from the slide controller and passes the messages on the
    correct presentation handlers
    """
    log.info('Message Listener loaded')

    def __init__(self, media_item):
        self.controllers = media_item.controllers
        self.media_item = media_item
        self.preview_handler = Controller(False)
        self.live_handler = Controller(True)
        # messages are sent from core.ui.slidecontroller
        Registry().register_function('presentations_start', self.startup)
        Registry().register_function('presentations_stop', self.shutdown)
        Registry().register_function('presentations_hide', self.hide)
        Registry().register_function('presentations_first', self.first)
        Registry().register_function('presentations_previous', self.previous)
        Registry().register_function('presentations_next', self.next)
        Registry().register_function('presentations_last', self.last)
        Registry().register_function('presentations_slide', self.slide)
        Registry().register_function('presentations_blank', self.blank)
        Registry().register_function('presentations_unblank', self.unblank)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.timeout)

    def startup(self, message):
        """
        Start of new presentation. Save the handler as any new presentations start here
        """
        log.debug('Startup called with message %s' % message)
        is_live = message[1]
        item = message[0]
        hide_mode = message[2]
        file = item.get_frame_path()
        self.handler = item.processor
        # When starting presentation from the servicemanager we convert
        # PDF/XPS/OXPS-serviceitems into image-serviceitems. When started from the mediamanager
        # the conversion has already been done at this point.
        file_type = os.path.splitext(file.lower())[1][1:]
        if file_type in PDF_CONTROLLER_FILETYPES:
            log.debug('Converting from pdf/xps/oxps to images for serviceitem with file %s', file)
            # Create a copy of the original item, and then clear the original item so it can be filled with images
            item_cpy = copy.copy(item)
            item.__init__(None)
            if is_live:
                self.media_item.generate_slide_data(item, item_cpy, False, False, ServiceItemContext.Live, file)
            else:
                self.media_item.generate_slide_data(item, item_cpy, False, False, ServiceItemContext.Preview, file)
            # Some of the original serviceitem attributes is needed in the new serviceitem
            item.footer = item_cpy.footer
            item.from_service = item_cpy.from_service
            item.iconic_representation = item_cpy.iconic_representation
            item.image_border = item_cpy.image_border
            item.main = item_cpy.main
            item.theme_data = item_cpy.theme_data
            # When presenting PDF/XPS/OXPS, we are using the image presentation code,
            # so handler & processor is set to None, and we skip adding the handler.
            self.handler = None
        if self.handler == self.media_item.automatic:
            self.handler = self.media_item.find_controller_by_type(file)
            if not self.handler:
                return
        if is_live:
            controller = self.live_handler
        else:
            controller = self.preview_handler
        # When presenting PDF/XPS/OXPS, we are using the image presentation code,
        # so handler & processor is set to None, and we skip adding the handler.
        if self.handler is None:
            self.controller = controller
        else:
            controller.add_handler(self.controllers[self.handler], file, hide_mode, message[3])
            self.timer.start()

    def slide(self, message):
        """
        React to the message to move to a specific slide.

        :param message: The message {1} is_live {2} slide
        """
        is_live = message[1]
        slide = message[2]
        if is_live:
            self.live_handler.slide(slide)
        else:
            self.preview_handler.slide(slide)

    def first(self, message):
        """
        React to the message to move to the first slide.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.first()
        else:
            self.preview_handler.first()

    def last(self, message):
        """
        React to the message to move to the last slide.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.last()
        else:
            self.preview_handler.last()

    def next(self, message):
        """
        React to the message to move to the next animation/slide.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.next()
        else:
            self.preview_handler.next()

    def previous(self, message):
        """
        React to the message to move to the previous animation/slide.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.previous()
        else:
            self.preview_handler.previous()

    def shutdown(self, message):
        """
        React to message to shutdown the presentation. I.e. end the show and close the file.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.shutdown()
            self.timer.stop()
        else:
            self.preview_handler.shutdown()

    def hide(self, message):
        """
        React to the message to show the desktop.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.stop()

    def blank(self, message):
        """
        React to the message to blank the display.

        :param message: The message {1} is_live {2} slide
        """
        is_live = message[1]
        hide_mode = message[2]
        if is_live:
            self.live_handler.blank(hide_mode)

    def unblank(self, message):
        """
        React to the message to unblank the display.

        :param message: The message {1} is_live
        """
        is_live = message[1]
        if is_live:
            self.live_handler.unblank()

    def timeout(self):
        """
        The presentation may be timed or might be controlled by the application directly, rather than through OpenLP.
        Poll occasionally to check which slide is currently displayed so the slidecontroller view can be updated.
        """
        self.live_handler.poll()
