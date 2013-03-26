#!/usr/bin/env python
#Copyright 2013 Matthew Thode

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


"""
 Write a script that accepts a directory as an
 argument as well as a container name. The script should upload the
 contents of the specified directory to the container (or create it if it
 doesn't exist). The script should handle errors appropriately. (Check
 for invalid paths, etc.)
 *Worth 2 Points*
"""


import pyrax
from os.path import expanduser
from os import path
import argparse



if __name__ == '__main__':
    #initialize pyrax and create variables
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    parser = argparse.ArgumentParser(description='Command line options')
    parser.add_argument('--container', '-c',
                        help='Selects container to upload to ' +
                             'instead of multiple containers at an endpoint)')
    parser.add_argument('--dir', '-d', required=True,
                        help='The source directory you wish to sync')
    args = parser.parse_args()

    if not path.isdir(args.dir):
        print 'You gave me a bad directory to sync'
        exit()

    cf = pyrax.cloudfiles
    if args.container not in cf.list_containers():
        cf.create_container(args.container)
    cf.sync_folder_to_container(args.dir, args.container, include_hidden=True)