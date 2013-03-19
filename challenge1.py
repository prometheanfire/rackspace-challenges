#!/usr/bin/env python
#Copyright 2012 Matthew Thode

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
 Write a script that builds three 512 MB Cloud
 Servers that following a similar naming convention. (ie., web1, web2,
 web3) and returns the IP and login credentials for each server. Use any
 image you want.

 *Worth 1 point*
"""

import pyrax
#import challenges_lib
import argparse
from os.path import expanduser


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Builds servers')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Turn up verbosity to 10')
    parser.add_argument('--veryverbose', action='store_true',
                        help='Turn up verbosity to 11')
    parser.add_argument('--count', '-c', type=int, default=3,
                        help='How many servers you want created')
    parser.add_argument('--name', '-n', required=True,
                        help='The base name for your instances')
    args = parser.parse_args()
    if args.veryverbose:
        args.verbose = True
        print parser.parse_args()
    if args.count < 1:
        print 'invalid number of servers'

    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cs = pyrax.cloudservers
    image = [image for image in cs.images.list()
                if "Gentoo 12.3" in image.name][0]
    flavor = [flavor for flavor in cs.flavors.list()
              if flavor.ram == 512][0]

    for count in xrange(1, args.count + 1):
        server_name = args.name + str(count)
        server = cs.servers.create(server_name, image.id, flavor.id)
        print "Name:", server.name
        print "ID:", server.id
        print "Status:", server.status
        print "Admin Password:", server.adminPass
        print "Networks:", server.networks