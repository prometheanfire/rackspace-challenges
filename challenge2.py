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
 Write a script that clones a server (takes an
 image and deploys the image as a new server).

 *Worth 2 Point*

 This will image the first server it can.
"""


import pyrax
from os.path import expanduser
from time import strftime, sleep, gmtime

if __name__ == '__main__':
    #initialize pyrax and create variables
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cs = pyrax.cloudservers
    flavor = [flavor for flavor in cs.flavors.list()
              if flavor.ram == 512][0]
    server = cs.servers.list()[0]
    image_name = server.name + strftime("_%Y%m%d-%H%M%S", gmtime())
    img_id = cs.servers.create_image(server.id, image_name)
    #wait for the image to be created then deploy image to new instance
    while True:
        sleep(60)
        image_list = cs.images.list()
        for image in image_list:
            if image.id == img_id:
                if image.status == 'ACTIVE':
                    server = cs.servers.create(image.name + 'DUP!',
                                               image.id, flavor.id)
                    print "Name:", server.name
                    print "ID:", server.id
                    print "Status:", server.status
                    print "Admin Password:", server.adminPass
                    print "Networks:", server.networks
                    break
        else:
            continue
        break