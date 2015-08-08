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


from PyQt4 import QtCore, QtGui
from openlp.core.common import translate
from openlp.core.lib import build_icon


class Ui_MediaClipSelector(object):
    def setupUi(self, media_clip_selector):
        media_clip_selector.setObjectName('media_clip_selector')
        media_clip_selector.resize(554, 654)
        self.combobox_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        media_clip_selector.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding))
        self.main_layout = QtGui.QVBoxLayout(media_clip_selector)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setObjectName('main_layout')
        # Source groupbox
        self.source_groupbox = QtGui.QGroupBox(media_clip_selector)
        self.source_groupbox.setObjectName('source_groupbox')
        self.source_layout = QtGui.QHBoxLayout()
        self.source_layout.setContentsMargins(8, 8, 8, 8)
        self.source_layout.setObjectName('source_layout')
        self.source_groupbox.setLayout(self.source_layout)
        # Media path label
        self.media_path_label = QtGui.QLabel(self.source_groupbox)
        self.media_path_label.setObjectName('media_path_label')
        self.source_layout.addWidget(self.media_path_label)
        # Media path combobox
        self.media_path_combobox = QtGui.QComboBox(self.source_groupbox)
        # Make the combobox expand
        self.media_path_combobox.setSizePolicy(self.combobox_size_policy)
        self.media_path_combobox.setEditable(True)
        self.media_path_combobox.setObjectName('media_path_combobox')
        self.source_layout.addWidget(self.media_path_combobox)
        # Load disc button
        self.load_disc_button = QtGui.QPushButton(media_clip_selector)
        self.load_disc_button.setEnabled(True)
        self.load_disc_button.setObjectName('load_disc_button')
        self.source_layout.addWidget(self.load_disc_button)
        self.main_layout.addWidget(self.source_groupbox)
        # Track details group box
        self.track_groupbox = QtGui.QGroupBox(media_clip_selector)
        self.track_groupbox.setObjectName('track_groupbox')
        self.track_layout = QtGui.QFormLayout()
        self.track_layout.setContentsMargins(8, 8, 8, 8)
        self.track_layout.setObjectName('track_layout')
        self.label_alignment = self.track_layout.labelAlignment()
        self.track_groupbox.setLayout(self.track_layout)
        # Title track
        self.title_label = QtGui.QLabel(self.track_groupbox)
        self.title_label.setObjectName('title_label')
        self.titles_combo_box = QtGui.QComboBox(self.track_groupbox)
        self.titles_combo_box.setSizePolicy(self.combobox_size_policy)
        self.titles_combo_box.setEditText('')
        self.titles_combo_box.setObjectName('titles_combo_box')
        self.track_layout.addRow(self.title_label, self.titles_combo_box)
        # Audio track
        self.audio_track_label = QtGui.QLabel(self.track_groupbox)
        self.audio_track_label.setObjectName('audio_track_label')
        self.audio_tracks_combobox = QtGui.QComboBox(self.track_groupbox)
        self.audio_tracks_combobox.setSizePolicy(self.combobox_size_policy)
        self.audio_tracks_combobox.setObjectName('audio_tracks_combobox')
        self.track_layout.addRow(self.audio_track_label, self.audio_tracks_combobox)
        self.main_layout.addWidget(self.track_groupbox)
        # Subtitle track
        self.subtitle_track_label = QtGui.QLabel(self.track_groupbox)
        self.subtitle_track_label.setObjectName('subtitle_track_label')
        self.subtitle_tracks_combobox = QtGui.QComboBox(self.track_groupbox)
        self.subtitle_tracks_combobox.setSizePolicy(self.combobox_size_policy)
        self.subtitle_tracks_combobox.setObjectName('subtitle_tracks_combobox')
        self.track_layout.addRow(self.subtitle_track_label, self.subtitle_tracks_combobox)
        # Preview frame
        self.preview_frame = QtGui.QFrame(media_clip_selector)
        self.preview_frame.setMinimumSize(QtCore.QSize(320, 240))
        self.preview_frame.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                                           QtGui.QSizePolicy.MinimumExpanding))
        self.preview_frame.setStyleSheet('background-color:black;')
        self.preview_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.preview_frame.setObjectName('preview_frame')
        self.main_layout.addWidget(self.preview_frame)
        # player controls
        self.controls_layout = QtGui.QHBoxLayout()
        self.controls_layout.setObjectName('controls_layout')
        self.play_button = QtGui.QToolButton(media_clip_selector)
        self.play_button.setIcon(build_icon(':/slides/media_playback_start.png'))
        self.play_button.setObjectName('play_button')
        self.controls_layout.addWidget(self.play_button)
        self.position_slider = QtGui.QSlider(media_clip_selector)
        self.position_slider.setTracking(False)
        self.position_slider.setOrientation(QtCore.Qt.Horizontal)
        self.position_slider.setObjectName('position_slider')
        self.controls_layout.addWidget(self.position_slider)
        self.position_timeedit = QtGui.QTimeEdit(media_clip_selector)
        self.position_timeedit.setReadOnly(True)
        self.position_timeedit.setObjectName('position_timeedit')
        self.controls_layout.addWidget(self.position_timeedit)
        self.main_layout.addLayout(self.controls_layout)
        # Range
        self.range_groupbox = QtGui.QGroupBox(media_clip_selector)
        self.range_groupbox.setObjectName('range_groupbox')
        self.range_layout = QtGui.QGridLayout()
        self.range_layout.setContentsMargins(8, 8, 8, 8)
        self.range_layout.setObjectName('range_layout')
        self.range_groupbox.setLayout(self.range_layout)
        # Start position
        self.start_position_label = QtGui.QLabel(self.range_groupbox)
        self.start_position_label.setObjectName('start_position_label')
        self.range_layout.addWidget(self.start_position_label, 0, 0, self.label_alignment)
        self.start_position_edit = QtGui.QTimeEdit(self.range_groupbox)
        self.start_position_edit.setObjectName('start_position_edit')
        self.range_layout.addWidget(self.start_position_edit, 0, 1)
        self.set_start_button = QtGui.QPushButton(self.range_groupbox)
        self.set_start_button.setObjectName('set_start_button')
        self.range_layout.addWidget(self.set_start_button, 0, 2)
        self.jump_start_button = QtGui.QPushButton(self.range_groupbox)
        self.jump_start_button.setObjectName('jump_start_button')
        self.range_layout.addWidget(self.jump_start_button, 0, 3)
        # End position
        self.end_position_label = QtGui.QLabel(self.range_groupbox)
        self.end_position_label.setObjectName('end_position_label')
        self.range_layout.addWidget(self.end_position_label, 1, 0, self.label_alignment)
        self.end_timeedit = QtGui.QTimeEdit(self.range_groupbox)
        self.end_timeedit.setObjectName('end_timeedit')
        self.range_layout.addWidget(self.end_timeedit, 1, 1)
        self.set_end_button = QtGui.QPushButton(self.range_groupbox)
        self.set_end_button.setObjectName('set_end_button')
        self.range_layout.addWidget(self.set_end_button, 1, 2)
        self.jump_end_button = QtGui.QPushButton(self.range_groupbox)
        self.jump_end_button.setObjectName('jump_end_button')
        self.range_layout.addWidget(self.jump_end_button, 1, 3)
        self.main_layout.addWidget(self.range_groupbox)
        # Save and close buttons
        self.button_box = QtGui.QDialogButtonBox(media_clip_selector)
        self.button_box.addButton(QtGui.QDialogButtonBox.Save)
        self.button_box.addButton(QtGui.QDialogButtonBox.Close)
        self.close_button = self.button_box.button(QtGui.QDialogButtonBox.Close)
        self.save_button = self.button_box.button(QtGui.QDialogButtonBox.Save)
        self.main_layout.addWidget(self.button_box)

        self.retranslateUi(media_clip_selector)
        self.button_box.accepted.connect(media_clip_selector.accept)
        self.button_box.rejected.connect(media_clip_selector.reject)
        QtCore.QMetaObject.connectSlotsByName(media_clip_selector)
        media_clip_selector.setTabOrder(self.media_path_combobox, self.load_disc_button)
        media_clip_selector.setTabOrder(self.load_disc_button, self.titles_combo_box)
        media_clip_selector.setTabOrder(self.titles_combo_box, self.audio_tracks_combobox)
        media_clip_selector.setTabOrder(self.audio_tracks_combobox, self.subtitle_tracks_combobox)
        media_clip_selector.setTabOrder(self.subtitle_tracks_combobox, self.play_button)
        media_clip_selector.setTabOrder(self.play_button, self.position_slider)
        media_clip_selector.setTabOrder(self.position_slider, self.position_timeedit)
        media_clip_selector.setTabOrder(self.position_timeedit, self.start_position_edit)
        media_clip_selector.setTabOrder(self.start_position_edit, self.set_start_button)
        media_clip_selector.setTabOrder(self.set_start_button, self.jump_start_button)
        media_clip_selector.setTabOrder(self.jump_start_button, self.end_timeedit)
        media_clip_selector.setTabOrder(self.end_timeedit, self.set_end_button)
        media_clip_selector.setTabOrder(self.set_end_button, self.jump_end_button)
        media_clip_selector.setTabOrder(self.jump_end_button, self.save_button)
        media_clip_selector.setTabOrder(self.save_button, self.close_button)

    def retranslateUi(self, media_clip_selector):
        media_clip_selector.setWindowTitle(translate('MediaPlugin.MediaClipSelector', 'Select Media Clip'))
        self.source_groupbox.setTitle(translate('MediaPlugin.MediaClipSelector', 'Source'))
        self.media_path_label.setText(translate('MediaPlugin.MediaClipSelector', 'Media path:'))
        self.media_path_combobox.lineEdit().setPlaceholderText(translate('MediaPlugin.MediaClipSelector',
                                                                         'Select drive from list'))
        self.load_disc_button.setText(translate('MediaPlugin.MediaClipSelector', 'Load disc'))
        self.track_groupbox.setTitle(translate('MediaPlugin.MediaClipSelector', 'Track Details'))
        self.title_label.setText(translate('MediaPlugin.MediaClipSelector', 'Title:'))
        self.audio_track_label.setText(translate('MediaPlugin.MediaClipSelector', 'Audio track:'))
        self.subtitle_track_label.setText(translate('MediaPlugin.MediaClipSelector', 'Subtitle track:'))
        self.position_timeedit.setDisplayFormat(translate('MediaPlugin.MediaClipSelector', 'HH:mm:ss.z'))
        self.range_groupbox.setTitle(translate('MediaPlugin.MediaClipSelector', 'Clip Range'))
        self.start_position_label.setText(translate('MediaPlugin.MediaClipSelector', 'Start point:'))
        self.start_position_edit.setDisplayFormat(translate('MediaPlugin.MediaClipSelector', 'HH:mm:ss.z'))
        self.set_start_button.setText(translate('MediaPlugin.MediaClipSelector', 'Set start point'))
        self.jump_start_button.setText(translate('MediaPlugin.MediaClipSelector', 'Jump to start point'))
        self.end_position_label.setText(translate('MediaPlugin.MediaClipSelector', 'End point:'))
        self.end_timeedit.setDisplayFormat(translate('MediaPlugin.MediaClipSelector', 'HH:mm:ss.z'))
        self.set_end_button.setText(translate('MediaPlugin.MediaClipSelector', 'Set end point'))
        self.jump_end_button.setText(translate('MediaPlugin.MediaClipSelector', 'Jump to end point'))
