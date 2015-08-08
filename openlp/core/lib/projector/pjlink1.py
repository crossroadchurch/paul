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
    :mod:`openlp.core.lib.projector.pjlink1` module
    Provides the necessary functions for connecting to a PJLink-capable projector.

    See PJLink Class 1 Specifications for details.
    http://pjlink.jbmia.or.jp/english/dl.html
        Section 5-1 PJLink Specifications
        Section 5-5 Guidelines for Input Terminals

    NOTE:
      Function names follow  the following syntax:
            def process_CCCC(...):
      WHERE:
            CCCC = PJLink command being processed.
"""

import logging
log = logging.getLogger(__name__)

log.debug('pjlink1 loaded')

__all__ = ['PJLink1']

from codecs import decode

from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtNetwork import QAbstractSocket, QTcpSocket

from openlp.core.common import translate, qmd5_hash
from openlp.core.lib.projector.constants import *

# Shortcuts
SocketError = QAbstractSocket.SocketError
SocketSTate = QAbstractSocket.SocketState

PJLINK_PREFIX = '%'
PJLINK_CLASS = '1'
PJLINK_HEADER = '%s%s' % (PJLINK_PREFIX, PJLINK_CLASS)
PJLINK_SUFFIX = CR


class PJLink1(QTcpSocket):
    """
    Socket service for connecting to a PJLink-capable projector.
    """
    # Signals sent by this module
    changeStatus = pyqtSignal(str, int, str)
    projectorNetwork = pyqtSignal(int)  # Projector network activity
    projectorStatus = pyqtSignal(int)  # Status update
    projectorAuthentication = pyqtSignal(str)  # Authentication error
    projectorNoAuthentication = pyqtSignal(str)  # PIN set and no authentication needed
    projectorReceivedData = pyqtSignal()  # Notify when received data finished processing
    projectorUpdateIcons = pyqtSignal()  # Update the status icons on toolbar

    def __init__(self, name=None, ip=None, port=PJLINK_PORT, pin=None, *args, **kwargs):
        """
        Setup for instance.

        :param name: Display name
        :param ip: IP address to connect to
        :param port: Port to use. Default to PJLINK_PORT
        :param pin: Access pin (if needed)

        Optional parameters
        :param dbid: Database ID number
        :param location: Location where projector is physically located
        :param notes: Extra notes about the projector
        :param poll_time: Time (in seconds) to poll connected projector
        :param socket_timeout: Time (in seconds) to abort the connection if no response
        """
        log.debug('PJlink(args="%s" kwargs="%s")' % (args, kwargs))
        self.name = name
        self.ip = ip
        self.port = port
        self.pin = pin
        super(PJLink1, self).__init__()
        self.dbid = None
        self.location = None
        self.notes = None
        self.dbid = None if 'dbid' not in kwargs else kwargs['dbid']
        self.location = None if 'location' not in kwargs else kwargs['notes']
        self.notes = None if 'notes' not in kwargs else kwargs['notes']
        # Poll time 20 seconds unless called with something else
        self.poll_time = 20000 if 'poll_time' not in kwargs else kwargs['poll_time'] * 1000
        # Timeout 5 seconds unless called with something else
        self.socket_timeout = 5000 if 'socket_timeout' not in kwargs else kwargs['socket_timeout'] * 1000
        # In case we're called from somewhere that only wants information
        self.no_poll = 'no_poll' in kwargs
        self.i_am_running = False
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        # Socket information
        # Add enough space to input buffer for extraneous \n \r
        self.maxSize = PJLINK_MAX_PACKET + 2
        self.setReadBufferSize(self.maxSize)
        # PJLink information
        self.pjlink_class = '1'  # Default class
        self.reset_information()
        # Set from ProjectorManager.add_projector()
        self.widget = None  # QListBox entry
        self.timer = None  # Timer that calls the poll_loop
        self.send_queue = []
        self.send_busy = False
        # Socket timer for some possible brain-dead projectors or network cable pulled
        self.socket_timer = None
        # Map command to function
        self.PJLINK1_FUNC = {'AVMT': self.process_avmt,
                             'CLSS': self.process_clss,
                             'ERST': self.process_erst,
                             'INFO': self.process_info,
                             'INF1': self.process_inf1,
                             'INF2': self.process_inf2,
                             'INPT': self.process_inpt,
                             'INST': self.process_inst,
                             'LAMP': self.process_lamp,
                             'NAME': self.process_name,
                             'PJLINK': self.check_login,
                             'POWR': self.process_powr
                             }

    def reset_information(self):
        """
        Reset projector-specific information to default
        """
        log.debug('(%s) reset_information() connect status is %s' % (self.ip, self.state()))
        self.power = S_OFF
        self.pjlink_name = None
        self.manufacturer = None
        self.model = None
        self.shutter = None
        self.mute = None
        self.lamp = None
        self.fan = None
        self.source_available = None
        self.source = None
        self.other_info = None
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'socket_timer'):
            self.socket_timer.stop()
        self.send_queue = []
        self.send_busy = False

    def thread_started(self):
        """
        Connects signals to methods when thread is started.
        """
        log.debug('(%s) Thread starting' % self.ip)
        self.i_am_running = True
        self.connected.connect(self.check_login)
        self.disconnected.connect(self.disconnect_from_host)
        self.error.connect(self.get_error)

    def thread_stopped(self):
        """
        Cleanups when thread is stopped.
        """
        log.debug('(%s) Thread stopped' % self.ip)
        try:
            self.connected.disconnect(self.check_login)
        except TypeError:
            pass
        try:
            self.disconnected.disconnect(self.disconnect_from_host)
        except TypeError:
            pass
        try:
            self.error.disconnect(self.get_error)
        except TypeError:
            pass
        try:
            self.projectorReceivedData.disconnect(self._send_command)
        except TypeError:
            pass
        self.disconnect_from_host()
        self.deleteLater()
        self.i_am_running = False

    def socket_abort(self):
        """
        Aborts connection and closes socket in case of brain-dead projectors.
        Should normally be called by socket_timer().
        """
        log.debug('(%s) socket_abort() - Killing connection' % self.ip)
        self.disconnect_from_host(abort=True)

    def poll_loop(self):
        """
        Retrieve information from projector that changes.
        Normally called by timer().
        """
        if self.state() != self.ConnectedState:
            return
        log.debug('(%s) Updating projector status' % self.ip)
        # Reset timer in case we were called from a set command
        if self.timer.interval() < self.poll_time:
            # Reset timer to 5 seconds
            self.timer.setInterval(self.poll_time)
        # Restart timer
        self.timer.start()
        # These commands may change during connetion
        for command in ['POWR', 'ERST', 'LAMP', 'AVMT', 'INPT']:
            self.send_command(command, queue=True)
        # The following commands do not change, so only check them once
        if self.power == S_ON and self.source_available is None:
            self.send_command('INST', queue=True)
        if self.other_info is None:
            self.send_command('INFO', queue=True)
        if self.manufacturer is None:
            self.send_command('INF1', queue=True)
        if self.model is None:
            self.send_command('INF2', queue=True)
        if self.pjlink_name is None:
            self.send_command('NAME', queue=True)
        if self.power == S_ON and self.source_available is None:
            self.send_command('INST', queue=True)

    def _get_status(self, status):
        """
        Helper to retrieve status/error codes and convert to strings.

        :param status: Status/Error code
        :returns: (Status/Error code, String)
        """
        if status in ERROR_STRING:
            return ERROR_STRING[status], ERROR_MSG[status]
        elif status in STATUS_STRING:
            return STATUS_STRING[status], ERROR_MSG[status]
        else:
            return status, translate('OpenLP.PJLink1', 'Unknown status')

    def change_status(self, status, msg=None):
        """
        Check connection/error status, set status for projector, then emit status change signal
        for gui to allow changing the icons.

        :param status: Status code
        :param msg: Optional message
        """
        message = translate('OpenLP.PJLink1', 'No message') if msg is None else msg
        (code, message) = self._get_status(status)
        if msg is not None:
            message = msg
        if status in CONNECTION_ERRORS:
            # Projector, connection state
            self.projector_status = self.error_status = self.status_connect = E_NOT_CONNECTED
        elif status >= S_NOT_CONNECTED and status < S_STATUS:
            self.status_connect = status
            self.projector_status = S_NOT_CONNECTED
        elif status < S_NETWORK_SENDING:
            self.status_connect = S_CONNECTED
            self.projector_status = status
        (status_code, status_message) = self._get_status(self.status_connect)
        log.debug('(%s) status_connect: %s: %s' % (self.ip, status_code, status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.projector_status)
        log.debug('(%s) projector_status: %s: %s' % (self.ip, status_code, status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.error_status)
        log.debug('(%s) error_status: %s: %s' % (self.ip, status_code, status_message if msg is None else msg))
        self.changeStatus.emit(self.ip, status, message)

    @pyqtSlot()
    def check_login(self, data=None):
        """
        Processes the initial connection and authentication (if needed).
        Starts poll timer if connection is established.

        :param data: Optional data if called from another routine
        """
        log.debug('(%s) check_login(data="%s")' % (self.ip, data))
        if data is None:
            # Reconnected setup?
            if not self.waitForReadyRead(2000):
                # Possible timeout issue
                log.error('(%s) Socket timeout waiting for login' % self.ip)
                self.change_status(E_SOCKET_TIMEOUT)
                return
            read = self.readLine(self.maxSize)
            dontcare = self.readLine(self.maxSize)  # Clean out the trailing \r\n
            if read is None:
                log.warn('(%s) read is None - socket error?' % self.ip)
                return
            elif len(read) < 8:
                log.warn('(%s) Not enough data read)' % self.ip)
                return
            data = decode(read, 'ascii')
            # Possibility of extraneous data on input when reading.
            # Clean out extraneous characters in buffer.
            dontcare = self.readLine(self.maxSize)
            log.debug('(%s) check_login() read "%s"' % (self.ip, data.strip()))
        # At this point, we should only have the initial login prompt with
        # possible authentication
        # PJLink initial login will be:
        # 'PJLink 0' - Unauthenticated login - no extra steps required.
        # 'PJLink 1 XXXXXX' Authenticated login - extra processing required.
        if not data.upper().startswith('PJLINK'):
            # Invalid response
            return self.disconnect_from_host()
        if '=' in data:
            # Processing a login reply
            data_check = data.strip().split('=')
        else:
            # Process initial connection
            data_check = data.strip().split(' ')
        log.debug('(%s) data_check="%s"' % (self.ip, data_check))
        # Check for projector reporting an error
        if data_check[1].upper() == 'ERRA':
            # Authentication error
            self.disconnect_from_host()
            self.change_status(E_AUTHENTICATION)
            log.debug('(%s) emitting projectorAuthentication() signal' % self.name)
            return
        elif data_check[1] == '0' and self.pin is not None:
            # Pin set and no authentication needed
            self.disconnect_from_host()
            self.change_status(E_AUTHENTICATION)
            log.debug('(%s) emitting projectorNoAuthentication() signal' % self.name)
            self.projectorNoAuthentication.emit(self.name)
            return
        elif data_check[1] == '1':
            # Authenticated login with salt
            log.debug('(%s) Setting hash with salt="%s"' % (self.ip, data_check[2]))
            log.debug('(%s) pin="%s"' % (self.ip, self.pin))
            salt = qmd5_hash(salt=data_check[2].endcode('ascii'), data=self.pin.encode('ascii'))
        else:
            salt = None
        # We're connected at this point, so go ahead and do regular I/O
        self.readyRead.connect(self.get_data)
        self.projectorReceivedData.connect(self._send_command)
        # Initial data we should know about
        self.send_command(cmd='CLSS', salt=salt)
        self.waitForReadyRead()
        if (not self.no_poll) and (self.state() == self.ConnectedState):
            log.debug('(%s) Starting timer' % self.ip)
            self.timer.setInterval(2000)  # Set 2 seconds for initial information
            self.timer.start()

    @pyqtSlot()
    def get_data(self):
        """
        Socket interface to retrieve data.
        """
        log.debug('(%s) get_data(): Reading data' % self.ip)
        if self.state() != self.ConnectedState:
            log.debug('(%s) get_data(): Not connected - returning' % self.ip)
            self.send_busy = False
            return
        read = self.readLine(self.maxSize)
        if read == -1:
            # No data available
            log.debug('(%s) get_data(): No data available (-1)' % self.ip)
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        self.socket_timer.stop()
        self.projectorNetwork.emit(S_NETWORK_RECEIVED)
        data_in = decode(read, 'ascii')
        data = data_in.strip()
        if len(data) < 7:
            # Not enough data for a packet
            log.debug('(%s) get_data(): Packet length < 7: "%s"' % (self.ip, data))
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        log.debug('(%s) get_data(): Checking new data "%s"' % (self.ip, data))
        if data.upper().startswith('PJLINK'):
            # Reconnected from remote host disconnect ?
            self.check_login(data)
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        elif '=' not in data:
            log.warn('(%s) get_data(): Invalid packet received' % self.ip)
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        data_split = data.split('=')
        try:
            (prefix, class_, cmd, data) = (data_split[0][0], data_split[0][1], data_split[0][2:], data_split[1])
        except ValueError as e:
            log.warn('(%s) get_data(): Invalid packet - expected header + command + data' % self.ip)
            log.warn('(%s) get_data(): Received data: "%s"' % (self.ip, read))
            self.change_status(E_INVALID_DATA)
            self.send_busy = False
            self.projectorReceivedData.emit()
            return

        if not (self.pjlink_class in PJLINK_VALID_CMD and cmd in PJLINK_VALID_CMD[self.pjlink_class]):
            log.warn('(%s) get_data(): Invalid packet - unknown command "%s"' % (self.ip, cmd))
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        return self.process_command(cmd, data)

    @pyqtSlot(int)
    def get_error(self, err):
        """
        Process error from SocketError signal.
        Remaps system error codes to projector error codes.

        :param err: Error code
        """
        log.debug('(%s) get_error(err=%s): %s' % (self.ip, err, self.errorString()))
        if err <= 18:
            # QSocket errors. Redefined in projector.constants so we don't mistake
            # them for system errors
            check = err + E_CONNECTION_REFUSED
            self.timer.stop()
        else:
            check = err
        if check < E_GENERAL:
            # Some system error?
            self.change_status(err, self.errorString())
        else:
            self.change_status(E_NETWORK, self.errorString())
        self.projectorUpdateIcons.emit()
        if self.status_connect == E_NOT_CONNECTED:
            self.abort()
            self.reset_information()
        return

    def send_command(self, cmd, opts='?', salt=None, queue=False):
        """
        Add command to output queue if not already in queue.

        :param cmd: Command to send
        :param opts: Command option (if any) - defaults to '?' (get information)
        :param salt: Optional  salt for md5 hash initial authentication
        :param queue: Option to force add to queue rather than sending directly
        """
        if self.state() != self.ConnectedState:
            log.warn('(%s) send_command(): Not connected - returning' % self.ip)
            self.send_queue = []
            return
        self.projectorNetwork.emit(S_NETWORK_SENDING)
        log.debug('(%s) send_command(): Building cmd="%s" opts="%s" %s' % (self.ip,
                                                                           cmd,
                                                                           opts,
                                                                           '' if salt is None else 'with hash'))
        if salt is None:
            out = '%s%s %s%s' % (PJLINK_HEADER, cmd, opts, CR)
        else:
            out = '%s%s%s %s%s' % (salt, PJLINK_HEADER, cmd, opts, CR)
        if out in self.send_queue:
            # Already there, so don't add
            log.debug('(%s) send_command(out="%s") Already in queue - skipping' % (self.ip, out.strip()))
        elif not queue and len(self.send_queue) == 0:
            # Nothing waiting to send, so just send it
            log.debug('(%s) send_command(out="%s") Sending data' % (self.ip, out.strip()))
            return self._send_command(data=out)
        else:
            log.debug('(%s) send_command(out="%s") adding to queue' % (self.ip, out.strip()))
            self.send_queue.append(out)
            self.projectorReceivedData.emit()
        log.debug('(%s) send_command(): send_busy is %s' % (self.ip, self.send_busy))
        if not self.send_busy:
            log.debug('(%s) send_command() calling _send_string()')
            self._send_command()

    @pyqtSlot()
    def _send_command(self, data=None):
        """
        Socket interface to send data. If data=None, then check queue.

        :param data: Immediate data to send
        """
        log.debug('(%s) _send_string()' % self.ip)
        log.debug('(%s) _send_string(): Connection status: %s' % (self.ip, self.state()))
        if self.state() != self.ConnectedState:
            log.debug('(%s) _send_string() Not connected - abort' % self.ip)
            self.send_queue = []
            self.send_busy = False
            return
        if self.send_busy:
            # Still waiting for response from last command sent
            return
        if data is not None:
            out = data
            log.debug('(%s) _send_string(data=%s)' % (self.ip, out.strip()))
        elif len(self.send_queue) != 0:
            out = self.send_queue.pop(0)
            log.debug('(%s) _send_string(queued data=%s)' % (self.ip, out.strip()))
        else:
            # No data to send
            log.debug('(%s) _send_string(): No data to send' % self.ip)
            self.send_busy = False
            return
        self.send_busy = True
        log.debug('(%s) _send_string(): Sending "%s"' % (self.ip, out.strip()))
        log.debug('(%s) _send_string(): Queue = %s' % (self.ip, self.send_queue))
        self.socket_timer.start()
        try:
            self.projectorNetwork.emit(S_NETWORK_SENDING)
            sent = self.write(out)
            self.waitForBytesWritten(2000)  # 2 seconds should be enough
            if sent == -1:
                # Network error?
                self.change_status(E_NETWORK,
                                   translate('OpenLP.PJLink1', 'Error while sending data to projector'))
        except SocketError as e:
            self.disconnect_from_host(abort=True)
            self.changeStatus(E_NETWORK, '%s : %s' % (e.error(), e.errorString()))

    def process_command(self, cmd, data):
        """
        Verifies any return error code. Calls the appropriate command handler.

        :param cmd: Command to process
        :param data: Data being processed
        """
        log.debug('(%s) Processing command "%s"' % (self.ip, cmd))
        if data in PJLINK_ERRORS:
            # Oops - projector error
            if data.upper() == 'ERRA':
                # Authentication error
                self.disconnect_from_host()
                self.change_status(E_AUTHENTICATION)
                log.debug('(%s) emitting projectorAuthentication() signal' % self.ip)
                self.projectorAuthentication.emit(self.name)
            elif data.upper() == 'ERR1':
                # Undefined command
                self.change_status(E_UNDEFINED, '%s "%s"' %
                                   (translate('OpenLP.PJLink1', 'Undefined command:'), cmd))
            elif data.upper() == 'ERR2':
                # Invalid parameter
                self.change_status(E_PARAMETER)
            elif data.upper() == 'ERR3':
                # Projector busy
                self.change_status(E_UNAVAILABLE)
            elif data.upper() == 'ERR4':
                # Projector/display error
                self.change_status(E_PROJECTOR)
            self.send_busy = False
            self.projectorReceivedData.emit()
            return
        # Command succeeded - no extra information
        elif data.upper() == 'OK':
            log.debug('(%s) Command returned OK' % self.ip)
            # A command returned successfully, recheck data
            self.send_busy = False
            self.projectorReceivedData.emit()
            return

        if cmd in self.PJLINK1_FUNC:
            self.PJLINK1_FUNC[cmd](data)
        else:
            log.warn('(%s) Invalid command %s' % (self.ip, cmd))
        self.send_busy = False
        self.projectorReceivedData.emit()

    def process_lamp(self, data):
        """
        Lamp(s) status. See PJLink Specifications for format.
        Data may have more than 1 lamp to process.
        Update self.lamp dictionary with lamp status.

        :param data: Lamp(s) status.
        """
        lamps = []
        data_dict = data.split()
        while data_dict:
            try:
                fill = {'Hours': int(data_dict[0]), 'On': False if data_dict[1] == '0' else True}
            except ValueError:
                # In case of invalid entry
                log.warn('(%s) process_lamp(): Invalid data "%s"' % (self.ip, data))
                return
            lamps.append(fill)
            data_dict.pop(0)  # Remove lamp hours
            data_dict.pop(0)  # Remove lamp on/off
        self.lamp = lamps
        return

    def process_powr(self, data):
        """
        Power status. See PJLink specification for format.
        Update self.power with status. Update icons if change from previous setting.

        :param data: Power status
        """
        if data in PJLINK_POWR_STATUS:
            power = PJLINK_POWR_STATUS[data]
            update_icons = self.power != power
            self.power = power
            self.change_status(PJLINK_POWR_STATUS[data])
            if update_icons:
                self.projectorUpdateIcons.emit()
                # Update the input sources available
                if power == S_ON:
                    self.send_command('INST')
        else:
            # Log unknown status response
            log.warn('Unknown power response: %s' % data)
        return

    def process_avmt(self, data):
        """
        Process shutter and speaker status. See PJLink specification for format.
        Update self.mute (audio) and self.shutter (video shutter).

        :param data: Shutter and audio status
        """
        shutter = self.shutter
        mute = self.mute
        if data == '11':
            shutter = True
            mute = False
        elif data == '21':
            shutter = False
            mute = True
        elif data == '30':
            shutter = False
            mute = False
        elif data == '31':
            shutter = True
            mute = True
        else:
            log.warn('Unknown shutter response: %s' % data)
        update_icons = shutter != self.shutter
        update_icons = update_icons or mute != self.mute
        self.shutter = shutter
        self.mute = mute
        if update_icons:
            self.projectorUpdateIcons.emit()
        return

    def process_inpt(self, data):
        """
        Current source input selected. See PJLink specification for format.
        Update self.source

        :param data: Currently selected source
        """
        self.source = data
        return

    def process_clss(self, data):
        """
        PJLink class that this projector supports. See PJLink specification for format.
        Updates self.class.

        :param data: Class that projector supports.
        """
        self.pjlink_class = data
        log.debug('(%s) Setting pjlink_class for this projector to "%s"' % (self.ip, self.pjlink_class))
        return

    def process_name(self, data):
        """
        Projector name set in projector.
        Updates self.pjlink_name

        :param data: Projector name
        """
        self.pjlink_name = data
        return

    def process_inf1(self, data):
        """
        Manufacturer name set in projector.
        Updates self.manufacturer

        :param data: Projector manufacturer
        """
        self.manufacturer = data
        return

    def process_inf2(self, data):
        """
        Projector Model set in projector.
        Updates self.model.

        :param data: Model name
        """
        self.model = data
        return

    def process_info(self, data):
        """
        Any extra info set in projector.
        Updates self.other_info.

        :param data: Projector other info
        """
        self.other_info = data
        return

    def process_inst(self, data):
        """
        Available source inputs. See PJLink specification for format.
        Updates self.source_available

        :param data: Sources list
        """
        sources = []
        check = data.split()
        for source in check:
            sources.append(source)
        sources.sort()
        self.source_available = sources
        self.projectorUpdateIcons.emit()
        return

    def process_erst(self, data):
        """
        Error status. See PJLink Specifications for format.
        Updates self.projector_errors

        :param data: Error status
        """
        try:
            datacheck = int(data)
        except ValueError:
            # Bad data - ignore
            return
        if datacheck == 0:
            self.projector_errors = None
        else:
            self.projector_errors = {}
            # Fan
            if data[0] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Fan')] = \
                    PJLINK_ERST_STATUS[data[0]]
            # Lamp
            if data[1] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Lamp')] =  \
                    PJLINK_ERST_STATUS[data[1]]
            # Temp
            if data[2] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Temperature')] =  \
                    PJLINK_ERST_STATUS[data[2]]
            # Cover
            if data[3] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Cover')] =  \
                    PJLINK_ERST_STATUS[data[3]]
            # Filter
            if data[4] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Filter')] =  \
                    PJLINK_ERST_STATUS[data[4]]
            # Other
            if data[5] != '0':
                self.projector_errors[translate('OpenLP.ProjectorPJLink', 'Other')] =  \
                    PJLINK_ERST_STATUS[data[5]]
        return

    def connect_to_host(self):
        """
        Initiate connection to projector.
        """
        if self.state() == self.ConnectedState:
            log.warn('(%s) connect_to_host(): Already connected - returning' % self.ip)
            return
        self.change_status(S_CONNECTING)
        self.connectToHost(self.ip, self.port if type(self.port) is int else int(self.port))

    @pyqtSlot()
    def disconnect_from_host(self, abort=False):
        """
        Close socket and cleanup.
        """
        if abort or self.state() != self.ConnectedState:
            if abort:
                log.warn('(%s) disconnect_from_host(): Aborting connection' % self.ip)
            else:
                log.warn('(%s) disconnect_from_host(): Not connected - returning' % self.ip)
            self.reset_information()
        self.disconnectFromHost()
        try:
            self.readyRead.disconnect(self.get_data)
        except TypeError:
            pass
        if abort:
            self.change_status(E_NOT_CONNECTED)
        else:
            log.debug('(%s) disconnect_from_host() Current status %s' % (self.ip,
                                                                         self._get_status(self.status_connect)[0]))
            if self.status_connect != E_NOT_CONNECTED:
                self.change_status(S_NOT_CONNECTED)
        self.reset_information()
        self.projectorUpdateIcons.emit()

    def get_available_inputs(self):
        """
        Send command to retrieve available source inputs.
        """
        return self.send_command(cmd='INST')

    def get_error_status(self):
        """
        Send command to retrieve currently known errors.
        """
        return self.send_command(cmd='ERST')

    def get_input_source(self):
        """
        Send command to retrieve currently selected source input.
        """
        return self.send_command(cmd='INPT')

    def get_lamp_status(self):
        """
        Send command to return the lap status.
        """
        return self.send_command(cmd='LAMP')

    def get_manufacturer(self):
        """
        Send command to retrieve manufacturer name.
        """
        return self.send_command(cmd='INF1')

    def get_model(self):
        """
        Send command to retrieve the model name.
        """
        return self.send_command(cmd='INF2')

    def get_name(self):
        """
        Send command to retrieve name as set by end-user (if set).
        """
        return self.send_command(cmd='NAME')

    def get_other_info(self):
        """
        Send command to retrieve extra info set by manufacturer.
        """
        return self.send_command(cmd='INFO')

    def get_power_status(self):
        """
        Send command to retrieve power status.
        """
        return self.send_command(cmd='POWR')

    def get_shutter_status(self):
        """
        Send command to retrieve shutter status.
        """
        return self.send_command(cmd='AVMT')

    def set_input_source(self, src=None):
        """
        Verify input source available as listed in 'INST' command,
        then send the command to select the input source.

        :param src: Video source to select in projector
        """
        log.debug('(%s) set_input_source(src=%s)' % (self.ip, src))
        if self.source_available is None:
            return
        elif src not in self.source_available:
            return
        log.debug('(%s) Setting input source to %s' % (self.ip, src))
        self.send_command(cmd='INPT', opts=src)
        self.poll_loop()

    def set_power_on(self):
        """
        Send command to turn power to on.
        """
        self.send_command(cmd='POWR', opts='1')
        self.poll_loop()

    def set_power_off(self):
        """
        Send command to turn power to standby.
        """
        self.send_command(cmd='POWR', opts='0')
        self.poll_loop()

    def set_shutter_closed(self):
        """
        Send command to set shutter to closed position.
        """
        self.send_command(cmd='AVMT', opts='11')
        self.poll_loop()

    def set_shutter_open(self):
        """
        Send command to set shutter to open position.
        """
        self.send_command(cmd='AVMT', opts='10')
        self.poll_loop()
