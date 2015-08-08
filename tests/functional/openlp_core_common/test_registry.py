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
Package to test the openlp.core.lib package.
"""
import os
from unittest import TestCase

from openlp.core.common import Registry
from tests.functional import MagicMock

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '..', 'resources'))


class TestRegistry(TestCase):

    def registry_service_test(self):
        """
        Test the registry creation and its usage
        """
        # GIVEN: A new registry
        Registry.create()

        # WHEN: I add a component it should save it
        mock_1 = MagicMock()
        Registry().register('test1', mock_1)

        # THEN: we should be able retrieve the saved component
        assert Registry().get('test1') == mock_1, 'The saved service can be retrieved and matches'

        # WHEN: I add a component for the second time I am mad.
        # THEN  and I will get an exception
        with self.assertRaises(KeyError) as context:
            Registry().register('test1', mock_1)
        self.assertEqual(context.exception.args[0], 'Duplicate service exception test1',
                         'KeyError exception should have been thrown for duplicate service')

        # WHEN I try to get back a non existent component
        # THEN I will get an exception
        temp = Registry().get('test2')
        self.assertEqual(temp, None, 'None should have been returned for missing service')

        # WHEN I try to replace a component I should be allowed (testing only)
        Registry().remove('test1')
        # THEN I will get an exception
        temp = Registry().get('test1')
        self.assertEqual(temp, None, 'None should have been returned for deleted service')

    def registry_function_test(self):
        """
        Test the registry function creation and their usages
        """
        # GIVEN: An existing registry register a function
        Registry.create()
        Registry().register_function('test1', self.dummy_function_1)

        # WHEN: I execute the function
        return_value = Registry().execute('test1')

        # THEN: I expect then function to have been called and a return given
        self.assertEqual(return_value[0], 'function_1', 'A return value is provided and matches')

        # WHEN: I execute the a function with the same reference and execute the function
        Registry().register_function('test1', self.dummy_function_1)
        return_value = Registry().execute('test1')

        # THEN: I expect then function to have been called and a return given
        self.assertEqual(return_value, ['function_1', 'function_1'], 'A return value list is provided and matches')

        # WHEN: I execute the a 2nd function with the different reference and execute the function
        Registry().register_function('test2', self.dummy_function_2)
        return_value = Registry().execute('test2')

        # THEN: I expect then function to have been called and a return given
        self.assertEqual(return_value[0], 'function_2', 'A return value is provided and matches')

    def remove_function_test(self):
        """
        Test the remove_function() method
        """
        # GIVEN: An existing registry register a function
        Registry.create()
        Registry().register_function('test1', self.dummy_function_1)

        # WHEN: Remove the function.
        Registry().remove_function('test1', self.dummy_function_1)

        # THEN: The method should not be available.
        assert not Registry().functions_list['test1'], 'The function should not be in the dict anymore.'

    def dummy_function_1(self):
        return "function_1"

    def dummy_function_2(self):
        return "function_2"
