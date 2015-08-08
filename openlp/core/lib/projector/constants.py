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
    :mod:`openlp.core.lib.projector.constants` module

    Provides the constants used for projector errors/status/defaults
"""

import logging
log = logging.getLogger(__name__)
log.debug('projector_constants loaded')

from openlp.core.common import translate


__all__ = ['S_OK', 'E_GENERAL', 'E_NOT_CONNECTED', 'E_FAN', 'E_LAMP', 'E_TEMP',
           'E_COVER', 'E_FILTER', 'E_AUTHENTICATION', 'E_NO_AUTHENTICATION',
           'E_UNDEFINED', 'E_PARAMETER', 'E_UNAVAILABLE', 'E_PROJECTOR',
           'E_INVALID_DATA', 'E_WARN', 'E_ERROR', 'E_CLASS', 'E_PREFIX',
           'E_CONNECTION_REFUSED', 'E_REMOTE_HOST_CLOSED_CONNECTION', 'E_HOST_NOT_FOUND',
           'E_SOCKET_ACCESS', 'E_SOCKET_RESOURCE', 'E_SOCKET_TIMEOUT', 'E_DATAGRAM_TOO_LARGE',
           'E_NETWORK', 'E_ADDRESS_IN_USE', 'E_SOCKET_ADDRESS_NOT_AVAILABLE',
           'E_UNSUPPORTED_SOCKET_OPERATION', 'E_PROXY_AUTHENTICATION_REQUIRED',
           'E_SLS_HANDSHAKE_FAILED', 'E_UNFINISHED_SOCKET_OPERATION', 'E_PROXY_CONNECTION_REFUSED',
           'E_PROXY_CONNECTION_CLOSED', 'E_PROXY_CONNECTION_TIMEOUT', 'E_PROXY_NOT_FOUND',
           'E_PROXY_PROTOCOL', 'E_UNKNOWN_SOCKET_ERROR',
           'S_NOT_CONNECTED', 'S_CONNECTING', 'S_CONNECTED',
           'S_STATUS', 'S_OFF', 'S_INITIALIZE', 'S_STANDBY', 'S_WARMUP', 'S_ON', 'S_COOLDOWN',
           'S_INFO', 'S_NETWORK_SENDING', 'S_NETWORK_RECEIVED',
           'ERROR_STRING', 'CR', 'LF', 'PJLINK_ERST_STATUS', 'PJLINK_POWR_STATUS',
           'PJLINK_PORT', 'PJLINK_MAX_PACKET', 'TIMEOUT', 'ERROR_MSG', 'PJLINK_ERRORS',
           'STATUS_STRING', 'PJLINK_VALID_CMD', 'CONNECTION_ERRORS']

# Set common constants.
CR = chr(0x0D)  # \r
LF = chr(0x0A)  # \n
PJLINK_PORT = 4352
TIMEOUT = 30.0
PJLINK_MAX_PACKET = 136
PJLINK_VALID_CMD = {'1': ['PJLINK',  # Initial connection
                          'POWR',  # Power option
                          'INPT',  # Video sources option
                          'AVMT',  # Shutter option
                          'ERST',  # Error status option
                          'LAMP',  # Lamp(s) query (Includes fans)
                          'INST',  # Input sources available query
                          'NAME',  # Projector name query
                          'INF1',  # Manufacturer name query
                          'INF2',  # Product name query
                          'INFO',  # Other information query
                          'CLSS'   # PJLink class support query
                          ]}

# Error and status codes
S_OK = E_OK = 0  # E_OK included since I sometimes forget
# Error codes. Start at 200 so we don't duplicate system error codes.
E_GENERAL = 200  # Unknown error
E_NOT_CONNECTED = 201
E_FAN = 202
E_LAMP = 203
E_TEMP = 204
E_COVER = 205
E_FILTER = 206
E_NO_AUTHENTICATION = 207  # PIN set and no authentication set on projector
E_UNDEFINED = 208       # ERR1
E_PARAMETER = 209       # ERR2
E_UNAVAILABLE = 210     # ERR3
E_PROJECTOR = 211       # ERR4
E_INVALID_DATA = 212
E_WARN = 213
E_ERROR = 214
E_AUTHENTICATION = 215  # ERRA
E_CLASS = 216
E_PREFIX = 217

# Remap Qt socket error codes to projector error codes
E_CONNECTION_REFUSED = 230
E_REMOTE_HOST_CLOSED_CONNECTION = 231
E_HOST_NOT_FOUND = 232
E_SOCKET_ACCESS = 233
E_SOCKET_RESOURCE = 234
E_SOCKET_TIMEOUT = 235
E_DATAGRAM_TOO_LARGE = 236
E_NETWORK = 237
E_ADDRESS_IN_USE = 238
E_SOCKET_ADDRESS_NOT_AVAILABLE = 239
E_UNSUPPORTED_SOCKET_OPERATION = 240
E_PROXY_AUTHENTICATION_REQUIRED = 241
E_SLS_HANDSHAKE_FAILED = 242
E_UNFINISHED_SOCKET_OPERATION = 243
E_PROXY_CONNECTION_REFUSED = 244
E_PROXY_CONNECTION_CLOSED = 245
E_PROXY_CONNECTION_TIMEOUT = 246
E_PROXY_NOT_FOUND = 247
E_PROXY_PROTOCOL = 248
E_UNKNOWN_SOCKET_ERROR = -1

# Status codes start at 300
S_NOT_CONNECTED = 300
S_CONNECTING = 301
S_CONNECTED = 302
S_INITIALIZE = 303
S_STATUS = 304
S_OFF = 305
S_STANDBY = 306
S_WARMUP = 307
S_ON = 308
S_COOLDOWN = 309
S_INFO = 310

# Information that does not affect status
S_NETWORK_SENDING = 400
S_NETWORK_RECEIVED = 401

CONNECTION_ERRORS = {E_NOT_CONNECTED, E_NO_AUTHENTICATION, E_AUTHENTICATION, E_CLASS,
                     E_PREFIX, E_CONNECTION_REFUSED, E_REMOTE_HOST_CLOSED_CONNECTION,
                     E_HOST_NOT_FOUND, E_SOCKET_ACCESS, E_SOCKET_RESOURCE, E_SOCKET_TIMEOUT,
                     E_DATAGRAM_TOO_LARGE, E_NETWORK, E_ADDRESS_IN_USE, E_SOCKET_ADDRESS_NOT_AVAILABLE,
                     E_UNSUPPORTED_SOCKET_OPERATION, E_PROXY_AUTHENTICATION_REQUIRED,
                     E_SLS_HANDSHAKE_FAILED, E_UNFINISHED_SOCKET_OPERATION, E_PROXY_CONNECTION_REFUSED,
                     E_PROXY_CONNECTION_CLOSED, E_PROXY_CONNECTION_TIMEOUT, E_PROXY_NOT_FOUND,
                     E_PROXY_PROTOCOL, E_UNKNOWN_SOCKET_ERROR
                     }

PJLINK_ERRORS = {'ERRA': E_AUTHENTICATION,   # Authentication error
                 'ERR1': E_UNDEFINED,        # Undefined command error
                 'ERR2': E_PARAMETER,        # Invalid parameter error
                 'ERR3': E_UNAVAILABLE,      # Projector busy
                 'ERR4': E_PROJECTOR,        # Projector or display failure
                 E_AUTHENTICATION: 'ERRA',
                 E_UNDEFINED: 'ERR1',
                 E_PARAMETER: 'ERR2',
                 E_UNAVAILABLE: 'ERR3',
                 E_PROJECTOR: 'ERR4'}

# Map error/status codes to string
ERROR_STRING = {0: 'S_OK',
                E_GENERAL: 'E_GENERAL',
                E_NOT_CONNECTED: 'E_NOT_CONNECTED',
                E_FAN: 'E_FAN',
                E_LAMP: 'E_LAMP',
                E_TEMP: 'E_TEMP',
                E_COVER: 'E_COVER',
                E_FILTER: 'E_FILTER',
                E_AUTHENTICATION: 'E_AUTHENTICATION',
                E_NO_AUTHENTICATION: 'E_NO_AUTHENTICATION',
                E_UNDEFINED: 'E_UNDEFINED',
                E_PARAMETER: 'E_PARAMETER',
                E_UNAVAILABLE: 'E_UNAVAILABLE',
                E_PROJECTOR: 'E_PROJECTOR',
                E_INVALID_DATA: 'E_INVALID_DATA',
                E_WARN: 'E_WARN',
                E_ERROR: 'E_ERROR',
                E_CLASS: 'E_CLASS',
                E_PREFIX: 'E_PREFIX',  # Last projector error
                E_CONNECTION_REFUSED: 'E_CONNECTION_REFUSED',  # First QtSocket error
                E_REMOTE_HOST_CLOSED_CONNECTION: 'E_REMOTE_HOST_CLOSED_CONNECTION',
                E_HOST_NOT_FOUND: 'E_HOST_NOT_FOUND',
                E_SOCKET_ACCESS: 'E_SOCKET_ACCESS',
                E_SOCKET_RESOURCE: 'E_SOCKET_RESOURCE',
                E_SOCKET_TIMEOUT: 'E_SOCKET_TIMEOUT',
                E_DATAGRAM_TOO_LARGE: 'E_DATAGRAM_TOO_LARGE',
                E_NETWORK: 'E_NETWORK',
                E_ADDRESS_IN_USE: 'E_ADDRESS_IN_USE',
                E_SOCKET_ADDRESS_NOT_AVAILABLE: 'E_SOCKET_ADDRESS_NOT_AVAILABLE',
                E_UNSUPPORTED_SOCKET_OPERATION: 'E_UNSUPPORTED_SOCKET_OPERATION',
                E_PROXY_AUTHENTICATION_REQUIRED: 'E_PROXY_AUTHENTICATION_REQUIRED',
                E_SLS_HANDSHAKE_FAILED: 'E_SLS_HANDSHAKE_FAILED',
                E_UNFINISHED_SOCKET_OPERATION: 'E_UNFINISHED_SOCKET_OPERATION',
                E_PROXY_CONNECTION_REFUSED: 'E_PROXY_CONNECTION_REFUSED',
                E_PROXY_CONNECTION_CLOSED: 'E_PROXY_CONNECTION_CLOSED',
                E_PROXY_CONNECTION_TIMEOUT: 'E_PROXY_CONNECTION_TIMEOUT',
                E_PROXY_NOT_FOUND: 'E_PROXY_NOT_FOUND',
                E_PROXY_PROTOCOL: 'E_PROXY_PROTOCOL',
                E_UNKNOWN_SOCKET_ERROR: 'E_UNKNOWN_SOCKET_ERROR'}

STATUS_STRING = {S_NOT_CONNECTED: 'S_NOT_CONNECTED',
                 S_CONNECTING: 'S_CONNECTING',
                 S_CONNECTED: 'S_CONNECTED',
                 S_STATUS: 'S_STATUS',
                 S_OFF: 'S_OFF',
                 S_INITIALIZE: 'S_INITIALIZE',
                 S_STANDBY: 'S_STANDBY',
                 S_WARMUP: 'S_WARMUP',
                 S_ON: 'S_ON',
                 S_COOLDOWN: 'S_COOLDOWN',
                 S_INFO: 'S_INFO',
                 S_NETWORK_SENDING: 'S_NETWORK_SENDING',
                 S_NETWORK_RECEIVED: 'S_NETWORK_RECEIVED'}

# Map error/status codes to message strings
ERROR_MSG = {E_OK: translate('OpenLP.ProjectorConstants', 'OK'),  # E_OK | S_OK
             E_GENERAL: translate('OpenLP.ProjectorConstants', 'General projector error'),
             E_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Not connected error'),
             E_LAMP: translate('OpenLP.ProjectorConstants', 'Lamp error'),
             E_FAN: translate('OpenLP.ProjectorConstants', 'Fan error'),
             E_TEMP: translate('OpenLP.ProjectorConstants', 'High temperature detected'),
             E_COVER: translate('OpenLP.ProjectorConstants', 'Cover open detected'),
             E_FILTER: translate('OpenLP.ProjectorConstants', 'Check filter'),
             E_AUTHENTICATION: translate('OpenLP.ProjectorConstants', 'Authentication Error'),
             E_UNDEFINED: translate('OpenLP.ProjectorConstants', 'Undefined Command'),
             E_PARAMETER: translate('OpenLP.ProjectorConstants', 'Invalid Parameter'),
             E_UNAVAILABLE: translate('OpenLP.ProjectorConstants', 'Projector Busy'),
             E_PROJECTOR: translate('OpenLP.ProjectorConstants', 'Projector/Display Error'),
             E_INVALID_DATA: translate('OpenLP.ProjectorConstants', 'Invalid packet received'),
             E_WARN: translate('OpenLP.ProjectorConstants', 'Warning condition detected'),
             E_ERROR: translate('OpenLP.ProjectorConstants', 'Error condition detected'),
             E_CLASS: translate('OpenLP.ProjectorConstants', 'PJLink class not supported'),
             E_PREFIX: translate('OpenLP.ProjectorConstants', 'Invalid prefix character'),
             E_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                             'The connection was refused by the peer (or timed out)'),
             E_REMOTE_HOST_CLOSED_CONNECTION: translate('OpenLP.ProjectorConstants',
                                                        'The remote host closed the connection'),
             E_HOST_NOT_FOUND: translate('OpenLP.ProjectorConstants', 'The host address was not found'),
             E_SOCKET_ACCESS: translate('OpenLP.ProjectorConstants',
                                        'The socket operation failed because the application '
                                        'lacked the required privileges'),
             E_SOCKET_RESOURCE: translate('OpenLP.ProjectorConstants',
                                          'The local system ran out of resources (e.g., too many sockets)'),
             E_SOCKET_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                         'The socket operation timed out'),
             E_DATAGRAM_TOO_LARGE: translate('OpenLP.ProjectorConstants',
                                             'The datagram was larger than the operating system\'s limit'),
             E_NETWORK: translate('OpenLP.ProjectorConstants',
                                  'An error occurred with the network (Possibly someone pulled the plug?)'),
             E_ADDRESS_IN_USE: translate('OpenLP.ProjectorConstants',
                                         'The address specified with socket.bind() '
                                         'is already in use and was set to be exclusive'),
             E_SOCKET_ADDRESS_NOT_AVAILABLE: translate('OpenLP.ProjectorConstants',
                                                       'The address specified to socket.bind() '
                                                       'does not belong to the host'),
             E_UNSUPPORTED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                                       'The requested socket operation is not supported by the local '
                                                       'operating system (e.g., lack of IPv6 support)'),
             E_PROXY_AUTHENTICATION_REQUIRED: translate('OpenLP.ProjectorConstants',
                                                        'The socket is using a proxy, '
                                                        'and the proxy requires authentication'),
             E_SLS_HANDSHAKE_FAILED: translate('OpenLP.ProjectorConstants',
                                               'The SSL/TLS handshake failed'),
             E_UNFINISHED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                                      'The last operation attempted has not finished yet '
                                                      '(still in progress in the background)'),
             E_PROXY_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                                   'Could not contact the proxy server because the connection '
                                                   'to that server was denied'),
             E_PROXY_CONNECTION_CLOSED: translate('OpenLP.ProjectorConstants',
                                                  'The connection to the proxy server was closed unexpectedly '
                                                  '(before the connection to the final peer was established)'),
             E_PROXY_CONNECTION_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                                   'The connection to the proxy server timed out or the proxy '
                                                   'server stopped responding in the authentication phase.'),
             E_PROXY_NOT_FOUND: translate('OpenLP.ProjectorConstants',
                                          'The proxy address set with setProxy() was not found'),
             E_PROXY_PROTOCOL: translate('OpenLP.ProjectorConstants',
                                         'The connection negotiation with the proxy server failed because the '
                                         'response from the proxy server could not be understood'),
             E_UNKNOWN_SOCKET_ERROR: translate('OpenLP.ProjectorConstants', 'An unidentified error occurred'),
             S_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Not connected'),
             S_CONNECTING: translate('OpenLP.ProjectorConstants', 'Connecting'),
             S_CONNECTED: translate('OpenLP.ProjectorConstants', 'Connected'),
             S_STATUS: translate('OpenLP.ProjectorConstants', 'Getting status'),
             S_OFF: translate('OpenLP.ProjectorConstants', 'Off'),
             S_INITIALIZE: translate('OpenLP.ProjectorConstants', 'Initialize in progress'),
             S_STANDBY: translate('OpenLP.ProjectorConstants', 'Power in standby'),
             S_WARMUP: translate('OpenLP.ProjectorConstants', 'Warmup in progress'),
             S_ON: translate('OpenLP.ProjectorConstants', 'Power is on'),
             S_COOLDOWN: translate('OpenLP.ProjectorConstants', 'Cooldown in progress'),
             S_INFO: translate('OpenLP.ProjectorConstants', 'Projector Information available'),
             S_NETWORK_SENDING: translate('OpenLP.ProjectorConstants', 'Sending data'),
             S_NETWORK_RECEIVED: translate('OpenLP.ProjectorConstants', 'Received data')}

# Map for ERST return codes to string
PJLINK_ERST_STATUS = {'0': ERROR_STRING[E_OK],
                      '1': ERROR_STRING[E_WARN],
                      '2': ERROR_STRING[E_ERROR]}

# Map for POWR return codes to status code
PJLINK_POWR_STATUS = {'0': S_STANDBY,
                      '1': S_ON,
                      '2': S_COOLDOWN,
                      '3': S_WARMUP}

PJLINK_DEFAULT_SOURCES = {'1': translate('OpenLP.DB', 'RGB'),
                          '2': translate('OpenLP.DB', 'Video'),
                          '3': translate('OpenLP.DB', 'Digital'),
                          '4': translate('OpenLP.DB', 'Storage'),
                          '5': translate('OpenLP.DB', 'Network')}

PJLINK_DEFAULT_CODES = {'11': translate('OpenLP.DB', 'RGB 1'),
                        '12': translate('OpenLP.DB', 'RGB 2'),
                        '13': translate('OpenLP.DB', 'RGB 3'),
                        '14': translate('OpenLP.DB', 'RGB 4'),
                        '15': translate('OpenLP.DB', 'RGB 5'),
                        '16': translate('OpenLP.DB', 'RGB 6'),
                        '17': translate('OpenLP.DB', 'RGB 7'),
                        '18': translate('OpenLP.DB', 'RGB 8'),
                        '19': translate('OpenLP.DB', 'RGB 9'),
                        '21': translate('OpenLP.DB', 'Video 1'),
                        '22': translate('OpenLP.DB', 'Video 2'),
                        '23': translate('OpenLP.DB', 'Video 3'),
                        '24': translate('OpenLP.DB', 'Video 4'),
                        '25': translate('OpenLP.DB', 'Video 5'),
                        '26': translate('OpenLP.DB', 'Video 6'),
                        '27': translate('OpenLP.DB', 'Video 7'),
                        '28': translate('OpenLP.DB', 'Video 8'),
                        '29': translate('OpenLP.DB', 'Video 9'),
                        '31': translate('OpenLP.DB', 'Digital 1'),
                        '32': translate('OpenLP.DB', 'Digital 2'),
                        '33': translate('OpenLP.DB', 'Digital 3'),
                        '34': translate('OpenLP.DB', 'Digital 4'),
                        '35': translate('OpenLP.DB', 'Digital 5'),
                        '36': translate('OpenLP.DB', 'Digital 6'),
                        '37': translate('OpenLP.DB', 'Digital 7'),
                        '38': translate('OpenLP.DB', 'Digital 8'),
                        '39': translate('OpenLP.DB', 'Digital 9'),
                        '41': translate('OpenLP.DB', 'Storage 1'),
                        '42': translate('OpenLP.DB', 'Storage 2'),
                        '43': translate('OpenLP.DB', 'Storage 3'),
                        '44': translate('OpenLP.DB', 'Storage 4'),
                        '45': translate('OpenLP.DB', 'Storage 5'),
                        '46': translate('OpenLP.DB', 'Storage 6'),
                        '47': translate('OpenLP.DB', 'Storage 7'),
                        '48': translate('OpenLP.DB', 'Storage 8'),
                        '49': translate('OpenLP.DB', 'Storage 9'),
                        '51': translate('OpenLP.DB', 'Network 1'),
                        '52': translate('OpenLP.DB', 'Network 2'),
                        '53': translate('OpenLP.DB', 'Network 3'),
                        '54': translate('OpenLP.DB', 'Network 4'),
                        '55': translate('OpenLP.DB', 'Network 5'),
                        '56': translate('OpenLP.DB', 'Network 6'),
                        '57': translate('OpenLP.DB', 'Network 7'),
                        '58': translate('OpenLP.DB', 'Network 8'),
                        '59': translate('OpenLP.DB', 'Network 9')
                        }
