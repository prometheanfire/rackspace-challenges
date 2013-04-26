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
 Write an application that nukes everything in your Cloud Account. It should:
 Delete all Cloud Servers
 Delete all Custom Images
 Delete all Cloud Files Containers and Objects
 Delete all Databases
 Delete all Networks
 Delete all CBS Volumes

 Worth 3 points
"""

from __future__ import print_function
import pyrax
from os.path import expanduser
from time import sleep


if __name__ == '__main__':
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cs_ord = pyrax.connect_to_cloudservers("ORD")
    cs_dfw = pyrax.connect_to_cloudservers("DFW")
    cf_ord = pyrax.connect_to_cloudfiles("ORD")
    cf_dfw = pyrax.connect_to_cloudfiles("DFW")
    cdb_ord = pyrax.connect_to_cloud_databases("ORD")
    cdb_dfw = pyrax.connect_to_cloud_databases("DFW")
    cnw_ord = pyrax.connect_to_cloud_networks("ORD")
    cnw_dfw = pyrax.connect_to_cloud_networks("DFW")
    cbs_ord = pyrax.connect_to_cloud_blockstorage("ORD")
    cbs_dfw = pyrax.connect_to_cloud_blockstorage("DFW")
    dns_ord = pyrax.connect_to_cloud_dns("ORD")
    dns_dfw = pyrax.connect_to_cloud_dns("DFW")
    lbs_ord = pyrax.connect_to_cloud_loadbalancers("ORD")
    lbs_dfw = pyrax.connect_to_cloud_loadbalancers("DFW")

    print('deleting servers')
    for server in cs_ord.servers.list():
        server.delete()
    for server in cs_dfw.servers.list():
        server.delete()

    print('deleting server images')
    for image in cs_ord.images.list():
        if hasattr(image, "server"):
            cs_ord.images.delete(image.id)
    for image in cs_dfw.images.list():
        if hasattr(image, "server"):
            cs_dfw.images.delete(image.id)

    print('deleting all dns records')
    for domain in dns_ord.list():
        domain.delete()
    for domain in dns_dfw.list():
        domain.delete()

    print('deleting files')
    for container in cf_ord.get_all_containers():
        container.delete_all_objects()
        sleep(10)
        container.delete()
    for container in cf_dfw.get_all_containers():
        container.delete_all_objects()
        sleep(10)
        container.delete()

    print('deleting databases')
    for db in cdb_ord.list():
        db.delete()
    for db in cdb_dfw.list():
        db.delete()

    print('waiting for servers to be deleted to delete networks and volumes')
    while not cs_ord.servers.list() == []:
        sleep(10)
    while not cs_dfw.servers.list() == []:
        sleep(10)

    print('deleting networks')
    for network in cnw_ord.list():
        if network.id == '00000000-0000-0000-0000-000000000000' or \
                '11111111-1111-1111-1111-111111111111':
            continue
        network.delete()
    for network in cnw_dfw.list():
        if network.id == '00000000-0000-0000-0000-000000000000' or \
                '11111111-1111-1111-1111-111111111111':
            continue
        network.delete()

    print('deleting volumes and volume snapshots')
    for vol in cbs_ord.list():
        while not vol.list_snapshots() == []:
            vol.delete_all_snapshots()
            sleep(10)
        vol.delete()
    for vol in cbs_dfw.list():
        while not vol.list_snapshots() == []:
            vol.delete_all_snapshots()
            sleep(10)
        vol.delete()

    print('deleting load balancers')
    for lb in lbs_dfw.list():
        lb.delete()
    for lb in lbs_ord.list():
        lb.delete()


    print('finished')