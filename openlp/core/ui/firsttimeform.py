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
This module contains the first time wizard.
"""
import hashlib
import logging
import os
import socket
import time
import urllib.request
import urllib.parse
import urllib.error
from tempfile import gettempdir
from configparser import ConfigParser, MissingSectionHeaderError, NoSectionError, NoOptionError

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, AppLocation, Settings, check_directory_exists, \
    translate, clean_button_text, trace_error_handler
from openlp.core.lib import PluginStatus, build_icon
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.utils import get_web_page, CONNECTION_RETRIES, CONNECTION_TIMEOUT
from .firsttimewizard import UiFirstTimeWizard, FirstTimePage

log = logging.getLogger(__name__)


class ThemeScreenshotWorker(QtCore.QObject):
    """
    This thread downloads a theme's screenshot
    """
    screenshot_downloaded = QtCore.pyqtSignal(str, str, str)
    finished = QtCore.pyqtSignal()

    def __init__(self, themes_url, title, filename, sha256, screenshot):
        """
        Set up the worker object
        """
        self.was_download_cancelled = False
        self.themes_url = themes_url
        self.title = title
        self.filename = filename
        self.sha256 = sha256
        self.screenshot = screenshot
        socket.setdefaulttimeout(CONNECTION_TIMEOUT)
        super(ThemeScreenshotWorker, self).__init__()

    def run(self):
        """
        Overridden method to run the thread.
        """
        if self.was_download_cancelled:
            return
        try:
            urllib.request.urlretrieve('%s%s' % (self.themes_url, self.screenshot),
                                       os.path.join(gettempdir(), 'openlp', self.screenshot))
            # Signal that the screenshot has been downloaded
            self.screenshot_downloaded.emit(self.title, self.filename, self.sha256)
        except:
            log.exception('Unable to download screenshot')
        finally:
            self.finished.emit()

    @QtCore.pyqtSlot(bool)
    def set_download_canceled(self, toggle):
        """
        Externally set if the download was canceled

        :param toggle: Set if the download was canceled or not
        """
        self.was_download_cancelled = toggle


class FirstTimeForm(QtGui.QWizard, UiFirstTimeWizard, RegistryProperties):
    """
    This is the Theme Import Wizard, which allows easy creation and editing of OpenLP themes.
    """
    log.info('ThemeWizardForm loaded')

    def __init__(self, parent=None):
        """
        Create and set up the first time wizard.
        """
        super(FirstTimeForm, self).__init__(parent)
        self.web_access = True
        self.web = ''
        self.setup_ui(self)

    def get_next_page_id(self):
        """
        Returns the id of the next FirstTimePage to go to based on enabled plugins
        """
        if FirstTimePage.Welcome < self.currentId() < FirstTimePage.Songs and self.songs_check_box.isChecked():
            # If the songs plugin is enabled then go to the songs page
            return FirstTimePage.Songs
        elif FirstTimePage.Welcome < self.currentId() < FirstTimePage.Bibles and self.bible_check_box.isChecked():
            # Otherwise, if the Bibles plugin is enabled then go to the Bibles page
            return FirstTimePage.Bibles
        elif FirstTimePage.Welcome < self.currentId() < FirstTimePage.Themes:
            # Otherwise, if the current page is somewhere between the Welcome and the Themes pages, go to the themes
            return FirstTimePage.Themes
        else:
            # If all else fails, go to the next page
            return self.currentId() + 1

    def nextId(self):
        """
        Determine the next page in the Wizard to go to.
        """
        self.application.process_events()
        if self.currentId() == FirstTimePage.Download:
            if not self.web_access:
                return FirstTimePage.NoInternet
            else:
                return FirstTimePage.Plugins
        elif self.currentId() == FirstTimePage.Plugins:
            return self.get_next_page_id()
        elif self.currentId() == FirstTimePage.Progress:
            return -1
        elif self.currentId() == FirstTimePage.NoInternet:
            return FirstTimePage.Progress
        elif self.currentId() == FirstTimePage.Themes:
            self.application.set_busy_cursor()
            while not all([thread.isFinished() for thread in self.theme_screenshot_threads]):
                time.sleep(0.1)
                self.application.process_events()
            # Build the screenshot icons, as this can not be done in the thread.
            self._build_theme_screenshots()
            self.application.set_normal_cursor()
            return FirstTimePage.Defaults
        else:
            return self.get_next_page_id()

    def exec_(self):
        """
        Run the wizard.
        """
        self.set_defaults()
        return QtGui.QWizard.exec_(self)

    def initialize(self, screens):
        """
        Set up the First Time Wizard

        :param screens: The screens detected by OpenLP
        """
        self.screens = screens
        self.was_cancelled = False
        self.theme_screenshot_threads = []
        self.theme_screenshot_workers = []
        self.has_run_wizard = False

    def _download_index(self):
        """
        Download the configuration file and kick off the theme screenshot download threads
        """
        # check to see if we have web access
        self.web_access = False
        self.config = ConfigParser()
        user_agent = 'OpenLP/' + Registry().get('application').applicationVersion()
        self.application.process_events()
        try:
            web_config = get_web_page('%s%s' % (self.web, 'download.cfg'), header=('User-Agent', user_agent))
        except (urllib.error.URLError, ConnectionError) as err:
            msg = QtGui.QMessageBox()
            title = translate('OpenLP.FirstTimeWizard', 'Network Error')
            msg.setText('{} {}'.format(title, err.code if hasattr(err, 'code') else ''))
            msg.setInformativeText(translate('OpenLP.FirstTimeWizard',
                                             'There was a network error attempting to '
                                             'connect to retrieve initial configuration information'))
            msg.setStandardButtons(msg.Ok)
            ans = msg.exec_()
            web_config = False
        if web_config:
            files = web_config.read()
            try:
                self.config.read_string(files.decode())
                self.web = self.config.get('general', 'base url')
                self.songs_url = self.web + self.config.get('songs', 'directory') + '/'
                self.bibles_url = self.web + self.config.get('bibles', 'directory') + '/'
                self.themes_url = self.web + self.config.get('themes', 'directory') + '/'
                self.web_access = True
            except (NoSectionError, NoOptionError, MissingSectionHeaderError):
                log.debug('A problem occured while parsing the downloaded config file')
                trace_error_handler(log)
        self.update_screen_list_combo()
        self.application.process_events()
        self.downloading = translate('OpenLP.FirstTimeWizard', 'Downloading %s...')
        if self.has_run_wizard:
            self.songs_check_box.setChecked(self.plugin_manager.get_plugin_by_name('songs').is_active())
            self.bible_check_box.setChecked(self.plugin_manager.get_plugin_by_name('bibles').is_active())
            self.presentation_check_box.setChecked(self.plugin_manager.get_plugin_by_name('presentations').is_active())
            self.image_check_box.setChecked(self.plugin_manager.get_plugin_by_name('images').is_active())
            self.media_check_box.setChecked(self.plugin_manager.get_plugin_by_name('media').is_active())
            self.remote_check_box.setChecked(self.plugin_manager.get_plugin_by_name('remotes').is_active())
            self.custom_check_box.setChecked(self.plugin_manager.get_plugin_by_name('custom').is_active())
            self.song_usage_check_box.setChecked(self.plugin_manager.get_plugin_by_name('songusage').is_active())
            self.alert_check_box.setChecked(self.plugin_manager.get_plugin_by_name('alerts').is_active())
        self.application.set_normal_cursor()
        # Sort out internet access for downloads
        if self.web_access:
            songs = self.config.get('songs', 'languages')
            songs = songs.split(',')
            for song in songs:
                self.application.process_events()
                title = self.config.get('songs_%s' % song, 'title')
                filename = self.config.get('songs_%s' % song, 'filename')
                sha256 = self.config.get('songs_%s' % song, 'sha256', fallback='')
                item = QtGui.QListWidgetItem(title, self.songs_list_widget)
                item.setData(QtCore.Qt.UserRole, (filename, sha256))
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            bible_languages = self.config.get('bibles', 'languages')
            bible_languages = bible_languages.split(',')
            for lang in bible_languages:
                self.application.process_events()
                language = self.config.get('bibles_%s' % lang, 'title')
                lang_item = QtGui.QTreeWidgetItem(self.bibles_tree_widget, [language])
                bibles = self.config.get('bibles_%s' % lang, 'translations')
                bibles = bibles.split(',')
                for bible in bibles:
                    self.application.process_events()
                    title = self.config.get('bible_%s' % bible, 'title')
                    filename = self.config.get('bible_%s' % bible, 'filename')
                    sha256 = self.config.get('bible_%s' % bible, 'sha256', fallback='')
                    item = QtGui.QTreeWidgetItem(lang_item, [title])
                    item.setData(0, QtCore.Qt.UserRole, (filename, sha256))
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.bibles_tree_widget.expandAll()
            self.application.process_events()
            # Download the theme screenshots
            themes = self.config.get('themes', 'files').split(',')
            for theme in themes:
                title = self.config.get('theme_%s' % theme, 'title')
                filename = self.config.get('theme_%s' % theme, 'filename')
                sha256 = self.config.get('theme_%s' % theme, 'sha256', fallback='')
                screenshot = self.config.get('theme_%s' % theme, 'screenshot')
                worker = ThemeScreenshotWorker(self.themes_url, title, filename, sha256, screenshot)
                self.theme_screenshot_workers.append(worker)
                worker.screenshot_downloaded.connect(self.on_screenshot_downloaded)
                thread = QtCore.QThread(self)
                self.theme_screenshot_threads.append(thread)
                thread.started.connect(worker.run)
                worker.finished.connect(thread.quit)
                worker.moveToThread(thread)
                thread.start()
            self.application.process_events()

    def set_defaults(self):
        """
        Set up display at start of theme edit.
        """
        self.restart()
        self.web = 'http://openlp.org/files/frw/'
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.no_internet_finish_button.clicked.connect(self.on_no_internet_finish_button_clicked)
        self.no_internet_cancel_button.clicked.connect(self.on_no_internet_cancel_button_clicked)
        self.currentIdChanged.connect(self.on_current_id_changed)
        Registry().register_function('config_screen_changed', self.update_screen_list_combo)
        self.no_internet_finish_button.setVisible(False)
        self.no_internet_cancel_button.setVisible(False)
        # Check if this is a re-run of the wizard.
        self.has_run_wizard = Settings().value('core/has run wizard')
        check_directory_exists(os.path.join(gettempdir(), 'openlp'))

    def update_screen_list_combo(self):
        """
        The user changed screen resolution or enabled/disabled more screens, so
        we need to update the combo box.
        """
        self.display_combo_box.clear()
        self.display_combo_box.addItems(self.screens.get_screen_list())
        self.display_combo_box.setCurrentIndex(self.display_combo_box.count() - 1)

    def on_current_id_changed(self, page_id):
        """
        Detects Page changes and updates as appropriate.
        """
        # Keep track of the page we are at.  Triggering "Cancel" causes page_id to be a -1.
        self.application.process_events()
        if page_id != -1:
            self.last_id = page_id
        if page_id == FirstTimePage.Download:
            self.back_button.setVisible(False)
            self.next_button.setVisible(False)
            # Set the no internet page text.
            if self.has_run_wizard:
                self.no_internet_label.setText(self.no_internet_text)
            else:
                self.no_internet_label.setText(self.no_internet_text + self.cancel_wizard_text)
            self.application.set_busy_cursor()
            self._download_index()
            self.application.set_normal_cursor()
            self.back_button.setVisible(False)
            self.next_button.setVisible(True)
            self.next()
        elif page_id == FirstTimePage.Defaults:
            self.theme_combo_box.clear()
            for index in range(self.themes_list_widget.count()):
                item = self.themes_list_widget.item(index)
                if item.checkState() == QtCore.Qt.Checked:
                    self.theme_combo_box.addItem(item.text())
            if self.has_run_wizard:
                # Add any existing themes to list.
                for theme in self.theme_manager.get_themes():
                    index = self.theme_combo_box.findText(theme)
                    if index == -1:
                        self.theme_combo_box.addItem(theme)
                default_theme = Settings().value('themes/global theme')
                # Pre-select the current default theme.
                index = self.theme_combo_box.findText(default_theme)
                self.theme_combo_box.setCurrentIndex(index)
        elif page_id == FirstTimePage.NoInternet:
            self.back_button.setVisible(False)
            self.next_button.setVisible(False)
            self.cancel_button.setVisible(False)
            self.no_internet_finish_button.setVisible(True)
            if self.has_run_wizard:
                self.no_internet_cancel_button.setVisible(False)
            else:
                self.no_internet_cancel_button.setVisible(True)
        elif page_id == FirstTimePage.Plugins:
            self.back_button.setVisible(False)
        elif page_id == FirstTimePage.Progress:
            self.application.set_busy_cursor()
            self._pre_wizard()
            self._perform_wizard()
            self._post_wizard()
            self.application.set_normal_cursor()

    def on_cancel_button_clicked(self):
        """
        Process the triggering of the cancel button.
        """
        self.was_cancelled = True
        if self.theme_screenshot_workers:
            for worker in self.theme_screenshot_workers:
                worker.set_download_canceled(True)
        # Was the thread created.
        if self.theme_screenshot_threads:
            while any([thread.isRunning() for thread in self.theme_screenshot_threads]):
                time.sleep(0.1)
        self.application.set_normal_cursor()

    def on_screenshot_downloaded(self, title, filename, sha256):
        """
        Add an item to the list when a theme has been downloaded

        :param title: The title of the theme
        :param filename: The filename of the theme
        """
        item = QtGui.QListWidgetItem(title, self.themes_list_widget)
        item.setData(QtCore.Qt.UserRole, (filename, sha256))
        item.setCheckState(QtCore.Qt.Unchecked)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)

    def on_no_internet_finish_button_clicked(self):
        """
        Process the triggering of the "Finish" button on the No Internet page.
        """
        self.application.set_busy_cursor()
        self._perform_wizard()
        self.application.set_normal_cursor()
        Settings().setValue('core/has run wizard', True)
        self.close()

    def on_no_internet_cancel_button_clicked(self):
        """
        Process the triggering of the "Cancel" button on the No Internet page.
        """
        self.was_cancelled = True
        self.close()

    def url_get_file(self, url, f_path, sha256=None):
        """"
        Download a file given a URL.  The file is retrieved in chunks, giving the ability to cancel the download at any
        point. Returns False on download error.

        :param url: URL to download
        :param f_path: Destination file
        """
        block_count = 0
        block_size = 4096
        retries = 0
        while True:
            try:
                filename = open(f_path, "wb")
                url_file = urllib.request.urlopen(url, timeout=CONNECTION_TIMEOUT)
                if sha256:
                    hasher = hashlib.sha256()
                # Download until finished or canceled.
                while not self.was_cancelled:
                    data = url_file.read(block_size)
                    if not data:
                        break
                    filename.write(data)
                    if sha256:
                        hasher.update(data)
                    block_count += 1
                    self._download_progress(block_count, block_size)
                filename.close()
                if sha256 and hasher.hexdigest() != sha256:
                    log.error('sha256 sums did not match for file: {}'.format(f_path))
                    os.remove(f_path)
                    return False
            except (urllib.error.URLError, socket.timeout) as err:
                trace_error_handler(log)
                filename.close()
                os.remove(f_path)
                if retries > CONNECTION_RETRIES:
                    return False
                else:
                    retries += 1
                    time.sleep(0.1)
                    continue
            break
        # Delete file if cancelled, it may be a partial file.
        if self.was_cancelled:
            os.remove(f_path)
        return True

    def _build_theme_screenshots(self):
        """
        This method builds the theme screenshots' icons for all items in the ``self.themes_list_widget``.
        """
        themes = self.config.get('themes', 'files')
        themes = themes.split(',')
        for index, theme in enumerate(themes):
            screenshot = self.config.get('theme_%s' % theme, 'screenshot')
            item = self.themes_list_widget.item(index)
            if item:
                item.setIcon(build_icon(os.path.join(gettempdir(), 'openlp', screenshot)))

    def _get_file_size(self, url):
        """
        Get the size of a file.

        :param url: The URL of the file we want to download.
        """
        retries = 0
        while True:
            try:
                site = urllib.request.urlopen(url, timeout=CONNECTION_TIMEOUT)
                meta = site.info()
                return int(meta.get("Content-Length"))
            except urllib.error.URLError:
                if retries > CONNECTION_RETRIES:
                    raise
                else:
                    retries += 1
                    time.sleep(0.1)
                    continue

    def _download_progress(self, count, block_size):
        """
        Calculate and display the download progress.
        """
        increment = (count * block_size) - self.previous_size
        self._increment_progress_bar(None, increment)
        self.previous_size = count * block_size

    def _increment_progress_bar(self, status_text, increment=1):
        """
        Update the wizard progress page.

        :param status_text: Current status information to display.
        :param increment: The value to increment the progress bar by.
        """
        if status_text:
            self.progress_label.setText(status_text)
        if increment > 0:
            self.progress_bar.setValue(self.progress_bar.value() + increment)
        self.application.process_events()

    def _pre_wizard(self):
        """
        Prepare the UI for the process.
        """
        self.max_progress = 0
        self.finish_button.setVisible(False)
        self.application.process_events()
        try:
            # Loop through the songs list and increase for each selected item
            for i in range(self.songs_list_widget.count()):
                self.application.process_events()
                item = self.songs_list_widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    filename, sha256 = item.data(QtCore.Qt.UserRole)
                    size = self._get_file_size('%s%s' % (self.songs_url, filename))
                    self.max_progress += size
            # Loop through the Bibles list and increase for each selected item
            iterator = QtGui.QTreeWidgetItemIterator(self.bibles_tree_widget)
            while iterator.value():
                self.application.process_events()
                item = iterator.value()
                if item.parent() and item.checkState(0) == QtCore.Qt.Checked:
                    filename, sha256 = item.data(0, QtCore.Qt.UserRole)
                    size = self._get_file_size('%s%s' % (self.bibles_url, filename))
                    self.max_progress += size
                iterator += 1
            # Loop through the themes list and increase for each selected item
            for i in range(self.themes_list_widget.count()):
                self.application.process_events()
                item = self.themes_list_widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    filename, sha256 = item.data(QtCore.Qt.UserRole)
                    size = self._get_file_size('%s%s' % (self.themes_url, filename))
                    self.max_progress += size
        except urllib.error.URLError:
            trace_error_handler(log)
            critical_error_message_box(translate('OpenLP.FirstTimeWizard', 'Download Error'),
                                       translate('OpenLP.FirstTimeWizard', 'There was a connection problem during '
                                                 'download, so further downloads will be skipped. Try to re-run the '
                                                 'First Time Wizard later.'))
            self.max_progress = 0
            self.web_access = None
        if self.max_progress:
            # Add on 2 for plugins status setting plus a "finished" point.
            self.max_progress += 2
            self.progress_bar.setValue(0)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(self.max_progress)
            self.progress_page.setTitle(translate('OpenLP.FirstTimeWizard', 'Setting Up And Downloading'))
            self.progress_page.setSubTitle(
                translate('OpenLP.FirstTimeWizard', 'Please wait while OpenLP is set up and your data is downloaded.'))
        else:
            self.progress_bar.setVisible(False)
            self.progress_page.setTitle(translate('OpenLP.FirstTimeWizard', 'Setting Up'))
            self.progress_page.setSubTitle('Setup complete.')
        self.repaint()
        self.application.process_events()
        # Try to give the wizard a chance to repaint itself
        time.sleep(0.1)

    def _post_wizard(self):
        """
        Clean up the UI after the process has finished.
        """
        if self.max_progress:
            self.progress_bar.setValue(self.progress_bar.maximum())
            if self.has_run_wizard:
                self.progress_label.setText(translate('OpenLP.FirstTimeWizard',
                                            'Download complete. Click the %s button to return to OpenLP.') %
                                            clean_button_text(self.buttonText(QtGui.QWizard.FinishButton)))
            else:
                self.progress_label.setText(translate('OpenLP.FirstTimeWizard',
                                            'Download complete. Click the %s button to start OpenLP.') %
                                            clean_button_text(self.buttonText(QtGui.QWizard.FinishButton)))
        else:
            if self.has_run_wizard:
                self.progress_label.setText(translate('OpenLP.FirstTimeWizard',
                                            'Click the %s button to return to OpenLP.') %
                                            clean_button_text(self.buttonText(QtGui.QWizard.FinishButton)))
            else:
                self.progress_label.setText(translate('OpenLP.FirstTimeWizard',
                                            'Click the %s button to start OpenLP.') %
                                            clean_button_text(self.buttonText(QtGui.QWizard.FinishButton)))
        self.finish_button.setVisible(True)
        self.finish_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.next_button.setVisible(False)
        self.application.process_events()

    def _perform_wizard(self):
        """
        Run the tasks in the wizard.
        """
        # Set plugin states
        self._increment_progress_bar(translate('OpenLP.FirstTimeWizard', 'Enabling selected plugins...'))
        self._set_plugin_status(self.songs_check_box, 'songs/status')
        self._set_plugin_status(self.bible_check_box, 'bibles/status')
        self._set_plugin_status(self.presentation_check_box, 'presentations/status')
        self._set_plugin_status(self.image_check_box, 'images/status')
        self._set_plugin_status(self.media_check_box, 'media/status')
        self._set_plugin_status(self.remote_check_box, 'remotes/status')
        self._set_plugin_status(self.custom_check_box, 'custom/status')
        self._set_plugin_status(self.song_usage_check_box, 'songusage/status')
        self._set_plugin_status(self.alert_check_box, 'alerts/status')
        if self.web_access:
            if not self._download_selected():
                critical_error_message_box(translate('OpenLP.FirstTimeWizard', 'Download Error'),
                                           translate('OpenLP.FirstTimeWizard', 'There was a connection problem while '
                                                     'downloading, so further downloads will be skipped. Try to re-run '
                                                     'the First Time Wizard later.'))
        # Set Default Display
        if self.display_combo_box.currentIndex() != -1:
            Settings().setValue('core/monitor', self.display_combo_box.currentIndex())
            self.screens.set_current_display(self.display_combo_box.currentIndex())
        # Set Global Theme
        if self.theme_combo_box.currentIndex() != -1:
            Settings().setValue('themes/global theme', self.theme_combo_box.currentText())

    def _download_selected(self):
        """
        Download selected songs, bibles and themes. Returns False on download error
        """
        # Build directories for downloads
        songs_destination = os.path.join(gettempdir(), 'openlp')
        bibles_destination = AppLocation.get_section_data_path('bibles')
        themes_destination = AppLocation.get_section_data_path('themes')
        missed_files = []
        # Download songs
        for i in range(self.songs_list_widget.count()):
            item = self.songs_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                filename, sha256 = item.data(QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading % filename, 0)
                self.previous_size = 0
                destination = os.path.join(songs_destination, str(filename))
                if not self.url_get_file('%s%s' % (self.songs_url, filename), destination, sha256):
                    missed_files.append('Song: {}'.format(filename))
        # Download Bibles
        bibles_iterator = QtGui.QTreeWidgetItemIterator(self.bibles_tree_widget)
        while bibles_iterator.value():
            item = bibles_iterator.value()
            if item.parent() and item.checkState(0) == QtCore.Qt.Checked:
                bible, sha256 = item.data(0, QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading % bible, 0)
                self.previous_size = 0
                if not self.url_get_file('%s%s' % (self.bibles_url, bible), os.path.join(bibles_destination, bible),
                                         sha256):
                    missed_files.append('Bible: {}'.format(bible))
            bibles_iterator += 1
        # Download themes
        for i in range(self.themes_list_widget.count()):
            item = self.themes_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                theme, sha256 = item.data(QtCore.Qt.UserRole)
                self._increment_progress_bar(self.downloading % theme, 0)
                self.previous_size = 0
                if not self.url_get_file('%s%s' % (self.themes_url, theme), os.path.join(themes_destination, theme),
                                         sha256):
                    missed_files.append('Theme: {}'.format(theme))
        if missed_files:
            file_list = ''
            for entry in missed_files:
                file_list += '{}<br \>'.format(entry)
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setWindowTitle(translate('OpenLP.FirstTimeWizard', 'Network Error'))
            msg.setText(translate('OpenLP.FirstTimeWizard', 'Unable to download some files'))
            msg.setInformativeText(translate('OpenLP.FirstTimeWizard',
                                             'The following files were not able to be '
                                             'downloaded:<br \>{}'.format(file_list)))
            msg.setStandardButtons(msg.Ok)
            ans = msg.exec_()
        return True

    def _set_plugin_status(self, field, tag):
        """
        Set the status of a plugin.
        """
        status = PluginStatus.Active if field.checkState() == QtCore.Qt.Checked else PluginStatus.Inactive
        Settings().setValue(tag, status)
