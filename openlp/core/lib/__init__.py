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
The :mod:`lib` module contains most of the components and libraries that make
OpenLP work.
"""

from distutils.version import LooseVersion
import logging
import os

from PyQt4 import QtCore, QtGui, Qt

from openlp.core.common import translate

log = logging.getLogger(__name__ + '.__init__')


class ServiceItemContext(object):
    """
    The context in which a Service Item is being generated
    """
    Preview = 0
    Live = 1
    Service = 2


class ImageSource(object):
    """
    This enumeration class represents different image sources. An image sources states where an image is used. This
    enumeration class is need in the context of the :class:~openlp.core.lib.imagemanager`.

    ``ImagePlugin``
        This states that an image is being used by the image plugin.

    ``Theme``
        This says, that the image is used by a theme.
    """
    ImagePlugin = 1
    Theme = 2


class MediaType(object):
    """
    An enumeration class for types of media.
    """
    Audio = 1
    Video = 2


class ServiceItemAction(object):
    """
    Provides an enumeration for the required action moving between service items by left/right arrow keys
    """
    Previous = 1
    PreviousLastSlide = 2
    Next = 3


def get_text_file_string(text_file):
    """
    Open a file and return its content as unicode string. If the supplied file name is not a file then the function
    returns False. If there is an error loading the file or the content can't be decoded then the function will return
    None.

    :param text_file: The name of the file.
    :return The file as a single string
    """
    if not os.path.isfile(text_file):
        return False
    file_handle = None
    content = None
    try:
        file_handle = open(text_file, 'r', encoding='utf-8')
        if not file_handle.read(3) == '\xEF\xBB\xBF':
            # no BOM was found
            file_handle.seek(0)
        content = file_handle.read()
    except (IOError, UnicodeError):
        log.exception('Failed to open text file %s' % text_file)
    finally:
        if file_handle:
            file_handle.close()
    return content


def str_to_bool(string_value):
    """
    Convert a string version of a boolean into a real boolean.

    :param string_value: The string value to examine and convert to a boolean type.
    :return The correct boolean value
    """
    if isinstance(string_value, bool):
        return string_value
    return str(string_value).strip().lower() in ('true', 'yes', 'y')


def build_icon(icon):
    """
    Build a QIcon instance from an existing QIcon, a resource location, or a physical file location. If the icon is a
    QIcon instance, that icon is simply returned. If not, it builds a QIcon instance from the resource or file name.

    :param icon:
        The icon to build. This can be a QIcon, a resource string in the form ``:/resource/file.png``, or a file
        location like ``/path/to/file.png``. However, the **recommended** way is to specify a resource string.
    :return The build icon.
    """
    button_icon = QtGui.QIcon()
    if isinstance(icon, QtGui.QIcon):
        button_icon = icon
    elif isinstance(icon, str):
        if icon.startswith(':/'):
            button_icon.addPixmap(QtGui.QPixmap(icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            button_icon.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(icon)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    elif isinstance(icon, QtGui.QImage):
        button_icon.addPixmap(QtGui.QPixmap.fromImage(icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return button_icon


def image_to_byte(image, base_64=True):
    """
    Resize an image to fit on the current screen for the web and returns it as a byte stream.

    :param image: The image to converted.
    :param base_64: If True returns the image as Base64 bytes, otherwise the image is returned as a byte array.
        To preserve original intention, this defaults to True
    """
    log.debug('image_to_byte - start')
    byte_array = QtCore.QByteArray()
    # use buffer to store pixmap into byteArray
    buffie = QtCore.QBuffer(byte_array)
    buffie.open(QtCore.QIODevice.WriteOnly)
    image.save(buffie, "PNG")
    log.debug('image_to_byte - end')
    if not base_64:
        return byte_array
    # convert to base64 encoding so does not get missed!
    return bytes(byte_array.toBase64()).decode('utf-8')


def create_thumb(image_path, thumb_path, return_icon=True, size=None):
    """
    Create a thumbnail from the given image path and depending on ``return_icon`` it returns an icon from this thumb.

    :param image_path: The image file to create the icon from.
    :param thumb_path: The filename to save the thumbnail to.
    :param return_icon: States if an icon should be build and returned from the thumb. Defaults to ``True``.
    :param size: Allows to state a own size (QtCore.QSize) to use. Defaults to ``None``, which means that a default
     height of 88 is used.
    :return The final icon.
    """
    ext = os.path.splitext(thumb_path)[1].lower()
    reader = QtGui.QImageReader(image_path)
    if size is None:
        ratio = reader.size().width() / reader.size().height()
        reader.setScaledSize(QtCore.QSize(int(ratio * 88), 88))
    else:
        reader.setScaledSize(size)
    thumb = reader.read()
    thumb.save(thumb_path, ext[1:])
    if not return_icon:
        return
    if os.path.exists(thumb_path):
        return build_icon(thumb_path)
    # Fallback for files with animation support.
    return build_icon(image_path)


def validate_thumb(file_path, thumb_path):
    """
    Validates whether an file's thumb still exists and if is up to date. **Note**, you must **not** call this function,
    before checking the existence of the file.

    :param file_path: The path to the file. The file **must** exist!
    :param thumb_path: The path to the thumb.
    :return True, False if the image has changed since the thumb was created.
    """
    if not os.path.exists(thumb_path):
        return False
    image_date = os.stat(file_path).st_mtime
    thumb_date = os.stat(thumb_path).st_mtime
    return image_date <= thumb_date


def resize_image(image_path, width, height, background='#000000'):
    """
    Resize an image to fit on the current screen.

    DO NOT REMOVE THE DEFAULT BACKGROUND VALUE!

    :param image_path: The path to the image to resize.
    :param width: The new image width.
    :param height: The new image height.
    :param background: The background colour. Defaults to black.
    """
    log.debug('resize_image - start')
    reader = QtGui.QImageReader(image_path)
    # The image's ratio.
    image_ratio = reader.size().width() / reader.size().height()
    resize_ratio = width / height
    # Figure out the size we want to resize the image to (keep aspect ratio).
    if image_ratio == resize_ratio:
        size = QtCore.QSize(width, height)
    elif image_ratio < resize_ratio:
        # Use the image's height as reference for the new size.
        size = QtCore.QSize(image_ratio * height, height)
    else:
        # Use the image's width as reference for the new size.
        size = QtCore.QSize(width, 1 / (image_ratio / width))
    reader.setScaledSize(size)
    preview = reader.read()
    if image_ratio == resize_ratio:
        # We neither need to centre the image nor add "bars" to the image.
        return preview
    real_width = preview.width()
    real_height = preview.height()
    # and move it to the centre of the preview space
    new_image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
    painter = QtGui.QPainter(new_image)
    painter.fillRect(new_image.rect(), QtGui.QColor(background))
    painter.drawImage((width - real_width) // 2, (height - real_height) // 2, preview)
    return new_image


def check_item_selected(list_widget, message):
    """
    Check if a list item is selected so an action may be performed on it

    :param list_widget: The list to check for selected items
    :param message: The message to give the user if no item is selected
    """
    if not list_widget.selectedIndexes():
        QtGui.QMessageBox.information(list_widget.parent(),
                                      translate('OpenLP.MediaManagerItem', 'No Items Selected'), message)
        return False
    return True


def clean_tags(text):
    """
    Remove Tags from text for display

    :param text: Text to be cleaned
    """
    text = text.replace('<br>', '\n')
    text = text.replace('{br}', '\n')
    text = text.replace('&nbsp;', ' ')
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], '')
        text = text.replace(tag['end tag'], '')
    return text


def expand_tags(text):
    """
    Expand tags HTML for display

    :param text: The text to be expanded.
    """
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], tag['start html'])
        text = text.replace(tag['end tag'], tag['end html'])
    return text


def create_separated_list(string_list):
    """
    Returns a string that represents a join of a list of strings with a localized separator. This function corresponds

    to QLocale::createSeparatedList which was introduced in Qt 4.8 and implements the algorithm from
    http://www.unicode.org/reports/tr35/#ListPatterns

     :param string_list: List of unicode strings
    """
    if LooseVersion(Qt.PYQT_VERSION_STR) >= LooseVersion('4.9') and LooseVersion(Qt.qVersion()) >= LooseVersion('4.8'):
        return QtCore.QLocale().createSeparatedList(string_list)
    if not string_list:
        return ''
    elif len(string_list) == 1:
        return string_list[0]
    elif len(string_list) == 2:
        return translate('OpenLP.core.lib', '%s and %s',
                         'Locale list separator: 2 items') % (string_list[0], string_list[1])
    else:
        merged = translate('OpenLP.core.lib', '%s, and %s',
                           'Locale list separator: end') % (string_list[-2], string_list[-1])
        for index in reversed(list(range(1, len(string_list) - 2))):
            merged = translate('OpenLP.core.lib', '%s, %s',
                               'Locale list separator: middle') % (string_list[index], merged)
        return translate('OpenLP.core.lib', '%s, %s', 'Locale list separator: start') % (string_list[0], merged)


from .colorbutton import ColorButton
from .exceptions import ValidationError
from .filedialog import FileDialog
from .screen import ScreenList
from .listwidgetwithdnd import ListWidgetWithDnD
from .treewidgetwithdnd import TreeWidgetWithDnD
from .formattingtags import FormattingTags
from .spelltextedit import SpellTextEdit
from .plugin import PluginStatus, StringContent, Plugin
from .pluginmanager import PluginManager
from .settingstab import SettingsTab
from .serviceitem import ServiceItem, ServiceItemType, ItemCapabilities
from .htmlbuilder import build_html, build_lyrics_format_css, build_lyrics_outline_css
from .toolbar import OpenLPToolbar
from .dockwidget import OpenLPDockWidget
from .imagemanager import ImageManager
from .renderer import Renderer
from .mediamanageritem import MediaManagerItem
from .projector.db import ProjectorDB, Projector
from .projector.pjlink1 import PJLink1
from .projector.constants import PJLINK_PORT, ERROR_MSG, ERROR_STRING
