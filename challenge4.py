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
 Write a script that uses Cloud DNS to create a
 new A record when passed a FQDN and IP address as arguments.
 *Worth 1 Point*
"""


from __future__ import print_function
import argparse
import pyrax
import re
import socket
from os.path import expanduser


def is_valid_ip(ip):
    """
     Returns true if the IP is valid
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_hostname(hostname):
    """
     Returns true if the hostname is valid
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
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Turn up verbosity to 10')
    parser.add_argument('--veryverbose', action='store_true',
                        help='Turn up verbosity to 11')
    parser.add_argument('--hostname', '-n', required=True,
                        help='The base name for your instances')
    parser.add_argument('--address', '-a', required=True,
                        help='The base name for your instances')
    args = parser.parse_args()
    if args.veryverbose:
        args.verbose = True
        print(parser.parse_args())
    if not is_valid_hostname(args.hostname):
        print('You need to give me a valid hostname')
        exit()
    if not is_valid_ip(args.address):
        print('You need to give me a valid IP address')
        exit()
    dns_dict_list = [{'type': 'A',
                      'name': args.hostname,
                      'data': args.address}]
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    dns = pyrax.cloud_dns
    dns.create(name=args.hostname,
               emailAddress='foo@bar.com',
               records=dns_dict_list)