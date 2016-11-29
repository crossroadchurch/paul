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
The :mod:`serviceitem` provides the service item functionality including the
type and capability of an item.
"""

import datetime
import html
import logging
import os
import uuid
import ntpath
import re

from PyQt4 import QtGui

from openlp.core.common import RegistryProperties, Settings, translate, AppLocation, md5_hash
from openlp.core.lib import ImageSource, build_icon, clean_tags, expand_tags, create_thumb
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics
from openlp.plugins.songs.lib.chords import Chords

log = logging.getLogger(__name__)


class ServiceItemType(object):
    """
    Defines the type of service item
    """
    Text = 1
    Image = 2
    Command = 3


class ItemCapabilities(object):
    """
    Provides an enumeration of a service item's capabilities

    ``CanPreview``
            The capability to allow the ServiceManager to add to the preview tab when making the previous item live.

    ``CanEdit``
            The capability to allow the ServiceManager to allow the item to be edited

    ``CanMaintain``
            The capability to allow the ServiceManager to allow the item to be reordered.

    ``RequiresMedia``
            Determines is the service_item needs a Media Player

    ``CanLoop``
            The capability to allow the SlideController to allow the loop processing.

    ``CanAppend``
            The capability to allow the ServiceManager to add leaves to the
            item

    ``NoLineBreaks``
            The capability to remove lines breaks in the renderer

    ``OnLoadUpdate``
            The capability to update MediaManager when a service Item is loaded.

    ``AddIfNewItem``
            Not Used

    ``ProvidesOwnDisplay``
            The capability to tell the SlideController the service Item has a different display.

    ``HasDetailedTitleDisplay``
            Being Removed and decommissioned.

    ``HasVariableStartTime``
            The capability to tell the ServiceManager that a change to start time is possible.

    ``CanSoftBreak``
            The capability to tell the renderer that Soft Break is allowed

    ``CanWordSplit``
            The capability to tell the renderer that it can split words is
            allowed

    ``HasBackgroundAudio``
            That a audio file is present with the text.

    ``CanAutoStartForLive``
            The capability to ignore the do not play if display blank flag.

    ``CanEditTitle``
            The capability to edit the title of the item

    ``IsOptical``
            Determines is the service_item is based on an optical device

    ``HasDisplayTitle``
            The item contains 'displaytitle' on every frame which should be
            preferred over 'title' when displaying the item

    ``HasNotes``
            The item contains 'notes'

    ``HasThumbnails``
            The item has related thumbnails available

    """
    CanPreview = 1
    CanEdit = 2
    CanMaintain = 3
    RequiresMedia = 4
    CanLoop = 5
    CanAppend = 6
    NoLineBreaks = 7
    OnLoadUpdate = 8
    AddIfNewItem = 9
    ProvidesOwnDisplay = 10
    HasDetailedTitleDisplay = 11
    HasVariableStartTime = 12
    CanSoftBreak = 13
    CanWordSplit = 14
    HasBackgroundAudio = 15
    CanAutoStartForLive = 16
    CanEditTitle = 17
    IsOptical = 18
    HasDisplayTitle = 19
    HasNotes = 20
    HasThumbnails = 21


class ServiceItem(RegistryProperties):
    """
    The service item is a base class for the plugins to use to interact with
    the service manager, the slide controller, and the projection screen
    compositor.
    """
    log.info('Service Item created')

    def __init__(self, plugin=None):
        """
        Set up the service item.

        :param plugin: The plugin that this service item belongs to.
        """
        if plugin:
            self.name = plugin.name
            self.plugin = plugin
        else:
            self.name = '' # Added to stop crash when trying to edit template
        self.title = ''
        self.processor = None
        self.audit = ''
        self.items = []
        self.iconic_representation = None
        self.raw_footer = []
        self.foot_text = ''
        self.theme = None
        self.service_item_type = None
        self._raw_frames = []
        self._display_frames = []
        self.unique_identifier = 0
        self.notes = ''
        self.from_plugin = False
        self.capabilities = []
        self.is_valid = True
        self.icon = None
        self.theme_data = None
        self.main = None
        self.footer = None
        self.bg_image_bytes = None
        self.search_string = ''
        self.data_string = ''
        self.edit_id = None
        self.xml_version = None
        self.start_time = 0
        self.end_time = 0
        self.media_length = 0
        self.from_service = False
        self.image_border = '#000000'
        self.background_audio = []
        self.theme_overwritten = False
        self.temporary_edit = False
        self.auto_play_slides_once = False
        self.auto_play_slides_loop = False
        self.timed_slide_interval = 0
        self.will_auto_start = False
        self.has_original_files = True
        self.extra_data_dict = {}
        self._new_item()

    def _new_item(self):
        """
        Method to set the internal id of the item. This is used to compare service items to see if they are the same.
        """
        self.unique_identifier = str(uuid.uuid1())
        self.validate_item()

    def add_capability(self, capability):
        """
        Add an ItemCapability to a ServiceItem

        :param capability: The capability to add
        """
        self.capabilities.append(capability)

    def is_capable(self, capability):
        """
        Tell the caller if a ServiceItem has a capability

        :param capability: The capability to test for
        """
        return capability in self.capabilities

    def set_extra_data_dict(self, data_dict):
        self.extra_data_dict = data_dict

    def add_icon(self, icon):
        """
        Add an icon to the service item. This is used when displaying the service item in the service manager.

        :param icon: A string to an icon in the resources or on disk.
        """
        self.icon = icon
        self.iconic_representation = build_icon(icon)

    def render(self, provides_own_theme_data=False):
        """
        The render method is what generates the frames for the screen and obtains the display information from the
        renderer. At this point all slides are built for the given display size.

        :param provides_own_theme_data: This switch disables the usage of the item's theme. However, this is
            disabled by default. If this is used, it has to be taken care, that
            the renderer knows the correct theme data. However, this is needed
            for the theme manager.
        """
        log.debug('Render called')
        self._display_frames = []
        self.bg_image_bytes = None
        if not provides_own_theme_data:
            self.renderer.set_item_theme(self.theme)
            self.theme_data, self.main, self.footer = self.renderer.pre_render()
        if self.service_item_type == ServiceItemType.Text:
            log.debug('Formatting slides: %s' % self.title)
            # Save rendered pages to this dict. In the case that a slide is used twice we can use the pages saved to
            # the dict instead of rendering them again.

            if self.get_plugin_name() == 'songs':
                if not self.extra_data_dict:
                    self.extra_data_dict = {}
                    if not self.xml_version.startswith('<?xml') and not self.xml_version.startswith('<song'):
                        # This is an old style song, without XML.
                        verses = self.xml_version.split('\n\n')
                        for count, verse in enumerate(verses):
                            self.extra_data_dict['v' + str(count)] = str(verse).split('\n')

                    elif self.xml_version.startswith('<?xml'):
                        # New style song, output as XML.
                        song_xml_split = re.split('(<verse[\w"= ]*>)', self.xml_version)
                        current_section = ''

                        for song_part in song_xml_split:
                            if song_part.startswith("<verse name"):
                                current_section = song_part.replace('<verse name="', '').replace('">', '')
                            elif song_part.startswith("<lines"):
                                # New line needed between <lines> sections
                                song_part = song_part.replace('</lines><line', '</lines><br/><line')
                                # Split out <lines>, </lines>, </verse>, </lyrics> and </song> tags
                                song_part = ''.join(re.split('<lines[\w"= ]*>', song_part))
                                song_part = song_part.replace('</lines>','').replace('</verse>', '')
                                song_part = song_part.replace('</lyrics>','').replace('</song>', '')
                                # Convert to list
                                self.extra_data_dict[current_section] = song_part.split('<br/>')

                previous_pages = {}

                # Get key and transpose amount, if used in this song
                if "<key>" in self.xml_version:
                    current_key = self.xml_version[(self.xml_version.index('<key>') + 5):(self.xml_version.index('<key>')+7)]
                    if current_key[1] == '<':
                        current_key = current_key[0]
                else:
                    current_key = ''

                if "<transposition>" in self.xml_version:
                    current_transpose = self.xml_version[(self.xml_version.index('<transposition>') + 15):(self.xml_version.index('<transposition>')+18)]
                    # Possible options: 1,...,9, 10, 11, -1, ... -9, -10, -11
                    if current_transpose[1] == '<':
                        current_transpose = int(current_transpose[0])
                    elif current_transpose[2] == '<':
                        current_transpose = int(current_transpose[0:2])
                else:
                    current_transpose = 0

                # Calculate resultant key for musician oriented view
                if current_key != '':
                    resultant_key = Chords.transpose_chord(current_key, current_key, current_transpose)
                else:
                    resultant_key = ''

                for slide in self._raw_frames:
                    verse_tag = slide['verseTag']
                    if verse_tag in previous_pages and previous_pages[verse_tag][0] == slide['raw_slide']:
                        pages = previous_pages[verse_tag][1]
                    else:
                        pages = self.renderer.format_slide(slide['raw_slide'], self)
                        previous_pages[verse_tag] = (slide['raw_slide'], pages)

                    xml_lines = self.extra_data_dict[verse_tag.lower()]
                    #print(xml_lines)
                    #print("-----")
                    xml_line_lower, xml_line_upper = 0, 0

                    subpage_count = 0
                    for page in pages:
                        subpage_count += 1

                        # Given the current page_lines, calculate the corresponding xml_lines
                        xml_line_lower = xml_line_upper
                        xml_segment = ''.join(re.split('<chord[\w\+#"=// ]*/>', xml_lines[xml_line_upper]))

                        while (xml_line_upper < len(xml_lines)) and not (xml_segment.strip() == page.strip()):
                            xml_line_upper += 1
                            xml_segment = xml_segment + '<br>' + ''.join(re.split('<chord[\w\+#"=// ]*/>', xml_lines[xml_line_upper]))

                        xml_line_upper += 1
                        page_xml = xml_lines[xml_line_lower: xml_line_upper]

                        # Exclude any [br] or [---] elements from the XML list
                        page_xml_short = []
                        for item in page_xml:
                            if item != '[br]' and item != '[---]':
								# split item by chord tags, then transpose each chord tag
                                if current_transpose != 0:
                                    item_sections = re.split('(<chord[\w\+#"=// ]*/>)', item)
                                    transposed_item = ''

                                    for item_section in item_sections:
                                        if item_section.startswith('<chord name'):
                                            transposed_item = transposed_item + Chords.transpose_chord_tag(item_section, current_key, current_transpose)
                                        else:
                                            transposed_item = transposed_item + item_section
                                    page_xml_short.append(transposed_item)
                                else:
                                    page_xml_short.append(item)

                        page = page.replace('<br>', '{br}')
                        html_data = expand_tags(html.escape(page.rstrip()))
                        self._display_frames.append({
                            'title': clean_tags(page),
                            'text': clean_tags(page.rstrip()),
                            'html': html_data.replace('&amp;nbsp;', '&nbsp;'),
                            'verseTag': verse_tag,
                            'verseSubpage': subpage_count,
                            'extraInfo': '<br>'.join(page_xml_short),
                            'playedKey': resultant_key
                        })

                        # Deal with any [br] or [---] tag in XML before processing next page
                        if xml_line_upper < len(xml_lines) and \
                            (xml_lines[xml_line_upper].strip() == '[br]' or xml_lines[xml_line_upper].strip() == '[---]'):
                            xml_line_upper += 1

            else:
                previous_pages = {}
                for slide in self._raw_frames:
                    verse_tag = slide['verseTag']
                    if verse_tag in previous_pages and previous_pages[verse_tag][0] == slide['raw_slide']:
                        pages = previous_pages[verse_tag][1]
                    else:
                        pages = self.renderer.format_slide(slide['raw_slide'], self)
                        previous_pages[verse_tag] = (slide['raw_slide'], pages)

                    for page in pages:
                        page = page.replace('<br>', '{br}')
                        html_data = expand_tags(html.escape(page.rstrip()))
                        self._display_frames.append({
                            'title': clean_tags(page),
                            'text': clean_tags(page.rstrip()),
                            'html': html_data.replace('&amp;nbsp;', '&nbsp;'),
                            'verseTag': verse_tag,
                        })

        elif self.service_item_type == ServiceItemType.Image or self.service_item_type == ServiceItemType.Command:
            pass
        else:
            log.error('Invalid value renderer: %s' % self.service_item_type)
        self.title = clean_tags(self.title)
        # The footer should never be None, but to be compatible with a few
        # nightly builds between 1.9.4 and 1.9.5, we have to correct this to
        # avoid tracebacks.
        if self.raw_footer is None:
            self.raw_footer = []
        self.foot_text = '<br>'.join([_f for _f in self.raw_footer if _f])

    def add_from_image(self, path, title, background=None, thumbnail=None):
        """
        Add an image slide to the service item.

        :param path: The directory in which the image file is located.
        :param title: A title for the slide in the service item.
        :param background:
        :param thumbnail: Optional alternative thumbnail, used for remote thumbnails.
        """
        if background:
            self.image_border = background
        self.service_item_type = ServiceItemType.Image
        if not thumbnail:
            self._raw_frames.append({'title': title, 'path': path})
        else:
            self._raw_frames.append({'title': title, 'path': path, 'image': thumbnail})
        self.image_manager.add_image(path, ImageSource.ImagePlugin, self.image_border)
        self._new_item()

    def add_from_text(self, raw_slide, verse_tag=None):
        """
        Add a text slide to the service item.

        :param raw_slide: The raw text of the slide.
        :param verse_tag:
        """
        if verse_tag:
            verse_tag = verse_tag.upper()
        self.service_item_type = ServiceItemType.Text
        title = raw_slide[:30].split('\n')[0]
        self._raw_frames.append({'title': title, 'raw_slide': raw_slide, 'verseTag': verse_tag})
        self._new_item()

    def add_from_command(self, path, file_name, image, display_title=None, notes=None):
        """
        Add a slide from a command.

        :param path: The title of the slide in the service item.
        :param file_name: The title of the slide in the service item.
        :param image: The command of/for the slide.
        :param display_title: Title to show in gui/webinterface, optional.
        :param notes: Notes to show in the webinteface, optional.
        """
        self.service_item_type = ServiceItemType.Command
        # If the item should have a display title but this frame doesn't have one, we make one up
        if self.is_capable(ItemCapabilities.HasDisplayTitle) and not display_title:
            display_title = translate('OpenLP.ServiceItem', '[slide %d]') % (len(self._raw_frames) + 1)
        # Update image path to match servicemanager location if file was loaded from service
        if image and not self.has_original_files and self.name == 'presentations':
            file_location = os.path.join(path, file_name)
            file_location_hash = md5_hash(file_location.encode('utf-8'))
            image = os.path.join(AppLocation.get_section_data_path(self.name), 'thumbnails',
                                 file_location_hash, ntpath.basename(image))
        self._raw_frames.append({'title': file_name, 'image': image, 'path': path,
                                 'display_title': display_title, 'notes': notes})
        self._new_item()


    def get_item_xml(self):
        if self.xml_version:
            return self.xml_version
        else:
            return ''

    def get_plugin_name(self):
        if self.name:
            return self.name
        else:
            return ''

    def get_service_repr(self, lite_save):
        """
        This method returns some text which can be saved into the service file to represent this item.
        """
        service_header = {
            'name': self.name,
            'plugin': self.name,
            'theme': self.theme,
            'title': self.title,
            'icon': self.icon,
            'footer': self.raw_footer,
            'type': self.service_item_type,
            'audit': self.audit,
            'notes': self.notes,
            'from_plugin': self.from_plugin,
            'capabilities': self.capabilities,
            'search': self.search_string,
            'data': self.data_string,
            'xml_version': self.xml_version,
            'auto_play_slides_once': self.auto_play_slides_once,
            'auto_play_slides_loop': self.auto_play_slides_loop,
            'timed_slide_interval': self.timed_slide_interval,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'media_length': self.media_length,
            'background_audio': self.background_audio,
            'theme_overwritten': self.theme_overwritten,
            'will_auto_start': self.will_auto_start,
            'processor': self.processor
        }
        service_data = []
        if self.service_item_type == ServiceItemType.Text:
            service_data = [slide for slide in self._raw_frames]
        elif self.service_item_type == ServiceItemType.Image:
            if lite_save:
                for slide in self._raw_frames:
                    service_data.append({'title': slide['title'], 'path': slide['path']})
            else:
                service_data = [slide['title'] for slide in self._raw_frames]
        elif self.service_item_type == ServiceItemType.Command:
            for slide in self._raw_frames:
                service_data.append({'title': slide['title'], 'image': slide['image'], 'path': slide['path'],
                                     'display_title': slide['display_title'], 'notes': slide['notes']})
        return {'header': service_header, 'data': service_data}

    def set_from_service(self, service_item, path=None):
        """
        This method takes a service item from a saved service file (passed from the ServiceManager) and extracts the
        data actually required.

        :param service_item: The item to extract data from.
        :param path: Defaults to *None*. This is the service manager path for things which have their files saved
        with them or None when the saved service is lite and the original file paths need to be preserved.
        """
        log.debug('set_from_service called with path %s' % path)
        header = service_item['serviceitem']['header']
        self.title = header['title']
        self.name = header['name']
        self.service_item_type = header['type']
        self.theme = header['theme']
        self.add_icon(header['icon'])
        self.raw_footer = header['footer']
        self.audit = header['audit']
        self.notes = header['notes']
        self.from_plugin = header['from_plugin']
        self.capabilities = header['capabilities']
        # Added later so may not be present in older services.
        self.search_string = header.get('search', '')
        self.data_string = header.get('data', '')
        self.xml_version = header.get('xml_version')
        self.start_time = header.get('start_time', 0)
        self.end_time = header.get('end_time', 0)
        self.media_length = header.get('media_length', 0)
        self.auto_play_slides_once = header.get('auto_play_slides_once', False)
        self.auto_play_slides_loop = header.get('auto_play_slides_loop', False)
        self.timed_slide_interval = header.get('timed_slide_interval', 0)
        self.will_auto_start = header.get('will_auto_start', False)
        self.processor = header.get('processor', None)
        self.has_original_files = True
        # TODO: Remove me in 2,3 build phase
        if self.is_capable(ItemCapabilities.HasDetailedTitleDisplay):
            self.capabilities.remove(ItemCapabilities.HasDetailedTitleDisplay)
            self.processor = self.title
            self.title = None
        if 'background_audio' in header:
            self.background_audio = []
            for filename in header['background_audio']:
                # Give them real file paths.
                filepath = filename
                if path:
                    # Windows can handle both forward and backward slashes, so we use ntpath to get the basename
                    filepath = os.path.join(path, ntpath.basename(filename))
                self.background_audio.append(filepath)
        self.theme_overwritten = header.get('theme_overwritten', False)
        if self.service_item_type == ServiceItemType.Text:
            for slide in service_item['serviceitem']['data']:
                self._raw_frames.append(slide)
        elif self.service_item_type == ServiceItemType.Image:
            settings_section = service_item['serviceitem']['header']['name']
            background = QtGui.QColor(Settings().value(settings_section + '/background color'))
            if path:
                self.has_original_files = False
                for text_image in service_item['serviceitem']['data']:
                    filename = os.path.join(path, text_image)
                    self.add_from_image(filename, text_image, background)
            else:
                for text_image in service_item['serviceitem']['data']:
                    self.add_from_image(text_image['path'], text_image['title'], background)
        elif self.service_item_type == ServiceItemType.Command:
            for text_image in service_item['serviceitem']['data']:
                if not self.title:
                    self.title = text_image['title']
                if self.is_capable(ItemCapabilities.IsOptical):
                    self.has_original_files = False
                    self.add_from_command(text_image['path'], text_image['title'], text_image['image'])
                elif path:
                    self.has_original_files = False
                    self.add_from_command(path, text_image['title'], text_image['image'],
                                          text_image.get('display_title', ''), text_image.get('notes', ''))
                else:
                    self.add_from_command(text_image['path'], text_image['title'], text_image['image'])
        self._new_item()

    def get_display_title(self):
        """
        Returns the title of the service item.
        """
        if self.is_text() or self.is_capable(ItemCapabilities.IsOptical) \
                or self.is_capable(ItemCapabilities.CanEditTitle):
            return self.title
        else:
            if len(self._raw_frames) > 1:
                return self.title
            else:
                return self._raw_frames[0]['title']

    def merge(self, other):
        """
        Updates the unique_identifier with the value from the original one
        The unique_identifier is unique for a given service item but this allows one to replace an original version.

        :param other: The service item to be merged with
        """
        self.unique_identifier = other.unique_identifier
        self.notes = other.notes
        self.temporary_edit = other.temporary_edit
        # Copy theme over if present.
        if other.theme is not None:
            self.theme = other.theme
            self._new_item()
        self.render()
        if self.is_capable(ItemCapabilities.HasBackgroundAudio):
            log.debug(self.background_audio)

    def __eq__(self, other):
        """
        Confirms the service items are for the same instance
        """
        if not other:
            return False
        return self.unique_identifier == other.unique_identifier

    def __ne__(self, other):
        """
        Confirms the service items are not for the same instance
        """
        return self.unique_identifier != other.unique_identifier

    def __hash__(self):
        """
        Return the hash for the service item.
        """
        return self.unique_identifier

    def is_media(self):
        """
        Confirms if the ServiceItem is media
        """
        return ItemCapabilities.RequiresMedia in self.capabilities

    def is_command(self):
        """
        Confirms if the ServiceItem is a command
        """
        return self.service_item_type == ServiceItemType.Command

    def is_image(self):
        """
        Confirms if the ServiceItem is an image
        """
        return self.service_item_type == ServiceItemType.Image

    def uses_file(self):
        """
        Confirms if the ServiceItem uses a file
        """
        return self.service_item_type == ServiceItemType.Image or \
            (self.service_item_type == ServiceItemType.Command and not self.is_capable(ItemCapabilities.IsOptical))

    def is_text(self):
        """
        Confirms if the ServiceItem is text
        """
        return self.service_item_type == ServiceItemType.Text

    def set_media_length(self, length):
        """
        Stores the media length of the item

        :param length: The length of the media item
        """
        self.media_length = length
        if length > 0:
            self.add_capability(ItemCapabilities.HasVariableStartTime)

    def get_frames(self):
        """
        Returns the frames for the ServiceItem
        """
        if self.service_item_type == ServiceItemType.Text:
            return self._display_frames
        else:
            return self._raw_frames

    def get_rendered_frame(self, row):
        """
        Returns the correct frame for a given list and renders it if required.

        :param row: The service item slide to be returned
        """
        if self.service_item_type == ServiceItemType.Text:
            return self._display_frames[row]['html'].split('\n')[0]
        elif self.service_item_type == ServiceItemType.Image:
            return self._raw_frames[row]['path']
        else:
            return self._raw_frames[row]['image']

    def get_frame_title(self, row=0):
        """
        Returns the title of the raw frame
        """
        try:
            return self._raw_frames[row]['title']
        except IndexError:
            return ''

    def get_frame_path(self, row=0, frame=None):
        """
        Returns the path of the raw frame
        """
        if not frame:
            try:
                frame = self._raw_frames[row]
            except IndexError:
                return ''
        if self.is_image() or self.is_capable(ItemCapabilities.IsOptical):
            path_from = frame['path']
        else:
            path_from = os.path.join(frame['path'], frame['title'])
        return path_from

    def remove_frame(self, frame):
        """
        Remove the specified frame from the item
        """
        if frame in self._raw_frames:
            self._raw_frames.remove(frame)

    def get_media_time(self):
        """
        Returns the start and finish time for a media item
        """
        start = None
        end = None
        if self.start_time != 0:
            start = translate('OpenLP.ServiceItem', '<strong>Start</strong>: %s') % \
                str(datetime.timedelta(seconds=self.start_time))
        if self.media_length != 0:
            end = translate('OpenLP.ServiceItem', '<strong>Length</strong>: %s') % \
                str(datetime.timedelta(seconds=self.media_length))
        if not start and not end:
            return ''
        elif start and not end:
            return start
        elif not start and end:
            return end
        else:
            return '%s <br>%s' % (start, end)

    def update_theme(self, theme):
        """
        updates the theme in the service item

        :param theme: The new theme to be replaced in the service item
        """
        self.theme_overwritten = (theme is None)
        self.theme = theme
        self._new_item()
        self.render()

    def remove_invalid_frames(self, invalid_paths=None):
        """
        Remove invalid frames, such as ones where the file no longer exists.
        """
        if self.uses_file():
            for frame in self.get_frames():
                if self.get_frame_path(frame=frame) in invalid_paths:
                    self.remove_frame(frame)

    def missing_frames(self):
        """
        Returns if there are any frames in the service item
        """
        return not bool(self._raw_frames)

    def validate_item(self, suffix_list=None):
        """
        Validates a service item to make sure it is valid
        """
        self.is_valid = True
        for frame in self._raw_frames:
            if self.is_image() and not os.path.exists(frame['path']):
                self.is_valid = False
                break
            elif self.is_command():
                if self.is_capable(ItemCapabilities.IsOptical):
                    if not os.path.exists(frame['title']):
                        self.is_valid = False
                        break
                else:
                    file_name = os.path.join(frame['path'], frame['title'])
                    if not os.path.exists(file_name):
                        self.is_valid = False
                        break
                    if suffix_list and not self.is_text():
                        file_suffix = frame['title'].split('.')[-1]
                        if file_suffix.lower() not in suffix_list:
                            self.is_valid = False
                            break
