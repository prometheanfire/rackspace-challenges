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
 Write an application that when passed the arguments FQDN, image, and flavor
 it creates a server of the specified image and flavor with the same name as
 the fqdn, and creates a DNS entry for the fqdn pointing to the server's
 public IP.

 Worth 2 Points
"""


from __future__ import print_function
import pyrax
import argparse
import re
import socket
from os.path import expanduser
from time import sleep


def is_valid_ipv4_address(address):
    """
     Returns true if the address is valid
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
        return True
    except socket.error: # not a valid address
        return False


def is_valid_ipv6_address(address):
    """
     Returns true if the address is valid
    """
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error: # not a valid address
        return False


def is_valid_hostname(hostname):
    """
    Takes a hostname and checks if it is validly formatted
    returns true if formatted correctly
    """
    if len(hostname) > 255:
        return False
    if hostname[-1:] == '.':
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile('(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split('.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Builds servers')
    parser.add_argument('--fqdn', '-n', required=True,
                        help='FQDN of instance to be created')
    parser.add_argument('--image', '-i', required=True,
                        help='Image ID to be built from')
    parser.add_argument('--flavor', '-f', required=True,
                        help='Flavor ID of the instance you wish to build')
    args = parser.parse_args()
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    dns = pyrax.cloud_dns
    cs = pyrax.cloudservers
    images = cs.images.list()
    flavors = cs.flavors.list()

    #checking if values passed in are valid
    image_found = False
    flavor_found = False
    for image in images:
        if image.id == args.image:
            image_found = True
    for flavor in flavors:
        if flavor.id == args.flavor:
            flavor_found = True
    if not is_valid_hostname(args.fqdn):
        print('You need to give me a valid hostname')
        exit()
    if not image_found:
        print('Invalid Image ID given, here is a list of valid Image IDs\n')
        print('               Image ID                   Image Name')
        for image in images:
            print(image.id, '    ', image.name)
        exit()
    if not flavor_found:
        print('Invalid Flavor ID given, here is a list of valid Flavor IDs\n')
        print('ID Name')
        for flavor in flavors:
            print(flavor.id, '', flavor.name)
        exit()

    #creating instance
    server = cs.servers.create(args.fqdn, args.image, args.flavor)
    while not server.networks:
        sleep(5)
        server = cs.servers.get(server.id)

    #pulls the addresses out of the randomly ordered list of addresses...
    server_public_ipv4 = ''
    server_public_ipv6 = ''
    for address in  server.networks['public']:
        if is_valid_ipv4_address(address):
            server_public_ipv4 = address
        if is_valid_ipv6_address(address):
            server_public_ipv6 = address

    #creating dns entry
    dns_dict_list = [{'type': 'A',
                      'name': args.fqdn,
                      'data': server_public_ipv4},
                     {'type': 'AAAA',
                      'name': args.fqdn,
                      'data': server_public_ipv6}]
    dns.create(name=args.fqdn,
               emailAddress='foo@bar.com',
               records=dns_dict_list)