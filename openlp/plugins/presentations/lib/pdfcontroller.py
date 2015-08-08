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

import os
import logging
from tempfile import NamedTemporaryFile
import re
from shutil import which
from subprocess import check_output, CalledProcessError, STDOUT

from openlp.core.utils import AppLocation
from openlp.core.common import Settings, is_win, trace_error_handler
from openlp.core.lib import ScreenList
from .presentationcontroller import PresentationController, PresentationDocument

if is_win():
    from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW

log = logging.getLogger(__name__)

PDF_CONTROLLER_FILETYPES = ['pdf', 'xps', 'oxps']


class PdfController(PresentationController):
    """
    Class to control PDF presentations
    """
    log.info('PdfController loaded')

    def __init__(self, plugin):
        """
        Initialise the class

        :param plugin: The plugin that creates the controller.
        """
        log.debug('Initialising')
        super(PdfController, self).__init__(plugin, 'Pdf', PdfDocument)
        self.process = None
        self.supports = ['pdf']
        self.also_supports = []
        # Determine whether mudraw or ghostscript is used
        self.check_installed()

    @staticmethod
    def check_binary(program_path):
        """
        Function that checks whether a binary is either ghostscript or mudraw or neither.
        Is also used from presentationtab.py

        :param program_path:The full path to the binary to check.
        :return: Type of the binary, 'gs' if ghostscript, 'mudraw' if mudraw, None if invalid.
        """
        program_type = None
        runlog = ''
        log.debug('testing program_path: %s', program_path)
        try:
            # Setup startupinfo options for check_output to avoid console popping up on windows
            if is_win():
                startupinfo = STARTUPINFO()
                startupinfo.dwFlags |= STARTF_USESHOWWINDOW
            else:
                startupinfo = None
            runlog = check_output([program_path, '--help'], stderr=STDOUT, startupinfo=startupinfo)
        except CalledProcessError as e:
            runlog = e.output
        except Exception:
            trace_error_handler(log)
            runlog = ''
        log.debug('check_output returned: %s' % runlog)
        # Analyse the output to see it the program is mudraw, ghostscript or neither
        for line in runlog.splitlines():
            decoded_line = line.decode()
            found_mudraw = re.search('usage: mudraw.*', decoded_line, re.IGNORECASE)
            if found_mudraw:
                program_type = 'mudraw'
                break
            found_gs = re.search('GPL Ghostscript.*', decoded_line, re.IGNORECASE)
            if found_gs:
                program_type = 'gs'
                break
        log.debug('in check_binary, found: %s', program_type)
        return program_type

    def check_available(self):
        """
        PdfController is able to run on this machine.

        :return: True if program to open PDF-files was found, otherwise False.
        """
        log.debug('check_available Pdf')
        return self.check_installed()

    def check_installed(self):
        """
        Check the viewer is installed.

        :return: True if program to open PDF-files was found, otherwise False.
        """
        log.debug('check_installed Pdf')
        self.mudrawbin = ''
        self.gsbin = ''
        self.also_supports = []
        # Use the user defined program if given
        if Settings().value('presentations/enable_pdf_program'):
            pdf_program = Settings().value('presentations/pdf_program')
            program_type = self.check_binary(pdf_program)
            if program_type == 'gs':
                self.gsbin = pdf_program
            elif program_type == 'mudraw':
                self.mudrawbin = pdf_program
        else:
            # Fallback to autodetection
            application_path = AppLocation.get_directory(AppLocation.AppDir)
            if is_win():
                # for windows we only accept mudraw.exe in the base folder
                application_path = AppLocation.get_directory(AppLocation.AppDir)
                if os.path.isfile(os.path.join(application_path, 'mudraw.exe')):
                    self.mudrawbin = os.path.join(application_path, 'mudraw.exe')
            else:
                DEVNULL = open(os.devnull, 'wb')
                # First try to find mupdf
                self.mudrawbin = which('mudraw')
                # if mupdf isn't installed, fallback to ghostscript
                if not self.mudrawbin:
                    self.gsbin = which('gs')
                # Last option: check if mudraw is placed in OpenLP base folder
                if not self.mudrawbin and not self.gsbin:
                    application_path = AppLocation.get_directory(AppLocation.AppDir)
                    if os.path.isfile(os.path.join(application_path, 'mudraw')):
                        self.mudrawbin = os.path.join(application_path, 'mudraw')
        if self.mudrawbin:
            self.also_supports = ['xps', 'oxps']
            return True
        elif self.gsbin:
            return True
        else:
            return False

    def kill(self):
        """
        Called at system exit to clean up any running presentations
        """
        log.debug('Kill pdfviewer')
        while self.docs:
            self.docs[0].close_presentation()


class PdfDocument(PresentationDocument):
    """
    Class which holds information of a single presentation.
    This class is not actually used to present the PDF, instead we convert to
    image-serviceitem on the fly and present as such. Therefore some of the 'playback'
    functions is not implemented.
    """
    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise.
        """
        log.debug('Init Presentation Pdf')
        PresentationDocument.__init__(self, controller, presentation)
        self.presentation = None
        self.blanked = False
        self.hidden = False
        self.image_files = []
        self.num_pages = -1
        # Setup startupinfo options for check_output to avoid console popping up on windows
        if is_win():
            self.startupinfo = STARTUPINFO()
            self.startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        else:
            self.startupinfo = None

    def gs_get_resolution(self, size):
        """
        Only used when using ghostscript
        Ghostscript can't scale automatically while keeping aspect like mupdf, so we need
        to get the ratio between the screen size and the PDF to scale

        :param size: Size struct containing the screen size.
        :return: The resolution dpi to be used.
        """
        # Use a postscript script to get size of the pdf. It is assumed that all pages have same size
        gs_resolution_script = AppLocation.get_directory(
            AppLocation.PluginsDir) + '/presentations/lib/ghostscript_get_resolution.ps'
        # Run the script on the pdf to get the size
        runlog = []
        try:
            runlog = check_output([self.controller.gsbin, '-dNOPAUSE', '-dNODISPLAY', '-dBATCH',
                                   '-sFile=' + self.file_path, gs_resolution_script],
                                  startupinfo=self.startupinfo)
        except CalledProcessError as e:
            log.debug(' '.join(e.cmd))
            log.debug(e.output)
        # Extract the pdf resolution from output, the format is " Size: x: <width>, y: <height>"
        width = 0.0
        height = 0.0
        for line in runlog.splitlines():
            try:
                width = float(re.search('.*Size: x: (\d+\.?\d*), y: \d+.*', line.decode()).group(1))
                height = float(re.search('.*Size: x: \d+\.?\d*, y: (\d+\.?\d*).*', line.decode()).group(1))
                break
            except AttributeError:
                continue
        # Calculate the ratio from pdf to screen
        if width > 0 and height > 0:
            width_ratio = size.width() / width
            height_ratio = size.height() / height
            # return the resolution that should be used. 72 is default.
            if width_ratio > height_ratio:
                return int(height_ratio * 72)
            else:
                return int(width_ratio * 72)
        else:
            return 72

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. It generates images from the PDF.

        :return: True is loading succeeded, otherwise False.
        """
        log.debug('load_presentation pdf')
        # Check if the images has already been created, and if yes load them
        if os.path.isfile(os.path.join(self.get_temp_folder(), 'mainslide001.png')):
            created_files = sorted(os.listdir(self.get_temp_folder()))
            for fn in created_files:
                if os.path.isfile(os.path.join(self.get_temp_folder(), fn)):
                    self.image_files.append(os.path.join(self.get_temp_folder(), fn))
            self.num_pages = len(self.image_files)
            return True
        size = ScreenList().current['size']
        # Generate images from PDF that will fit the frame.
        runlog = ''
        try:
            if not os.path.isdir(self.get_temp_folder()):
                os.makedirs(self.get_temp_folder())
            if self.controller.mudrawbin:
                runlog = check_output([self.controller.mudrawbin, '-w', str(size.width()), '-h', str(size.height()),
                                       '-o', os.path.join(self.get_temp_folder(), 'mainslide%03d.png'), self.file_path],
                                      startupinfo=self.startupinfo)
            elif self.controller.gsbin:
                resolution = self.gs_get_resolution(size)
                runlog = check_output([self.controller.gsbin, '-dSAFER', '-dNOPAUSE', '-dBATCH', '-sDEVICE=png16m',
                                       '-r' + str(resolution), '-dTextAlphaBits=4', '-dGraphicsAlphaBits=4',
                                       '-sOutputFile=' + os.path.join(self.get_temp_folder(), 'mainslide%03d.png'),
                                       self.file_path], startupinfo=self.startupinfo)
            created_files = sorted(os.listdir(self.get_temp_folder()))
            for fn in created_files:
                if os.path.isfile(os.path.join(self.get_temp_folder(), fn)):
                    self.image_files.append(os.path.join(self.get_temp_folder(), fn))
        except Exception as e:
            log.debug(e)
            log.debug(runlog)
            return False
        self.num_pages = len(self.image_files)
        # Create thumbnails
        self.create_thumbnails()
        return True

    def create_thumbnails(self):
        """
        Generates thumbnails
        """
        log.debug('create_thumbnails pdf')
        if self.check_thumbnails():
            return
        # use builtin function to create thumbnails from generated images
        index = 1
        for image in self.image_files:
            self.convert_thumbnail(image, index)
            index += 1

    def close_presentation(self):
        """
        Close presentation and clean up objects. Triggered by new object being added to SlideController or OpenLP being
        shut down.
        """
        log.debug('close_presentation pdf')
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns true if a presentation is loaded.

        :return: True if loaded, False if not.
        """
        log.debug('is_loaded pdf')
        if self.num_pages < 0:
            return False
        return True

    def is_active(self):
        """
        Returns true if a presentation is currently active.

        :return: True if active, False if not.
        """
        log.debug('is_active pdf')
        return self.is_loaded() and not self.hidden

    def get_slide_count(self):
        """
        Returns total number of slides

        :return: The number of pages in the presentation..
        """
        return self.num_pages
