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
This module is for controlling powerpoint. PPT API documentation:
`http://msdn.microsoft.com/en-us/library/aa269321(office.10).aspx`_
2010: https://msdn.microsoft.com/en-us/library/office/ff743835%28v=office.14%29.aspx
2013: https://msdn.microsoft.com/en-us/library/office/ff743835.aspx
"""
import os
import logging
import time

from openlp.core.common import is_win, Settings

if is_win():
    from win32com.client import Dispatch
    import win32con
    import winreg
    import win32ui
    import win32gui
    import pywintypes


from openlp.core.lib import ScreenList
from openlp.core.lib.ui import UiStrings, critical_error_message_box, translate
from openlp.core.common import trace_error_handler, Registry
from .presentationcontroller import PresentationController, PresentationDocument

log = logging.getLogger(__name__)


class PowerpointController(PresentationController):
    """
    Class to control interactions with PowerPoint Presentations. It creates the runtime Environment , Loads the and
    Closes the Presentation. As well as triggering the correct activities based on the users input.
    """
    log.info('PowerpointController loaded')

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        super(PowerpointController, self).__init__(plugin, 'Powerpoint', PowerpointDocument)
        self.supports = ['ppt', 'pps', 'pptx', 'ppsx', 'pptm']
        self.process = None

    def check_available(self):
        """
        PowerPoint is able to run on this machine.
        """
        log.debug('check_available')
        if is_win():
            try:
                winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'PowerPoint.Application').Close()
                try:
                    # Try to detect if the version is 12 (2007) or above, and if so add 'odp' as a support filetype
                    version_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'PowerPoint.Application\\CurVer')
                    tmp1, app_version_string, tmp2 = winreg.EnumValue(version_key, 0)
                    version_key.Close()
                    app_version = int(app_version_string[-2:])
                    if app_version >= 12:
                        self.also_supports = ['odp']
                except (OSError, ValueError):
                    log.warning('Detection of powerpoint version using registry failed.')
                return True
            except OSError:
                pass
        return False

    if is_win():
        def start_process(self):
            """
            Loads PowerPoint process.
            """
            log.debug('start_process')
            if not self.process:
                self.process = Dispatch('PowerPoint.Application')

        def kill(self):
            """
            Called at system exit to clean up any running presentations.
            """
            log.debug('Kill powerpoint')
            while self.docs:
                self.docs[0].close_presentation()
            if self.process is None:
                return
            try:
                if self.process.Presentations.Count > 0:
                    return
                self.process.Quit()
            except (AttributeError, pywintypes.com_error) as e:
                log.exception('Exception caught while killing powerpoint process')
                log.exception(e)
                trace_error_handler(log)
            self.process = None


class PowerpointDocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation.
    """

    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise.

        :param controller:
        :param presentation:
        """
        log.debug('Init Presentation Powerpoint')
        super(PowerpointDocument, self).__init__(controller, presentation)
        self.presentation = None
        self.index_map = {}
        self.slide_count = 0
        self.blank_slide = 1
        self.blank_click = None
        self.presentation_hwnd = None

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. Opens the PowerPoint file using the process created
        earlier.
        """
        log.debug('load_presentation')
        try:
            if not self.controller.process:
                self.controller.start_process()
            self.controller.process.Presentations.Open(os.path.normpath(self.file_path), False, False, False)
            self.presentation = self.controller.process.Presentations(self.controller.process.Presentations.Count)
            self.create_thumbnails()
            self.create_titles_and_notes()
            # Make sure powerpoint doesn't steal focus, unless we're on a single screen setup
            if len(ScreenList().screen_list) > 1:
                Registry().get('main_window').activateWindow()
            return True
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Exception caught while loading Powerpoint presentation')
            log.exception(e)
            trace_error_handler(log)
            return False

    def create_thumbnails(self):
        """
        Create the thumbnail images for the current presentation.

        Note an alternative and quicker method would be do::

            self.presentation.Slides[n].Copy()
            thumbnail = QApplication.clipboard.image()

        However, for the moment, we want a physical file since it makes life easier elsewhere.
        """
        log.debug('create_thumbnails')
        if self.check_thumbnails():
            return
        key = 1
        for num in range(self.presentation.Slides.Count):
            if not self.presentation.Slides(num + 1).SlideShowTransition.Hidden:
                self.index_map[key] = num + 1
                self.presentation.Slides(num + 1).Export(
                    os.path.join(self.get_thumbnail_folder(), 'slide%d.png' % (key)), 'png', 320, 240)
                key += 1
        self.slide_count = key - 1

    def close_presentation(self):
        """
        Close presentation and clean up objects. This is triggered by a new object being added to SlideController or
        OpenLP being shut down.
        """
        log.debug('ClosePresentation')
        if self.presentation:
            try:
                self.presentation.Close()
            except (AttributeError, pywintypes.com_error) as e:
                log.exception('Caught exception while closing powerpoint presentation')
                log.exception(e)
                trace_error_handler(log)
        self.presentation = None
        self.controller.remove_doc(self)
        # Make sure powerpoint doesn't steal focus, unless we're on a single screen setup
        if len(ScreenList().screen_list) > 1:
            Registry().get('main_window').activateWindow()

    def is_loaded(self):
        """
        Returns ``True`` if a presentation is loaded.
        """
        log.debug('is_loaded')
        try:
            if self.controller.process.Presentations.Count == 0:
                return False
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in is_loaded')
            log.exception(e)
            trace_error_handler(log)
            return False
        return True

    def is_active(self):
        """
        Returns ``True`` if a presentation is currently active.
        """
        log.debug('is_active')
        if not self.is_loaded():
            return False
        try:
            if self.presentation.SlideShowWindow is None:
                return False
            if self.presentation.SlideShowWindow.View is None:
                return False
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in is_active')
            log.exception(e)
            trace_error_handler(log)
            return False
        return True

    def unblank_screen(self):
        """
        Unblanks (restores) the presentation.
        """
        log.debug('unblank_screen')
        try:
            self.presentation.SlideShowWindow.Activate()
            self.presentation.SlideShowWindow.View.State = 1
            # Unblanking is broken in PowerPoint 2010 (14.0), need to redisplay
            if 15.0 > float(self.presentation.Application.Version) >= 14.0:
                self.presentation.SlideShowWindow.View.GotoSlide(self.index_map[self.blank_slide], False)
                if self.blank_click:
                    self.presentation.SlideShowWindow.View.GotoClick(self.blank_click)
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in unblank_screen')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()
        # Stop powerpoint from flashing in the taskbar
        if self.presentation_hwnd:
            win32gui.FlashWindowEx(self.presentation_hwnd, win32con.FLASHW_STOP, 0, 0)
        # Make sure powerpoint doesn't steal focus, unless we're on a single screen setup
        if len(ScreenList().screen_list) > 1:
            Registry().get('main_window').activateWindow()

    def blank_screen(self):
        """
        Blanks the screen.
        """
        log.debug('blank_screen')
        try:
            # Unblanking is broken in PowerPoint 2010 (14.0), need to save info for later
            if 15.0 > float(self.presentation.Application.Version) >= 14.0:
                self.blank_slide = self.get_slide_number()
                self.blank_click = self.presentation.SlideShowWindow.View.GetClickIndex()
            # ppSlideShowBlackScreen = 3
            self.presentation.SlideShowWindow.View.State = 3
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in blank_screen')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()

    def is_blank(self):
        """
        Returns ``True`` if screen is blank.
        """
        log.debug('is_blank')
        if self.is_active():
            try:
                # ppSlideShowBlackScreen = 3
                return self.presentation.SlideShowWindow.View.State == 3
            except (AttributeError, pywintypes.com_error) as e:
                log.exception('Caught exception while in is_blank')
                log.exception(e)
                trace_error_handler(log)
                self.show_error_msg()
        else:
            return False

    def stop_presentation(self):
        """
        Stops the current presentation and hides the output. Used when blanking to desktop.
        """
        log.debug('stop_presentation')
        try:
            self.presentation.SlideShowWindow.View.Exit()
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in stop_presentation')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()

    if is_win():
        def start_presentation(self):
            """
            Starts a presentation from the beginning.
            """
            log.debug('start_presentation')
            # SlideShowWindow measures its size/position by points, not pixels
            # https://technet.microsoft.com/en-us/library/dn528846.aspx
            try:
                dpi = win32ui.GetActiveWindow().GetDC().GetDeviceCaps(88)
            except win32ui.error:
                try:
                    dpi = win32ui.GetForegroundWindow().GetDC().GetDeviceCaps(88)
                except win32ui.error:
                    dpi = 96
            size = ScreenList().current['size']
            ppt_window = None
            try:
                ppt_window = self.presentation.SlideShowSettings.Run()
            except (AttributeError, pywintypes.com_error) as e:
                log.exception('Caught exception while in start_presentation')
                log.exception(e)
                trace_error_handler(log)
                self.show_error_msg()
            if ppt_window and not Settings().value('presentations/powerpoint control window'):
                try:
                    ppt_window.Top = size.y() * 72 / dpi
                    ppt_window.Height = size.height() * 72 / dpi
                    ppt_window.Left = size.x() * 72 / dpi
                    ppt_window.Width = size.width() * 72 / dpi
                except AttributeError as e:
                    log.exception('AttributeError while in start_presentation')
                    log.exception(e)
            # Find the presentation window and save the handle for later
            self.presentation_hwnd = None
            if ppt_window:
                log.debug('main display size:  y=%d, height=%d, x=%d, width=%d'
                          % (size.y(), size.height(), size.x(), size.width()))
                win32gui.EnumWindows(self._window_enum_callback, size)
            # Make sure powerpoint doesn't steal focus, unless we're on a single screen setup
            if len(ScreenList().screen_list) > 1:
                Registry().get('main_window').activateWindow()

    def _window_enum_callback(self, hwnd, size):
        """
        Method for callback from win32gui.EnumWindows.
        Used to find the powerpoint presentation window and stop it flashing in the taskbar.
        """
        # Get the size of the current window and if it matches the size of our main display we assume
        # it is the powerpoint presentation window.
        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
        window_title = win32gui.GetWindowText(hwnd)
        log.debug('window size:  left=%d, top=%d, right=%d, width=%d' % (left, top, right, bottom))
        log.debug('compare size:  %d and %d, %d and %d, %d and %d, %d and %d'
                  % (size.y(), top, size.height(), (bottom - top), size.x(), left, size.width(), (right - left)))
        log.debug('window title: %s' % window_title)
        filename_root, filename_ext = os.path.splitext(os.path.basename(self.file_path))
        if size.y() == top and size.height() == (bottom - top) and size.x() == left and \
                size.width() == (right - left) and filename_root in window_title:
            log.debug('Found a match and will save the handle')
            self.presentation_hwnd = hwnd
            # Stop powerpoint from flashing in the taskbar
            win32gui.FlashWindowEx(self.presentation_hwnd, win32con.FLASHW_STOP, 0, 0)

    def get_slide_number(self):
        """
        Returns the current slide number.
        """
        log.debug('get_slide_number')
        ret = 0
        try:
            # We need 2 approaches to getting the current slide number, because
            # SlideShowWindow.View.Slide.SlideIndex wont work on the end-slide where Slide isn't available, and
            # SlideShowWindow.View.CurrentShowPosition returns 0 when called when a transistion is executing (in 2013)
            # So we use SlideShowWindow.View.Slide.SlideIndex unless the state is done (ppSlideShowDone = 5)
            if self.presentation.SlideShowWindow.View.State != 5:
                ret = self.presentation.SlideShowWindow.View.Slide.SlideNumber
                # Do reverse lookup in the index_map to find the slide number to return
                ret = next((key for key, slidenum in self.index_map.items() if slidenum == ret), None)
            else:
                ret = self.presentation.SlideShowWindow.View.CurrentShowPosition
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in get_slide_number')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()
        return ret

    def get_slide_count(self):
        """
        Returns total number of slides.
        """
        log.debug('get_slide_count')
        return self.slide_count

    def goto_slide(self, slide_no):
        """
        Moves to a specific slide in the presentation.

        :param slide_no: The slide the text is required for, starting at 1
        """
        log.debug('goto_slide')
        try:
            if Settings().value('presentations/powerpoint slide click advance') \
                    and self.get_slide_number() == slide_no:
                click_index = self.presentation.SlideShowWindow.View.GetClickIndex()
                click_count = self.presentation.SlideShowWindow.View.GetClickCount()
                log.debug('We are already on this slide - go to next effect if any left, idx: %d, count: %d'
                          % (click_index, click_count))
                if click_index < click_count:
                    self.next_step()
            else:
                self.presentation.SlideShowWindow.View.GotoSlide(self.index_map[slide_no])
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in goto_slide')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation.
        """
        log.debug('next_step')
        try:
            self.presentation.SlideShowWindow.Activate()
            self.presentation.SlideShowWindow.View.Next()
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in next_step')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()
            return
        if self.get_slide_number() > self.get_slide_count():
            log.debug('past end, stepping back to previous')
            self.previous_step()
        # Stop powerpoint from flashing in the taskbar
        if self.presentation_hwnd:
            win32gui.FlashWindowEx(self.presentation_hwnd, win32con.FLASHW_STOP, 0, 0)
        # Make sure powerpoint doesn't steal focus, unless we're on a single screen setup
        if len(ScreenList().screen_list) > 1:
            Registry().get('main_window').activateWindow()

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation.
        """
        log.debug('previous_step')
        try:
            self.presentation.SlideShowWindow.View.Previous()
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Caught exception while in previous_step')
            log.exception(e)
            trace_error_handler(log)
            self.show_error_msg()

    def get_slide_text(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return _get_text_from_shapes(self.presentation.Slides(self.index_map[slide_no]).Shapes)

    def get_slide_notes(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return _get_text_from_shapes(self.presentation.Slides(self.index_map[slide_no]).NotesPage.Shapes)

    def create_titles_and_notes(self):
        """
        Writes the list of titles (one per slide)
        to 'titles.txt'
        and the notes to 'slideNotes[x].txt'
        in the thumbnails directory
        """
        titles = []
        notes = []
        for num in range(self.get_slide_count()):
            slide = self.presentation.Slides(self.index_map[num + 1])
            try:
                text = slide.Shapes.Title.TextFrame.TextRange.Text
            except Exception as e:
                log.exception(e)
                text = ''
            titles.append(text.replace('\n', ' ').replace('\x0b', ' ') + '\n')
            note = _get_text_from_shapes(slide.NotesPage.Shapes)
            if len(note) == 0:
                note = ' '
            notes.append(note)
        self.save_titles_and_notes(titles, notes)

    def show_error_msg(self):
        """
        Stop presentation and display an error message.
        """
        try:
            self.presentation.SlideShowWindow.View.Exit()
        except (AttributeError, pywintypes.com_error) as e:
            log.exception('Failed to exit Powerpoint presentation after error')
            log.exception(e)
        critical_error_message_box(UiStrings().Error, translate('PresentationPlugin.PowerpointDocument',
                                                                'An error occurred in the Powerpoint integration '
                                                                'and the presentation will be stopped. '
                                                                'Restart the presentation if you wish to present it.'))


def _get_text_from_shapes(shapes):
    """
    Returns any text extracted from the shapes on a presentation slide.

    :param shapes: A set of shapes to search for text.
    """
    text = ''
    try:
        for shape in shapes:
            if shape.PlaceholderFormat.Type == 2:  # 2 from is enum PpPlaceholderType.ppPlaceholderBody
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    text += shape.TextFrame.TextRange.Text + '\n'
    except pywintypes.com_error as e:
        log.warning('Failed to extract text from powerpoint slide')
        log.warning(e)
    return text
