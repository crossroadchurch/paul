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
The bible import functions for OpenLP
"""
import logging
import os
import shutil
from tempfile import gettempdir

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, AppLocation, UiStrings, Settings, check_directory_exists, translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.wizard import OpenLPWizard, WizardStrings
from openlp.core.utils import delete_file
from openlp.plugins.bibles.lib.db import BibleDB, BibleMeta, OldBibleDB, BiblesResourcesDB
from openlp.plugins.bibles.lib.http import BSExtract, BGExtract, CWExtract

log = logging.getLogger(__name__)


class BibleUpgradeForm(OpenLPWizard):
    """
    This is the Bible Upgrade Wizard, which allows easy importing of Bibles into OpenLP from older OpenLP2 database
    versions.
    """
    log.info('BibleUpgradeForm loaded')

    def __init__(self, parent, manager, bible_plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        :param manager: The Bible manager.
        :param bible_plugin: The Bible plugin.
        """
        self.manager = manager
        self.media_item = bible_plugin.media_item
        self.suffix = '.sqlite'
        self.settings_section = 'bibles'
        self.path = AppLocation.get_section_data_path(self.settings_section)
        self.temp_dir = os.path.join(gettempdir(), 'openlp')
        self.files = self.manager.old_bible_databases
        self.success = {}
        self.new_bibles = {}
        super(BibleUpgradeForm, self).__init__(
            parent, bible_plugin, 'bibleUpgradeWizard', ':/wizards/wizard_importbible.bmp')

    def setupUi(self, image):
        """
        Set up the UI for the bible wizard.
        """
        super(BibleUpgradeForm, self).setupUi(image)
        Registry().register_function('openlp_stop_wizard', self.stop_import)

    def stop_import(self):
        """
        Stops the import of the Bible.
        """
        log.debug('Stopping import')
        self.stop_import_flag = True

    def reject(self):
        """
        Stop the wizard on cancel button, close button or ESC key.
        """
        log.debug('Wizard cancelled by user')
        self.stop_import_flag = True
        if not self.currentPage() == self.progress_page:
            self.done(QtGui.QDialog.Rejected)

    def onCurrentIdChanged(self, page_id):
        """
        Perform necessary functions depending on which wizard page is active.
        """
        if self.page(page_id) == self.progress_page:
            self.pre_wizard()
            self.perform_wizard()
            self.post_wizard()
        elif self.page(page_id) == self.selectPage and not self.files:
            self.next()

    def on_backup_browse_button_clicked(self):
        """
        Show the file open dialog for the OSIS file.
        """
        filename = QtGui.QFileDialog.getExistingDirectory(self, translate('BiblesPlugin.UpgradeWizardForm',
                                                                          'Select a Backup Directory'), '')
        if filename:
            self.backupDirectoryEdit.setText(filename)

    def on_no_backup_check_box_toggled(self, checked):
        """
        Enable or disable the backup directory widgets.
        """
        self.backupDirectoryEdit.setEnabled(not checked)
        self.backupBrowseButton.setEnabled(not checked)

    def backup_old_bibles(self, backup_directory):
        """
        Backup old bible databases in a given folder.
        """
        check_directory_exists(backup_directory)
        success = True
        for filename in self.files:
            try:
                shutil.copy(os.path.join(self.path, filename[0]), backup_directory)
            except:
                success = False
        return success

    def custom_init(self):
        """
        Perform any custom initialisation for bible upgrading.
        """
        self.manager.set_process_dialog(self)
        self.restart()

    def custom_signals(self):
        """
        Set up the signals used in the bible importer.
        """
        self.backupBrowseButton.clicked.connect(self.on_backup_browse_button_clicked)
        self.noBackupCheckBox.toggled.connect(self.on_no_backup_check_box_toggled)

    def add_custom_pages(self):
        """
        Add the bible import specific wizard pages.
        """
        # Backup Page
        self.backup_page = QtGui.QWizardPage()
        self.backup_page.setObjectName('BackupPage')
        self.backupLayout = QtGui.QVBoxLayout(self.backup_page)
        self.backupLayout.setObjectName('BackupLayout')
        self.backupInfoLabel = QtGui.QLabel(self.backup_page)
        self.backupInfoLabel.setOpenExternalLinks(True)
        self.backupInfoLabel.setTextFormat(QtCore.Qt.RichText)
        self.backupInfoLabel.setWordWrap(True)
        self.backupInfoLabel.setObjectName('backupInfoLabel')
        self.backupLayout.addWidget(self.backupInfoLabel)
        self.selectLabel = QtGui.QLabel(self.backup_page)
        self.selectLabel.setObjectName('select_label')
        self.backupLayout.addWidget(self.selectLabel)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName('FormLayout')
        self.backupDirectoryLabel = QtGui.QLabel(self.backup_page)
        self.backupDirectoryLabel.setObjectName('backupDirectoryLabel')
        self.backupDirectoryLayout = QtGui.QHBoxLayout()
        self.backupDirectoryLayout.setObjectName('BackupDirectoryLayout')
        self.backupDirectoryEdit = QtGui.QLineEdit(self.backup_page)
        self.backupDirectoryEdit.setObjectName('BackupFolderEdit')
        self.backupDirectoryLayout.addWidget(self.backupDirectoryEdit)
        self.backupBrowseButton = QtGui.QToolButton(self.backup_page)
        self.backupBrowseButton.setIcon(self.open_icon)
        self.backupBrowseButton.setObjectName('BackupBrowseButton')
        self.backupDirectoryLayout.addWidget(self.backupBrowseButton)
        self.formLayout.addRow(self.backupDirectoryLabel, self.backupDirectoryLayout)
        self.backupLayout.addLayout(self.formLayout)
        self.noBackupCheckBox = QtGui.QCheckBox(self.backup_page)
        self.noBackupCheckBox.setObjectName('NoBackupCheckBox')
        self.backupLayout.addWidget(self.noBackupCheckBox)
        self.spacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.backupLayout.addItem(self.spacer)
        self.addPage(self.backup_page)
        # Select Page
        self.selectPage = QtGui.QWizardPage()
        self.selectPage.setObjectName('SelectPage')
        self.pageLayout = QtGui.QVBoxLayout(self.selectPage)
        self.pageLayout.setObjectName('pageLayout')
        self.scrollArea = QtGui.QScrollArea(self.selectPage)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName('scrollArea')
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollAreaContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaContents.setObjectName('scrollAreaContents')
        self.formLayout = QtGui.QVBoxLayout(self.scrollAreaContents)
        self.formLayout.setSpacing(2)
        self.formLayout.setObjectName('formLayout')
        self.addScrollArea()
        self.pageLayout.addWidget(self.scrollArea)
        self.addPage(self.selectPage)

    def addScrollArea(self):
        """
        Add the content to the scrollArea.
        """
        self.checkBox = {}
        for number, filename in enumerate(self.files):
            bible = OldBibleDB(self.media_item, path=self.path, file=filename[0])
            self.checkBox[number] = QtGui.QCheckBox(self.scrollAreaContents)
            self.checkBox[number].setObjectName('checkBox[%d]' % number)
            self.checkBox[number].setText(bible.get_name())
            self.checkBox[number].setCheckState(QtCore.Qt.Checked)
            self.formLayout.addWidget(self.checkBox[number])
        self.spacer_item = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.addItem(self.spacer_item)
        self.scrollArea.setWidget(self.scrollAreaContents)

    def clearScrollArea(self):
        """
        Remove the content from the scrollArea.
        """
        for number, filename in enumerate(self.files):
            self.formLayout.removeWidget(self.checkBox[number])
            self.checkBox[number].setParent(None)
        self.formLayout.removeItem(self.spacer_item)

    def retranslateUi(self):
        """
        Allow for localisation of the bible import wizard.
        """
        self.setWindowTitle(translate('BiblesPlugin.UpgradeWizardForm', 'Bible Upgrade Wizard'))
        self.title_label.setText(WizardStrings.HeaderStyle % translate('OpenLP.Ui',
                                                                       'Welcome to the Bible Upgrade Wizard'))
        self.information_label.setText(
            translate('BiblesPlugin.UpgradeWizardForm',
                      'This wizard will help you to upgrade your existing Bibles from a prior version of OpenLP 2. '
                      'Click the next button below to start the upgrade process.'))
        self.backup_page.setTitle(translate('BiblesPlugin.UpgradeWizardForm', 'Select Backup Directory'))
        self.backup_page.setSubTitle(
            translate('BiblesPlugin.UpgradeWizardForm', 'Please select a backup directory for your Bibles'))
        self.backupInfoLabel.setText(
            translate('BiblesPlugin.UpgradeWizardForm',
                      'Previous releases of OpenLP 2.0 are unable to use upgraded Bibles.'
                      ' This will create a backup of your current Bibles so that you can '
                      'simply copy the files back to your OpenLP data directory if you '
                      'need to revert to a previous release of OpenLP. Instructions on '
                      'how to restore the files can be found in our <a href="'
                      'http://wiki.openlp.org/faq">Frequently Asked Questions</a>.'))
        self.selectLabel.setText(
            translate('BiblesPlugin.UpgradeWizardForm', 'Please select a backup location for your Bibles.'))
        self.backupDirectoryLabel.setText(translate('BiblesPlugin.UpgradeWizardForm', 'Backup Directory:'))
        self.noBackupCheckBox.setText(
            translate('BiblesPlugin.UpgradeWizardForm', 'There is no need to backup my Bibles'))
        self.selectPage.setTitle(translate('BiblesPlugin.UpgradeWizardForm', 'Select Bibles'))
        self.selectPage.setSubTitle(
            translate('BiblesPlugin.UpgradeWizardForm', 'Please select the Bibles to upgrade'))
        self.progress_page.setTitle(translate('BiblesPlugin.UpgradeWizardForm', 'Upgrading'))
        self.progress_page.setSubTitle(
            translate('BiblesPlugin.UpgradeWizardForm', 'Please wait while your Bibles are upgraded.'))
        self.progress_label.setText(WizardStrings.Ready)
        self.progress_bar.setFormat('%p%')

    def validateCurrentPage(self):
        """
        Validate the current page before moving on to the next page.
        """
        if self.currentPage() == self.welcome_page:
            return True
        elif self.currentPage() == self.backup_page:
            if not self.noBackupCheckBox.checkState() == QtCore.Qt.Checked:
                backup_path = self.backupDirectoryEdit.text()
                if not backup_path:
                    critical_error_message_box(
                        UiStrings().EmptyField,
                        translate('BiblesPlugin.UpgradeWizardForm', 'You need to specify a backup directory for '
                                                                    'your Bibles.'))
                    self.backupDirectoryEdit.setFocus()
                    return False
                else:
                    if not self.backup_old_bibles(backup_path):
                        critical_error_message_box(
                            UiStrings().Error,
                            translate('BiblesPlugin.UpgradeWizardForm', 'The backup was not successful.\nTo backup '
                                      'your Bibles you need permission to write to the given directory.'))
                        return False
            return True
        elif self.currentPage() == self.selectPage:
            check_directory_exists(self.temp_dir)
            for number, filename in enumerate(self.files):
                if not self.checkBox[number].checkState() == QtCore.Qt.Checked:
                    continue
                # Move bibles to temp dir.
                if not os.path.exists(os.path.join(self.temp_dir, filename[0])):
                    shutil.move(os.path.join(self.path, filename[0]), self.temp_dir)
                else:
                    delete_file(os.path.join(self.path, filename[0]))
            return True
        if self.currentPage() == self.progress_page:
            return True

    def set_defaults(self):
        """
        Set default values for the wizard pages.
        """
        log.debug('BibleUpgrade set_defaults')
        settings = Settings()
        settings.beginGroup(self.plugin.settings_section)
        self.stop_import_flag = False
        self.success.clear()
        self.new_bibles.clear()
        self.clearScrollArea()
        self.files = self.manager.old_bible_databases
        self.addScrollArea()
        self.retranslateUi()
        for number, filename in enumerate(self.files):
            self.checkBox[number].setCheckState(QtCore.Qt.Checked)
        self.progress_bar.show()
        self.restart()
        self.finish_button.setVisible(False)
        self.cancel_button.setVisible(True)
        settings.endGroup()

    def pre_wizard(self):
        """
        Prepare the UI for the upgrade.
        """
        super(BibleUpgradeForm, self).pre_wizard()
        self.progress_label.setText(translate('BiblesPlugin.UpgradeWizardForm', 'Starting upgrade...'))
        self.application.process_events()

    def perform_wizard(self):
        """
        Perform the actual upgrade.
        """
        self.includeWebBible = False
        proxy_server = None
        if not self.files:
            self.progress_label.setText(
                translate('BiblesPlugin.UpgradeWizardForm', 'There are no Bibles that need to be upgraded.'))
            self.progress_bar.hide()
            return
        max_bibles = 0
        for number, file in enumerate(self.files):
            if self.checkBox[number].checkState() == QtCore.Qt.Checked:
                max_bibles += 1
        old_bible = None
        for number, filename in enumerate(self.files):
            # Close the previous bible's connection.
            if old_bible is not None:
                old_bible.close_connection()
                # Set to None to make obvious that we have already closed the
                # database.
                old_bible = None
            if self.stop_import_flag:
                self.success[number] = False
                break
            if not self.checkBox[number].checkState() == QtCore.Qt.Checked:
                self.success[number] = False
                continue
            self.progress_bar.reset()
            old_bible = OldBibleDB(self.media_item, path=self.temp_dir, file=filename[0])
            name = filename[1]
            self.progress_label.setText(
                translate('BiblesPlugin.UpgradeWizardForm',
                          'Upgrading Bible %s of %s: "%s"\nUpgrading ...') % (number + 1, max_bibles, name))
            self.new_bibles[number] = BibleDB(self.media_item, path=self.path, name=name, file=filename[0])
            self.new_bibles[number].register(self.plugin.upgrade_wizard)
            metadata = old_bible.get_metadata()
            web_bible = False
            meta_data = {}
            for meta in metadata:
                # Upgrade the names of the metadata keys
                if meta['key'] == 'Version':
                    meta['key'] = 'name'
                if meta['key'] == 'Bookname language':
                    meta['key'] = 'book_name_language'
                meta['key'] = meta['key'].lower().replace(' ', '_')
                # Copy the metadata
                meta_data[meta['key']] = meta['value']
                if meta['key'] != 'name' and meta['key'] != 'dbversion':
                    self.new_bibles[number].save_meta(meta['key'], meta['value'])
                if meta['key'] == 'download_source':
                    web_bible = True
                    self.includeWebBible = True
                proxy_server = meta.get('proxy_server')
            if web_bible:
                if meta_data['download_source'].lower() == 'crosswalk':
                    handler = CWExtract(proxy_server)
                elif meta_data['download_source'].lower() == 'biblegateway':
                    handler = BGExtract(proxy_server)
                elif meta_data['download_source'].lower() == 'bibleserver':
                    handler = BSExtract(proxy_server)
                books = handler.get_books_from_http(meta_data['download_name'])
                if not books:
                    log.error('Upgrading books from %s - download name: "%s" failed' % (
                        meta_data['download_source'], meta_data['download_name']))
                    self.new_bibles[number].session.close()
                    del self.new_bibles[number]
                    critical_error_message_box(
                        translate('BiblesPlugin.UpgradeWizardForm', 'Download Error'),
                        translate('BiblesPlugin.UpgradeWizardForm',
                                  'To upgrade your Web Bibles an Internet connection is required.'))
                    self.increment_progress_bar(translate(
                        'BiblesPlugin.UpgradeWizardForm', 'Upgrading Bible %s of %s: "%s"\nFailed') %
                        (number + 1, max_bibles, name), self.progress_bar.maximum() - self.progress_bar.value())
                    self.success[number] = False
                    continue
                bible = BiblesResourcesDB.get_webbible(
                    meta_data['download_name'],
                    meta_data['download_source'].lower())
                if bible and bible['language_id']:
                    language_id = bible['language_id']
                    self.new_bibles[number].save_meta('language_id', language_id)
                else:
                    language_id = self.new_bibles[number].get_language(name)
                if not language_id:
                    log.warning('Upgrading from "%s" failed' % filename[0])
                    self.new_bibles[number].session.close()
                    del self.new_bibles[number]
                    self.increment_progress_bar(
                        translate('BiblesPlugin.UpgradeWizardForm',
                                  'Upgrading Bible %s of %s: "%s"\nFailed') % (number + 1, max_bibles, name),
                        self.progress_bar.maximum() - self.progress_bar.value())
                    self.success[number] = False
                    continue
                self.progress_bar.setMaximum(len(books))
                for book in books:
                    if self.stop_import_flag:
                        self.success[number] = False
                        break
                    self.increment_progress_bar(
                        translate('BiblesPlugin.UpgradeWizardForm',
                                  'Upgrading Bible %s of %s: "%s"\nUpgrading %s ...') %
                        (number + 1, max_bibles, name, book))
                    book_ref_id = self.new_bibles[number].\
                        get_book_ref_id_by_name(book, len(books), language_id)
                    if not book_ref_id:
                        log.warning('Upgrading books from %s - download name: "%s" aborted by user' % (
                            meta_data['download_source'], meta_data['download_name']))
                        self.new_bibles[number].session.close()
                        del self.new_bibles[number]
                        self.success[number] = False
                        break
                    book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                    db_book = self.new_bibles[number].create_book(book, book_ref_id, book_details['testament_id'])
                    # Try to import already downloaded verses.
                    oldbook = old_bible.get_book(book)
                    if oldbook:
                        verses = old_bible.get_verses(oldbook['id'])
                        if not verses:
                            log.warning('No verses found to import for book "%s"', book)
                            continue
                        for verse in verses:
                            if self.stop_import_flag:
                                self.success[number] = False
                                break
                            self.new_bibles[number].create_verse(db_book.id, int(verse['chapter']),
                                                                 int(verse['verse']), str(verse['text']))
                            self.application.process_events()
                        self.new_bibles[number].session.commit()
            else:
                language_id = self.new_bibles[number].get_object(BibleMeta, 'language_id')
                if not language_id:
                    language_id = self.new_bibles[number].get_language(name)
                if not language_id:
                    log.warning('Upgrading books from "%s" failed' % name)
                    self.new_bibles[number].session.close()
                    del self.new_bibles[number]
                    self.increment_progress_bar(
                        translate('BiblesPlugin.UpgradeWizardForm',
                                  'Upgrading Bible %s of %s: "%s"\nFailed') % (number + 1, max_bibles, name),
                        self.progress_bar.maximum() - self.progress_bar.value())
                    self.success[number] = False
                    continue
                books = old_bible.get_books()
                self.progress_bar.setMaximum(len(books))
                for book in books:
                    if self.stop_import_flag:
                        self.success[number] = False
                        break
                    self.increment_progress_bar(
                        translate('BiblesPlugin.UpgradeWizardForm',
                                  'Upgrading Bible %s of %s: "%s"\nUpgrading %s ...') %
                        (number + 1, max_bibles, name, book['name']))
                    book_ref_id = self.new_bibles[number].get_book_ref_id_by_name(book['name'], len(books), language_id)
                    if not book_ref_id:
                        log.warning('Upgrading books from %s " failed - aborted by user' % name)
                        self.new_bibles[number].session.close()
                        del self.new_bibles[number]
                        self.success[number] = False
                        break
                    book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                    db_book = self.new_bibles[number].create_book(book['name'], book_ref_id,
                                                                  book_details['testament_id'])
                    verses = old_bible.get_verses(book['id'])
                    if not verses:
                        log.warning('No verses found to import for book "%s"', book['name'])
                        self.new_bibles[number].delete_book(db_book)
                        continue
                    for verse in verses:
                        if self.stop_import_flag:
                            self.success[number] = False
                            break
                        self.new_bibles[number].create_verse(db_book.id, int(verse['chapter']), int(verse['verse']),
                                                             str(verse['text']))
                        self.application.process_events()
                    self.new_bibles[number].session.commit()
            if not self.success.get(number, True):
                self.increment_progress_bar(
                    translate('BiblesPlugin.UpgradeWizardForm',
                              'Upgrading Bible %s of %s: "%s"\nFailed') % (number + 1, max_bibles, name),
                    self.progress_bar.maximum() - self.progress_bar.value())
            else:
                self.success[number] = True
                self.new_bibles[number].save_meta('name', name)
                self.increment_progress_bar(
                    translate('BiblesPlugin.UpgradeWizardForm',
                              'Upgrading Bible %s of %s: "%s"\nComplete') % (number + 1, max_bibles, name))
            if number in self.new_bibles:
                self.new_bibles[number].session.close()
        # Close the last bible's connection if possible.
        if old_bible is not None:
            old_bible.close_connection()

    def post_wizard(self):
        """
        Clean up the UI after the import has finished.
        """
        successful_import = 0
        failed_import = 0
        for number, filename in enumerate(self.files):
            if self.success.get(number):
                successful_import += 1
            elif self.checkBox[number].checkState() == QtCore.Qt.Checked:
                failed_import += 1
                # Delete upgraded (but not complete, corrupted, ...) bible.
                delete_file(os.path.join(self.path, filename[0]))
                # Copy not upgraded bible back.
                shutil.move(os.path.join(self.temp_dir, filename[0]), self.path)
        if failed_import > 0:
            failed_import_text = translate('BiblesPlugin.UpgradeWizardForm', ', %s failed') % failed_import
        else:
            failed_import_text = ''
        if successful_import > 0:
            if self.includeWebBible:
                self.progress_label.setText(
                    translate('BiblesPlugin.UpgradeWizardForm',
                              'Upgrading Bible(s): %s successful%s\nPlease note that verses from Web Bibles will be '
                              'downloaded on demand and so an Internet connection is required.') %
                    (successful_import, failed_import_text))
            else:
                self.progress_label.setText(
                    translate('BiblesPlugin.UpgradeWizardForm', 'Upgrading Bible(s): %s successful%s') % (
                        successful_import, failed_import_text))
        else:
            self.progress_label.setText(translate('BiblesPlugin.UpgradeWizardForm', 'Upgrade failed.'))
        # Remove temp directory.
        shutil.rmtree(self.temp_dir, True)
        super(BibleUpgradeForm, self).post_wizard()
