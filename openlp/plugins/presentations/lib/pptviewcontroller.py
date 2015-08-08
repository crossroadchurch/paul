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
import os
import logging
import zipfile
import re
from xml.etree import ElementTree


from openlp.core.common import is_win

if is_win():
    from ctypes import cdll
    from ctypes.wintypes import RECT

from openlp.core.utils import AppLocation
from openlp.core.lib import ScreenList
from .presentationcontroller import PresentationController, PresentationDocument


log = logging.getLogger(__name__)


class PptviewController(PresentationController):
    """
    Class to control interactions with PowerPoint Viewer Presentations. It creates the runtime Environment , Loads the
    and Closes the Presentation. As well as triggering the correct activities based on the users input
    """
    log.info('PPTViewController loaded')

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        self.process = None
        super(PptviewController, self).__init__(plugin, 'Powerpoint Viewer', PptviewDocument)
        self.supports = ['ppt', 'pps', 'pptx', 'ppsx', 'pptm']

    def check_available(self):
        """
        PPT Viewer is able to run on this machine.
        """
        log.debug('check_available')
        if not is_win():
            return False
        return self.check_installed()

    if is_win():
        def check_installed(self):
            """
            Check the viewer is installed.
            """
            log.debug('Check installed')
            try:
                self.start_process()
                return self.process.CheckInstalled()
            except WindowsError:
                return False

        def start_process(self):
            """
            Loads the PPTVIEWLIB library.
            """
            if self.process:
                return
            log.debug('start PPTView')
            dll_path = os.path.join(AppLocation.get_directory(AppLocation.AppDir),
                                    'plugins', 'presentations', 'lib', 'pptviewlib', 'pptviewlib.dll')
            self.process = cdll.LoadLibrary(dll_path)
            if log.isEnabledFor(logging.DEBUG):
                self.process.SetDebug(1)

        def kill(self):
            """
            Called at system exit to clean up any running presentations
            """
            log.debug('Kill pptviewer')
            while self.docs:
                self.docs[0].close_presentation()


class PptviewDocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation.
    """
    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise.
        """
        log.debug('Init Presentation PowerPoint')
        super(PptviewDocument, self).__init__(controller, presentation)
        self.presentation = None
        self.ppt_id = None
        self.blanked = False
        self.hidden = False

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. It builds the environment, starts communication with
        the background PptView task started earlier.
        """
        log.debug('LoadPresentation')
        temp_folder = self.get_temp_folder()
        size = ScreenList().current['size']
        rect = RECT(size.x(), size.y(), size.right(), size.bottom())
        self.file_path = os.path.normpath(self.file_path)
        preview_path = os.path.join(temp_folder, 'slide')
        # Ensure that the paths are null terminated
        byte_file_path = self.file_path.encode('utf-16-le') + b'\0'
        preview_path = preview_path.encode('utf-16-le') + b'\0'
        if not os.path.isdir(temp_folder):
            os.makedirs(temp_folder)
        self.ppt_id = self.controller.process.OpenPPT(byte_file_path, None, rect, preview_path)
        if self.ppt_id >= 0:
            self.create_thumbnails()
            self.stop_presentation()
            return True
        else:
            return False

    def create_thumbnails(self):
        """
        PPTviewLib creates large BMP's, but we want small PNG's for consistency. Convert them here.
        """
        log.debug('create_thumbnails')
        if self.check_thumbnails():
            return
        log.debug('create_thumbnails proceeding')
        for idx in range(self.get_slide_count()):
            path = '%s\\slide%s.bmp' % (self.get_temp_folder(), str(idx + 1))
            self.convert_thumbnail(path, idx + 1)

    def create_titles_and_notes(self):
        """
        Extracts the titles and notes from the zipped file
        and writes the list of titles (one per slide)
        to 'titles.txt'
        and the notes to 'slideNotes[x].txt'
        in the thumbnails directory
        """
        titles = None
        notes = None
        filename = os.path.normpath(self.file_path)
        # let's make sure we have a valid zipped presentation
        if os.path.exists(filename) and zipfile.is_zipfile(filename):
            namespaces = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
                          "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
            # open the file
            with zipfile.ZipFile(filename) as zip_file:
                # find the presentation.xml to get the slide count
                with zip_file.open('ppt/presentation.xml') as pres:
                    tree = ElementTree.parse(pres)
                nodes = tree.getroot().findall(".//p:sldIdLst/p:sldId", namespaces=namespaces)
                # initialize the lists
                titles = ['' for i in range(len(nodes))]
                notes = ['' for i in range(len(nodes))]
                # loop thru the file list to find slides and notes
                for zip_info in zip_file.infolist():
                    node_type = ''
                    index = -1
                    list_to_add = None
                    # check if it is a slide
                    match = re.search("slides/slide(.+)\.xml", zip_info.filename)
                    if match:
                        index = int(match.group(1))-1
                        node_type = 'ctrTitle'
                        list_to_add = titles
                    # or a note
                    match = re.search("notesSlides/notesSlide(.+)\.xml", zip_info.filename)
                    if match:
                        index = int(match.group(1))-1
                        node_type = 'body'
                        list_to_add = notes
                    # if it is one of our files, index shouldn't be -1
                    if index >= 0:
                        with zip_file.open(zip_info) as zipped_file:
                            tree = ElementTree.parse(zipped_file)
                        text = ''
                        nodes = tree.getroot().findall(".//p:ph[@type='" + node_type + "']../../..//p:txBody//a:t",
                                                       namespaces=namespaces)
                        # if we found any content
                        if nodes and len(nodes) > 0:
                            for node in nodes:
                                if len(text) > 0:
                                    text += '\n'
                                text += node.text
                        # Let's remove the \n from the titles and
                        # just add one at the end
                        if node_type == 'ctrTitle':
                            text = text.replace('\n', ' ').replace('\x0b', ' ') + '\n'
                        list_to_add[index] = text
        # now let's write the files
        self.save_titles_and_notes(titles, notes)

    def close_presentation(self):
        """
        Close presentation and clean up objects. Triggered by new object being added to SlideController or OpenLP being
        shut down.
        """
        log.debug('ClosePresentation')
        if self.controller.process:
            self.controller.process.ClosePPT(self.ppt_id)
            self.ppt_id = -1
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns true if a presentation is loaded.
        """
        if self.ppt_id < 0:
            return False
        if self.get_slide_count() < 0:
            return False
        return True

    def is_active(self):
        """
        Returns true if a presentation is currently active.
        """
        return self.is_loaded() and not self.hidden

    def blank_screen(self):
        """
        Blanks the screen.
        """
        self.controller.process.Blank(self.ppt_id)
        self.blanked = True

    def unblank_screen(self):
        """
        Unblanks (restores) the presentation.
        """
        self.controller.process.Unblank(self.ppt_id)
        self.blanked = False

    def is_blank(self):
        """
        Returns true if screen is blank.
        """
        log.debug('is blank OpenOffice')
        return self.blanked

    def stop_presentation(self):
        """
        Stops the current presentation and hides the output.
        """
        self.hidden = True
        self.controller.process.Stop(self.ppt_id)

    def start_presentation(self):
        """
        Starts a presentation from the beginning.
        """
        if self.hidden:
            self.hidden = False
            self.controller.process.Resume(self.ppt_id)
        else:
            self.controller.process.RestartShow(self.ppt_id)

    def get_slide_number(self):
        """
        Returns the current slide number.
        """
        return self.controller.process.GetCurrentSlide(self.ppt_id)

    def get_slide_count(self):
        """
        Returns total number of slides.
        """
        return self.controller.process.GetSlideCount(self.ppt_id)

    def goto_slide(self, slide_no):
        """
        Moves to a specific slide in the presentation.

        :param slide_no: The slide the text is required for, starting at 1
        """
        self.controller.process.GotoSlide(self.ppt_id, slide_no)

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation.
        """
        self.controller.process.NextStep(self.ppt_id)

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation.
        """
        self.controller.process.PrevStep(self.ppt_id)
