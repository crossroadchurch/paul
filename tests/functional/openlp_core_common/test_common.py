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
Functional tests to test the AppLocation class and related methods.
"""

from unittest import TestCase

from openlp.core.common import check_directory_exists, de_hump, trace_error_handler, translate, is_win, is_macosx, \
    is_linux, clean_button_text
from tests.functional import MagicMock, patch


class TestCommonFunctions(TestCase):
    """
    A test suite to test out various functions in the openlp.core.common module.
    """
    def check_directory_exists_test(self):
        """
        Test the check_directory_exists() function
        """
        with patch('openlp.core.lib.os.path.exists') as mocked_exists, \
                patch('openlp.core.lib.os.makedirs') as mocked_makedirs:
            # GIVEN: A directory to check and a mocked out os.makedirs and os.path.exists
            directory_to_check = 'existing/directory'

            # WHEN: os.path.exists returns True and we check to see if the directory exists
            mocked_exists.return_value = True
            check_directory_exists(directory_to_check)

            # THEN: Only os.path.exists should have been called
            mocked_exists.assert_called_with(directory_to_check)
            self.assertIsNot(mocked_makedirs.called, 'os.makedirs should not have been called')

            # WHEN: os.path.exists returns False and we check the directory exists
            mocked_exists.return_value = False
            check_directory_exists(directory_to_check)

            # THEN: Both the mocked functions should have been called
            mocked_exists.assert_called_with(directory_to_check)
            mocked_makedirs.assert_called_with(directory_to_check)

            # WHEN: os.path.exists raises an IOError
            mocked_exists.side_effect = IOError()
            check_directory_exists(directory_to_check)

            # THEN: We shouldn't get an exception though the mocked exists has been called
            mocked_exists.assert_called_with(directory_to_check)

            # WHEN: Some other exception is raised
            mocked_exists.side_effect = ValueError()

            # THEN: check_directory_exists raises an exception
            mocked_exists.assert_called_with(directory_to_check)
            self.assertRaises(ValueError, check_directory_exists, directory_to_check)

    def de_hump_conversion_test(self):
        """
        Test the de_hump function with a class name
        """
        # GIVEN: a Class name in Camel Case
        string = "MyClass"

        # WHEN: we call de_hump
        new_string = de_hump(string)

        # THEN: the new string should be converted to python format
        self.assertTrue(new_string == "my_class", 'The class name should have been converted')

    def de_hump_static_test(self):
        """
        Test the de_hump function with a python string
        """
        # GIVEN: a Class name in Camel Case
        string = "my_class"

        # WHEN: we call de_hump
        new_string = de_hump(string)

        # THEN: the new string should be converted to python format
        self.assertTrue(new_string == "my_class", 'The class name should have been preserved')

    def trace_error_handler_test(self):
        """
        Test the trace_error_handler() method
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.traceback') as mocked_traceback:
            mocked_traceback.extract_stack.return_value = [('openlp.fake', 56, None, 'trace_error_handler_test')]
            mocked_logger = MagicMock()

            # WHEN: trace_error_handler() is called
            trace_error_handler(mocked_logger)

            # THEN: The mocked_logger.error() method should have been called with the correct parameters
            mocked_logger.error.assert_called_with(
                'OpenLP Error trace\n   File openlp.fake at line 56 \n\t called trace_error_handler_test')

    def translate_test(self):
        """
        Test the translate() function
        """
        # GIVEN: A string to translate and a mocked Qt translate function
        context = 'OpenLP.Tests'
        text = 'Untranslated string'
        comment = 'A comment'
        encoding = 1
        n = 1
        mocked_translate = MagicMock(return_value='Translated string')

        # WHEN: we call the translate function
        result = translate(context, text, comment, encoding, n, mocked_translate)

        # THEN: the translated string should be returned, and the mocked function should have been called
        mocked_translate.assert_called_with(context, text, comment, encoding, n)
        self.assertEqual('Translated string', result, 'The translated string should have been returned')

    def is_win_test(self):
        """
        Test the is_win() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'nt' and 'win32' repectivly
            mocked_os.name = 'nt'
            mocked_sys.platform = 'win32'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_win(), 'is_win() should return True')
            self.assertFalse(is_macosx(), 'is_macosx() should return False')
            self.assertFalse(is_linux(), 'is_linux() should return False')

    def is_macosx_test(self):
        """
        Test the is_macosx() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'darwin' repectivly
            mocked_os.name = 'posix'
            mocked_sys.platform = 'darwin'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_macosx(), 'is_macosx() should return True')
            self.assertFalse(is_win(), 'is_win() should return False')
            self.assertFalse(is_linux(), 'is_linux() should return False')

    def is_linux_test(self):
        """
        Test the is_linux() function
        """
        # GIVEN: Mocked out objects
        with patch('openlp.core.common.os') as mocked_os, patch('openlp.core.common.sys') as mocked_sys:

            # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'linux3' repectivly
            mocked_os.name = 'posix'
            mocked_sys.platform = 'linux3'

            # THEN: The three platform functions should perform properly
            self.assertTrue(is_linux(), 'is_linux() should return True')
            self.assertFalse(is_win(), 'is_win() should return False')
            self.assertFalse(is_macosx(), 'is_macosx() should return False')

    def clean_button_text_test(self):
        """
        Test the clean_button_text() function.
        """
        # GIVEN: Button text
        input_text = '&Next >'
        expected_text = 'Next'

        # WHEN: The button caption is sent through the clean_button_text function
        actual_text = clean_button_text(input_text)

        # THEN: The text should have been cleaned
        self.assertEqual(expected_text, actual_text, 'The text should be clean')
