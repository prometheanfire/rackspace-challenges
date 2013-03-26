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
 Write a script that creates a CDN-enabled container in Cloud Files.

 Worth 1 Point
"""


import pyrax
from os.path import expanduser


if __name__ == '__main__':
    #initialize pyrax and create variables
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cf = pyrax.cloudfiles
    cont = cf.create_container("example")
    cf.make_container_public("example", ttl=900)