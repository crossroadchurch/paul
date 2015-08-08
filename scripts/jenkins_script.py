#!/usr/bin/env python3
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
This script helps to trigger builds of branches. To use it you have to install the jenkins-webapi package:

    pip3 install jenkins-webapi

You probably want to create an alias. Add this to your ~/.bashrc file and then logout and login (to apply the alias):

    alias ci="python3 ./scripts/jenkins_script.py TOKEN"

You can look up the token in the Branch-01-Pull job configuration or ask in IRC.
"""

import re
import sys
import time
from optparse import OptionParser
from subprocess import Popen, PIPE
import warnings

from requests.exceptions import HTTPError
from jenkins import Jenkins


JENKINS_URL = 'https://ci.openlp.io/'
REPO_REGEX = r'(.*/+)(~.*)'
# Allows us to black list token. So when we change the token, we can display a proper message to the user.
OLD_TOKENS = []

# Disable the InsecureRequestWarning we get from urllib3, because we're not verifying our own self-signed certificate
warnings.simplefilter('ignore')


class OpenLPJobs(object):
    """
    This class holds any jobs we have on jenkins and we actually need in this script.
    """
    Branch_Pull = 'Branch-01-Pull'
    Branch_Functional = 'Branch-02-Functional-Tests'
    Branch_Interface = 'Branch-03-Interface-Tests'
    Branch_Windows_Functional = 'Branch-04a-Windows_Functional_Tests'
    Branch_Windows_Interface = 'Branch-04b-Windows_Interface_Tests'
    Branch_PEP = 'Branch-05a-Code_Analysis'
    Branch_Coverage = 'Branch-05b-Test_Coverage'

    Jobs = [Branch_Pull, Branch_Functional, Branch_Interface, Branch_Windows_Functional, Branch_Windows_Interface,
            Branch_PEP, Branch_Coverage]


class Colour(object):
    """
    This class holds values which can be used to print coloured text.
    """
    RED_START = '\033[1;31m'
    RED_END = '\033[1;m'
    GREEN_START = '\033[1;32m'
    GREEN_END = '\033[1;m'


class JenkinsTrigger(object):
    """
    A class to trigger builds on Jenkins and print the results.

    :param token: The token we need to trigger the build. If you do not have this token, ask in IRC.
    """

    def __init__(self, token):
        """
        Create the JenkinsTrigger instance.
        """
        self.token = token
        self.repo_name = get_repo_name()
        self.jenkins_instance = Jenkins(JENKINS_URL)

    def trigger_build(self):
        """
        Ask our jenkins server to build the "Branch-01-Pull" job.
        """
        bzr = Popen(('bzr', 'whoami'), stdout=PIPE, stderr=PIPE)
        raw_output, error = bzr.communicate()
        # We just want the name (not the email).
        name = ' '.join(raw_output.decode().split()[:-1])
        cause = 'Build triggered by %s (%s)' % (name, self.repo_name)
        self.jenkins_instance.job(OpenLPJobs.Branch_Pull).build({'BRANCH_NAME': self.repo_name, 'cause': cause},
                                                                token=self.token)

    def print_output(self):
        """
        Print the status information of the build triggered.
        """
        print('Add this to your merge proposal:')
        print('--------------------------------')
        bzr = Popen(('bzr', 'revno'), stdout=PIPE, stderr=PIPE)
        raw_output, error = bzr.communicate()
        revno = raw_output.decode().strip()
        print('%s (revision %s)' % (get_repo_name(), revno))

        for job in OpenLPJobs.Jobs:
            if not self.__print_build_info(job):
                print('Stopping after failure')
                break

    def open_browser(self):
        """
        Opens the browser.
        """
        url = self.jenkins_instance.job(OpenLPJobs.Branch_Pull).info['url']
        # Open the url
        Popen(('xdg-open', url), stderr=PIPE)

    def __print_build_info(self, job_name):
        """
        This helper method prints the job information of the given ``job_name``

        :param job_name: The name of the job we want the information from. For example *Branch-01-Pull*. Use the class
         variables from the :class:`OpenLPJobs` class.
        """
        is_success = False
        job = self.jenkins_instance.job(job_name)
        while job.info['inQueue']:
            time.sleep(1)
        build = job.last_build
        build.wait()
        if build.info['result'] == 'SUCCESS':
            # Make 'SUCCESS' green.
            result_string = '%s%s%s' % (Colour.GREEN_START, build.info['result'], Colour.GREEN_END)
            is_success = True
        else:
            # Make 'FAILURE' red.
            result_string = '%s%s%s' % (Colour.RED_START, build.info['result'], Colour.RED_END)
        url = build.info['url']
        print('[%s] %s' % (result_string, url))
        return is_success


def get_repo_name():
    """
    This returns the name of branch of the working directory. For example it returns *lp:~googol/openlp/render*.
    """
    # Run the bzr command.
    bzr = Popen(('bzr', 'info'), stdout=PIPE, stderr=PIPE)
    raw_output, error = bzr.communicate()
    # Detect any errors
    if error:
        print('This is not a branch.')
        return
    # Clean the output.
    raw_output = raw_output.decode()
    output_list = list(map(str.strip, raw_output.split('\n')))
    # Determine the branch's name
    repo_name = ''
    for line in output_list:
        # Check if it is remote branch.
        if 'push branch' in line:
            match = re.match(REPO_REGEX, line)
            if match:
                repo_name = 'lp:%s' % match.group(2)
                break
        elif 'checkout of branch' in line:
            match = re.match(REPO_REGEX, line)
            if match:
                repo_name = 'lp:%s' % match.group(2)
                break
    return repo_name.strip('/')


def main():
    usage = 'Usage: python %prog TOKEN [options]'

    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--disable-output', dest='enable_output', action='store_false', default=True,
                      help='Disable output.')
    parser.add_option('-b', '--open-browser', dest='open_browser', action='store_true', default=False,
                      help='Opens the jenkins page in your browser.')
    options, args = parser.parse_args(sys.argv)

    if len(args) == 2:
        if not get_repo_name():
            print('Not a branch. Have you pushed it to launchpad? Did you cd to the branch?')
            return
        token = args[-1]
        if token in OLD_TOKENS:
            print('Your token is not valid anymore. Get the most recent one.')
            return
        jenkins_trigger = JenkinsTrigger(token)
        try:
            jenkins_trigger.trigger_build()
        except HTTPError:
            print('Wrong token.')
            return
        # Open the browser before printing the output.
        if options.open_browser:
            jenkins_trigger.open_browser()
        if options.enable_output:
            jenkins_trigger.print_output()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
