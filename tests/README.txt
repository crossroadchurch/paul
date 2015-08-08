Tests for OpenLP
================

This directory contains unit tests for OpenLP. The ``functional`` directory contains functional unit tests.

Prerequisites
-------------

In order to run the unit tests, you will need the following Python packages/libraries installed:

 - Mock
 - Nose

On Ubuntu you can simple install the python-mock and python-nose packages. Most other distributions will also have these
packages. On Windows and Mac OS X you will need to use ``pip`` or ``easy_install`` to install these packages.

Running the Tests
-----------------

To run the tests, navigate to the root directory of the OpenLP project, and then run the following command::

    nosetests -v tests

Or, to run only the functional tests, run the following command::

    nosetests -v tests/functional

Or, to run only a particular test suite within a file, run the following command::

    nosetests -v tests/functional/test_applocation.py

Finally, to only run a particular test, run the following command::

    nosetests -v tests/functional/test_applocation.py:TestAppLocation.get_frozen_path_test
