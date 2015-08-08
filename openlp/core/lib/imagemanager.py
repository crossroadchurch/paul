
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
Provides the store and management for Images automatically caching them and resizing them when needed. Only one copy of
each image is needed in the system. A Thread is used to convert the image to a byte array so the user does not need to
wait for the conversion to happen.
"""
import logging
import os
import time
import queue

from PyQt4 import QtCore

from openlp.core.common import Registry
from openlp.core.lib import ScreenList, resize_image, image_to_byte

log = logging.getLogger(__name__)


class ImageThread(QtCore.QThread):
    """
    A special Qt thread class to speed up the display of images. This is threaded so it loads the frames and generates
    byte stream in background.
    """
    def __init__(self, manager):
        """
        Constructor for the thread class.

        ``manager``
            The image manager.
        """
        super(ImageThread, self).__init__(None)
        self.image_manager = manager

    def run(self):
        """
        Run the thread.
        """
        self.image_manager._process()


class Priority(object):
    """
    Enumeration class for different priorities.

    ``Lowest``
        Only the image's byte stream has to be generated. But neither the ``QImage`` nor the byte stream has been
        requested yet.

    ``Low``
        Only the image's byte stream has to be generated. Because the image's ``QImage`` has been requested previously
        it is reasonable to assume that the byte stream will be needed before the byte stream of other images whose
        ``QImage`` were not generated due to a request.

    ``Normal``
        The image's byte stream as well as the image has to be generated. Neither the ``QImage`` nor the byte stream has
        been requested yet.

    ``High``
        The image's byte stream as well as the image has to be generated. The ``QImage`` for this image has been
        requested. **Note**, this priority is only set when the ``QImage`` has not been generated yet.

    ``Urgent``
        The image's byte stream as well as the image has to be generated. The byte stream for this image has been
        requested. **Note**, this priority is only set when the byte stream has not been generated yet.
    """
    Lowest = 4
    Low = 3
    Normal = 2
    High = 1
    Urgent = 0


class Image(object):
    """
    This class represents an image. To mark an image as *dirty* call the :class:`ImageManager`'s ``_reset_image`` method
    with the Image instance as argument.
    """
    secondary_priority = 0

    def __init__(self, path, source, background, width=-1, height=-1):
        """
        Create an image for the :class:`ImageManager`'s cache.

        :param path: The image's file path. This should be an existing file path.
        :param source: The source describes the image's origin. Possible values are described in the
            :class:`~openlp.core.lib.ImageSource` class.
        :param background: A ``QtGui.QColor`` object specifying the colour to be used to fill the gabs if the image's
            ratio does not match with the display ratio.
        :param width: The width of the image, defaults to -1 meaning that the screen width will be used.
        :param height: The height of the image, defaults to -1 meaning that the screen height will be used.
        """
        self.path = path
        self.image = None
        self.image_bytes = None
        self.priority = Priority.Normal
        self.source = source
        self.background = background
        self.timestamp = 0
        self.width = width
        self.height = height
        # FIXME: We assume that the path exist. The caller has to take care that it exists!
        if os.path.exists(path):
            self.timestamp = os.stat(path).st_mtime
        self.secondary_priority = Image.secondary_priority
        Image.secondary_priority += 1


class PriorityQueue(queue.PriorityQueue):
    """
    Customised ``Queue.PriorityQueue``.

    Each item in the queue must be a tuple with three values. The first value is the :class:`Image`'s ``priority``
    attribute, the second value the :class:`Image`'s ``secondary_priority`` attribute. The last value the :class:`Image`
    instance itself::

        (image.priority, image.secondary_priority, image)

    Doing this, the :class:`Queue.PriorityQueue` will sort the images according to their priorities, but also according
    to there number. However, the number only has an impact on the result if there are more images with the same
    priority. In such case the image which has been added earlier is privileged.
    """
    def modify_priority(self, image, new_priority):
        """
        Modifies the priority of the given ``image``.

        :param image: The image to remove. This should be an :class:`Image` instance.
        :param new_priority: The image's new priority. See the :class:`Priority` class for priorities.
        """
        self.remove(image)
        image.priority = new_priority
        self.put((image.priority, image.secondary_priority, image))

    def remove(self, image):
        """
        Removes the given ``image`` from the queue.

        :param image:  The image to remove. This should be an ``Image`` instance.
        """
        if (image.priority, image.secondary_priority, image) in self.queue:
            self.queue.remove((image.priority, image.secondary_priority, image))


class ImageManager(QtCore.QObject):
    """
    Image Manager handles the conversion and sizing of images.
    """
    log.info('Image Manager loaded')

    def __init__(self):
        """
        Constructor for the image manager.
        """
        super(ImageManager, self).__init__()
        Registry().register('image_manager', self)
        current_screen = ScreenList().current
        self.width = current_screen['size'].width()
        self.height = current_screen['size'].height()
        self._cache = {}
        self.image_thread = ImageThread(self)
        self._conversion_queue = PriorityQueue()
        self.stop_manager = False
        Registry().register_function('images_regenerate', self.process_updates)

    def update_display(self):
        """
        Screen has changed size so rebuild the cache to new size.
        """
        log.debug('update_display')
        current_screen = ScreenList().current
        self.width = current_screen['size'].width()
        self.height = current_screen['size'].height()
        # Mark the images as dirty for a rebuild by setting the image and byte stream to None.
        for image in list(self._cache.values()):
            self._reset_image(image)

    def update_images_border(self, source, background):
        """
        Border has changed so update all the images affected.
        """
        log.debug('update_images_border')
        # Mark the images as dirty for a rebuild by setting the image and byte stream to None.
        for image in list(self._cache.values()):
            if image.source == source:
                image.background = background
                self._reset_image(image)

    def update_image_border(self, path, source, background, width=-1, height=-1):
        """
        Border has changed so update the image affected.
        """
        log.debug('update_image_border')
        # Mark the image as dirty for a rebuild by setting the image and byte stream to None.
        image = self._cache[(path, source, width, height)]
        if image.source == source:
            image.background = background
            self._reset_image(image)

    def _reset_image(self, image):
        """
        Mark the given :class:`Image` instance as dirty by setting its ``image`` and ``image_bytes`` attributes to None.
        """
        image.image = None
        image.image_bytes = None
        self._conversion_queue.modify_priority(image, Priority.Normal)

    def process_updates(self):
        """
        Flush the queue to updated any data to update
        """
        # We want only one thread.
        if not self.image_thread.isRunning():
            self.image_thread.start()

    def get_image(self, path, source, width=-1, height=-1):
        """
        Return the ``QImage`` from the cache. If not present wait for the background thread to process it.
        """
        log.debug('getImage %s' % path)
        image = self._cache[(path, source, width, height)]
        if image.image is None:
            self._conversion_queue.modify_priority(image, Priority.High)
            # make sure we are running and if not give it a kick
            self.process_updates()
            while image.image is None:
                log.debug('getImage - waiting')
                time.sleep(0.1)
        elif image.image_bytes is None:
            # Set the priority to Low, because the image was requested but the byte stream was not generated yet.
            # However, we only need to do this, when the image was generated before it was requested (otherwise this is
            # already taken care of).
            self._conversion_queue.modify_priority(image, Priority.Low)
        return image.image

    def get_image_bytes(self, path, source, width=-1, height=-1):
        """
        Returns the byte string for an image. If not present wait for the background thread to process it.
        """
        log.debug('get_image_bytes %s' % path)
        image = self._cache[(path, source, width, height)]
        if image.image_bytes is None:
            self._conversion_queue.modify_priority(image, Priority.Urgent)
            # make sure we are running and if not give it a kick
            self.process_updates()
            while image.image_bytes is None:
                log.debug('getImageBytes - waiting')
                time.sleep(0.1)
        return image.image_bytes

    def add_image(self, path, source, background, width=-1, height=-1):
        """
        Add image to cache if it is not already there.
        """
        log.debug('add_image %s' % path)
        if not (path, source, width, height) in self._cache:
            image = Image(path, source, background, width, height)
            self._cache[(path, source, width, height)] = image
            self._conversion_queue.put((image.priority, image.secondary_priority, image))
        # Check if the there are any images with the same path and check if the timestamp has changed.
        for image in list(self._cache.values()):
            if os.path.exists(path):
                if image.path == path and image.timestamp != os.stat(path).st_mtime:
                    image.timestamp = os.stat(path).st_mtime
                    self._reset_image(image)
        # We want only one thread.
        if not self.image_thread.isRunning():
            self.image_thread.start()

    def _process(self):
        """
        Controls the processing called from a ``QtCore.QThread``.
        """
        log.debug('_process - started')
        while not self._conversion_queue.empty() and not self.stop_manager:
            self._process_cache()
        log.debug('_process - ended')

    def _process_cache(self):
        """
        Actually does the work.
        """
        log.debug('_processCache')
        image = self._conversion_queue.get()[2]
        # Generate the QImage for the image.
        if image.image is None:
            # Let's see if the image was requested with specific dimensions
            width = self.width if image.width == -1 else image.width
            height = self.height if image.height == -1 else image.height
            image.image = resize_image(image.path, width, height, image.background)
            # Set the priority to Lowest and stop here as we need to process more important images first.
            if image.priority == Priority.Normal:
                self._conversion_queue.modify_priority(image, Priority.Lowest)
                return
            # For image with high priority we set the priority to Low, as the byte stream might be needed earlier the
            # byte stream of image with Normal priority. We stop here as we need to process more important images first.
            elif image.priority == Priority.High:
                self._conversion_queue.modify_priority(image, Priority.Low)
                return
        # Generate the byte stream for the image.
        if image.image_bytes is None:
            image.image_bytes = image_to_byte(image.image)
