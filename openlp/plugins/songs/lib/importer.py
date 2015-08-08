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
The :mod:`importer` modules provides the general song import functionality.
"""
import os
import logging

from openlp.core.common import translate, UiStrings, is_win
from openlp.core.ui.wizard import WizardStrings
from .importers.opensong import OpenSongImport
from .importers.easyslides import EasySlidesImport
from .importers.openlp import OpenLPSongImport
from .importers.openlyrics import OpenLyricsImport
from .importers.wordsofworship import WordsOfWorshipImport
from .importers.cclifile import CCLIFileImport
from .importers.dreambeam import DreamBeamImport
from .importers.powersong import PowerSongImport
from .importers.easyworship import EasyWorshipSongImport
from .importers.songbeamer import SongBeamerImport
from .importers.songshowplus import SongShowPlusImport
from .importers.songpro import SongProImport
from .importers.sundayplus import SundayPlusImport
from .importers.foilpresenter import FoilPresenterImport
from .importers.zionworx import ZionWorxImport
from .importers.propresenter import ProPresenterImport
from .importers.worshipassistant import WorshipAssistantImport
from .importers.powerpraise import PowerPraiseImport
from .importers.presentationmanager import PresentationManagerImport

log = logging.getLogger(__name__)

# Imports that might fail
try:
    from .importers.songsoffellowship import SongsOfFellowshipImport
    HAS_SOF = True
except ImportError:
    log.exception('Error importing %s', 'SongsOfFellowshipImport')
    HAS_SOF = False
try:
    from .importers.openoffice import OpenOfficeImport
    HAS_OOO = True
except ImportError:
    log.exception('Error importing %s', 'OooImport')
    HAS_OOO = False
HAS_MEDIASHOUT = False
if is_win():
    try:
        from .importers.mediashout import MediaShoutImport
        HAS_MEDIASHOUT = True
    except ImportError:
        log.exception('Error importing %s', 'MediaShoutImport')
HAS_WORSHIPCENTERPRO = False
if is_win():
    try:
        from .importers.worshipcenterpro import WorshipCenterProImport
        HAS_WORSHIPCENTERPRO = True
    except ImportError:
        log.exception('Error importing %s', 'WorshipCenterProImport')


class SongFormatSelect(object):
    """
    This is a special enumeration class listing available file selection modes.
    """
    SingleFile = 0
    MultipleFiles = 1
    SingleFolder = 2


class SongFormat(object):
    """
    This is a special static class that holds an enumeration of the various
    song formats handled by the importer, the attributes of each song format,
    and a few helper functions.

    Required attributes for each song format:

    ``'class'``
        Import class, e.g. ``OpenLyricsImport``

    ``'name'``
        Name of the format, e.g. ``'OpenLyrics'``

    ``'prefix'``
        Prefix for Qt objects. Use mixedCase, e.g. ``'openLyrics'``
        See ``SongImportForm.add_file_select_item()``

    Optional attributes for each song format:

    ``'canDisable'``
        Whether song format importer is disablable.
        If ``True``, then ``'disabledLabelText'`` must also be defined.

    ``'availability'``
        Whether song format importer is available.

    ``'selectMode'``
        Whether format accepts single file, multiple files, or single folder
        (as per ``SongFormatSelect`` options).

    ``'filter'``
        File extension filter for ``QFileDialog``.

    Optional/custom text Strings for ``SongImportForm`` widgets:

    ``'comboBoxText'``
        Combo box selector (default value is the format's ``'name'``).

    ``'disabledLabelText'``
        Required for disablable song formats.

    ``'getFilesTitle'``
        Title for ``QFileDialog`` (default includes the format's ``'name'``).

    ``'invalidSourceMsg'``
        Message displayed if ``is_valid_source()`` returns ``False``.

    ``'descriptionText'``
        Short description (1-2 lines) about the song format.
    """
    # Song formats (ordered alphabetically after Generic)
    # * Numerical order of song formats is significant as it determines the
    #   order used by format_combo_box.
    Unknown = -1
    OpenLyrics = 0
    OpenLP2 = 1
    Generic = 2
    CCLI = 3
    DreamBeam = 4
    EasySlides = 5
    EasyWorshipDB = 6
    EasyWorshipService = 7
    FoilPresenter = 8
    MediaShout = 9
    OpenSong = 10
    PowerPraise = 11
    PowerSong = 12
    PresentationManager = 13
    ProPresenter = 14
    SongBeamer = 15
    SongPro = 16
    SongShowPlus = 17
    SongsOfFellowship = 18
    SundayPlus = 19
    WordsOfWorship = 20
    WorshipAssistant = 21
    WorshipCenterPro = 22
    ZionWorx = 23

    # Set optional attribute defaults
    __defaults__ = {
        'canDisable': False,
        'availability': True,
        'selectMode': SongFormatSelect.MultipleFiles,
        'filter': '',
        'comboBoxText': None,
        'disabledLabelText': translate('SongsPlugin.ImportWizardForm', 'This importer has been disabled.'),
        'getFilesTitle': None,
        'invalidSourceMsg': None,
        'descriptionText': None
    }

    # Set attribute values for each Song Format
    __attributes__ = {
        OpenLyrics: {
            'class': OpenLyricsImport,
            'name': 'OpenLyrics',
            'prefix': 'openLyrics',
            'filter': '%s (*.xml)' % translate('SongsPlugin.ImportWizardForm', 'OpenLyrics Files'),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'OpenLyrics or OpenLP 2.0 Exported Song')
        },
        OpenLP2: {
            'class': OpenLPSongImport,
            'name': UiStrings().OLPV2,
            'prefix': 'openLP2',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.sqlite)' % (translate('SongsPlugin.ImportWizardForm', 'OpenLP 2.0 Databases'))
        },
        Generic: {
            'name': translate('SongsPlugin.ImportWizardForm', 'Generic Document/Presentation'),
            'prefix': 'generic',
            'canDisable': True,
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The generic document/presentation importer has been disabled '
                                           'because OpenLP cannot access OpenOffice or LibreOffice.'),
            'getFilesTitle': translate('SongsPlugin.ImportWizardForm', 'Select Document/Presentation Files')
        },
        CCLI: {
            'class': CCLIFileImport,
            'name': 'CCLI/SongSelect',
            'prefix': 'ccli',
            'filter': '%s (*.usr *.txt *.bin)' % translate('SongsPlugin.ImportWizardForm', 'CCLI SongSelect Files')
        },
        DreamBeam: {
            'class': DreamBeamImport,
            'name': 'DreamBeam',
            'prefix': 'dreamBeam',
            'filter': '%s (*.xml)' % translate('SongsPlugin.ImportWizardForm', 'DreamBeam Song Files')
        },
        EasySlides: {
            'class': EasySlidesImport,
            'name': 'EasySlides',
            'prefix': 'easySlides',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.xml)' % translate('SongsPlugin.ImportWizardForm', 'EasySlides XML File')
        },
        EasyWorshipDB: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship Song Database',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.db)' % translate('SongsPlugin.ImportWizardForm', 'EasyWorship Song Database')
        },
        EasyWorshipService: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship Service File',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.ews)' % translate('SongsPlugin.ImportWizardForm', 'EasyWorship Service File')
        },
        FoilPresenter: {
            'class': FoilPresenterImport,
            'name': 'Foilpresenter',
            'prefix': 'foilPresenter',
            'filter': '%s (*.foil)' % translate('SongsPlugin.ImportWizardForm', 'Foilpresenter Song Files')
        },
        MediaShout: {
            'name': 'MediaShout',
            'prefix': 'mediaShout',
            'canDisable': True,
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.mdb)' % translate('SongsPlugin.ImportWizardForm', 'MediaShout Database'),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The MediaShout importer is only supported on Windows. It has '
                                           'been disabled due to a missing Python module. If you want to '
                                           'use this importer, you will need to install the "pyodbc" '
                                           'module.')
        },
        OpenSong: {
            'class': OpenSongImport,
            'name': WizardStrings.OS,
            'prefix': 'openSong'
        },
        PowerPraise: {
            'class': PowerPraiseImport,
            'name': 'PowerPraise',
            'prefix': 'powerPraise',
            'filter': '%s (*.ppl)' % translate('SongsPlugin.ImportWizardForm', 'PowerPraise Song Files')
        },
        PowerSong: {
            'class': PowerSongImport,
            'name': 'PowerSong 1.0',
            'prefix': 'powerSong',
            'selectMode': SongFormatSelect.SingleFolder,
            'invalidSourceMsg': translate('SongsPlugin.ImportWizardForm', 'You need to specify a valid PowerSong 1.0 '
                                                                          'database folder.')
        },
        PresentationManager: {
            'class': PresentationManagerImport,
            'name': 'PresentationManager',
            'prefix': 'presentationManager',
            'filter': '%s (*.sng)' % translate('SongsPlugin.ImportWizardForm', 'PresentationManager Song Files')
        },
        ProPresenter: {
            'class': ProPresenterImport,
            'name': 'ProPresenter 4',
            'prefix': 'proPresenter',
            'filter': '%s (*.pro4)' % translate('SongsPlugin.ImportWizardForm', 'ProPresenter 4 Song Files')
        },
        SongBeamer: {
            'class': SongBeamerImport,
            'name': 'SongBeamer',
            'prefix': 'songBeamer',
            'filter': '%s (*.sng)' % translate('SongsPlugin.ImportWizardForm', 'SongBeamer Files')
        },
        SongPro: {
            'class': SongProImport,
            'name': 'SongPro',
            'prefix': 'songPro',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.txt)' % translate('SongsPlugin.ImportWizardForm', 'SongPro Text Files'),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'SongPro (Export File)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'In SongPro, export your songs using the File -> Export menu')
        },
        SongShowPlus: {
            'class': SongShowPlusImport,
            'name': 'SongShow Plus',
            'prefix': 'songShowPlus',
            'filter': '%s (*.sbsong)' % translate('SongsPlugin.ImportWizardForm', 'SongShow Plus Song Files')
        },
        SongsOfFellowship: {
            'name': 'Songs of Fellowship',
            'prefix': 'songsOfFellowship',
            'canDisable': True,
            'filter': '%s (*.rtf)' % translate('SongsPlugin.ImportWizardForm', 'Songs Of Fellowship Song Files'),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The Songs of Fellowship importer has been disabled because '
                                           'OpenLP cannot access OpenOffice or LibreOffice.')
        },
        SundayPlus: {
            'class': SundayPlusImport,
            'name': 'SundayPlus',
            'prefix': 'sundayPlus',
            'filter': '%s (*.ptf)' % translate('SongsPlugin.ImportWizardForm', 'SundayPlus Song Files')
        },
        WordsOfWorship: {
            'class': WordsOfWorshipImport,
            'name': 'Words of Worship',
            'prefix': 'wordsOfWorship',
            'filter': '%s (*.wsg *.wow-song)' % translate('SongsPlugin.ImportWizardForm', 'Words Of Worship Song Files')
        },
        WorshipAssistant: {
            'class': WorshipAssistantImport,
            'name': 'Worship Assistant 0',
            'prefix': 'worshipAssistant',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.csv)' % translate('SongsPlugin.ImportWizardForm', 'Worship Assistant Files'),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'Worship Assistant (CSV)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'In Worship Assistant, export your Database to a CSV file.')
        },
        WorshipCenterPro: {
            'name': 'WorshipCenter Pro',
            'prefix': 'worshipCenterPro',
            'canDisable': True,
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '%s (*.mdb)' % translate('SongsPlugin.ImportWizardForm', 'WorshipCenter Pro Song Files'),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The WorshipCenter Pro importer is only supported on Windows. It has been '
                                           'disabled due to a missing Python module. If you want to use this '
                                           'importer, you will need to install the "pyodbc" module.')
        },
        ZionWorx: {
            'class': ZionWorxImport,
            'name': 'ZionWorx',
            'prefix': 'zionWorx',
            'selectMode': SongFormatSelect.SingleFile,
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'ZionWorx (CSV)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'First convert your ZionWorx database to a CSV text file, as '
                                         'explained in the <a href="http://manual.openlp.org/songs.html'
                                         '#importing-from-zionworx">User Manual</a>.')
        }
    }

    @staticmethod
    def get_format_list():
        """
        Return a list of the supported song formats.
        """
        return [
            SongFormat.OpenLyrics,
            SongFormat.OpenLP2,
            SongFormat.Generic,
            SongFormat.CCLI,
            SongFormat.DreamBeam,
            SongFormat.EasySlides,
            SongFormat.EasyWorshipDB,
            SongFormat.EasyWorshipService,
            SongFormat.FoilPresenter,
            SongFormat.MediaShout,
            SongFormat.OpenSong,
            SongFormat.PowerPraise,
            SongFormat.PowerSong,
            SongFormat.PresentationManager,
            SongFormat.ProPresenter,
            SongFormat.SongBeamer,
            SongFormat.SongPro,
            SongFormat.SongShowPlus,
            SongFormat.SongsOfFellowship,
            SongFormat.SundayPlus,
            SongFormat.WordsOfWorship,
            SongFormat.WorshipAssistant,
            SongFormat.WorshipCenterPro,
            SongFormat.ZionWorx
        ]

    @staticmethod
    def get(song_format, *attributes):
        """
        Return requested song format attribute(s).

        :param song_format: A song format from SongFormat.
        :param attributes: Zero or more song format attributes from SongFormat.

        Return type depends on number of supplied attributes:

        :0: Return dict containing all defined attributes for the format.
        :1: Return the attribute value.
        :>1: Return tuple of requested attribute values.
        """
        if not attributes:
            return SongFormat.__attributes__.get(song_format)
        elif len(attributes) == 1:
            default = SongFormat.__defaults__.get(attributes[0])
            return SongFormat.__attributes__[song_format].get(attributes[0], default)
        else:
            values = []
            for attr in attributes:
                default = SongFormat.__defaults__.get(attr)
                values.append(SongFormat.__attributes__[song_format].get(attr, default))
            return tuple(values)

    @staticmethod
    def set(song_format, attribute, value):
        """
        Set specified song format attribute to the supplied value.
        """
        SongFormat.__attributes__[song_format][attribute] = value


SongFormat.set(SongFormat.SongsOfFellowship, 'availability', HAS_SOF)
if HAS_SOF:
    SongFormat.set(SongFormat.SongsOfFellowship, 'class', SongsOfFellowshipImport)
SongFormat.set(SongFormat.Generic, 'availability', HAS_OOO)
if HAS_OOO:
    SongFormat.set(SongFormat.Generic, 'class', OpenOfficeImport)
SongFormat.set(SongFormat.MediaShout, 'availability', HAS_MEDIASHOUT)
if HAS_MEDIASHOUT:
    SongFormat.set(SongFormat.MediaShout, 'class', MediaShoutImport)
SongFormat.set(SongFormat.WorshipCenterPro, 'availability', HAS_WORSHIPCENTERPRO)
if HAS_WORSHIPCENTERPRO:
    SongFormat.set(SongFormat.WorshipCenterPro, 'class', WorshipCenterProImport)


__all__ = ['SongFormat', 'SongFormatSelect']
