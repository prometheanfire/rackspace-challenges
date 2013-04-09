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
 Create an SSL terminated load balancer (Create self-signed certificate.)
 Create a DNS record that should be pointed to the load balancer.
 Create Three servers as nodes behind the LB.
      Each server should have a CBS volume attached to it. (Size and type are irrelevant.)
      All three servers should have a private Cloud Network shared between them.
      Login information to all three servers returned in a readable format as the result of the script, including connection information.

 Worth 6 points
"""

import pyrax
import statics
from time import sleep
from os.path import expanduser

if __name__ == '__main__':
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cnw = pyrax.cloud_networks
    cbs = pyrax.cloud_blockstorage
    cs = pyrax.cloudservers
    clb = pyrax.cloud_loadbalancers
    dns = pyrax.cloud_dns

    #build network
    network = cnw.create("challenge11", cidr="192.168.0.0/24")
    networks = network.get_server_networks(public=True, private=True)

    #build CBS volumes
    vol1 = cbs.create(name="challenge11-1", size=100, volume_type="SATA")
    vol2 = cbs.create(name="challenge11-2", size=100, volume_type="SATA")
    vol3 = cbs.create(name="challenge11-3", size=100, volume_type="SATA")

    #build instances
    images = cs.images.list()
    image = [image for image in cs.images.list()
             if 'Gentoo 12.3' in image.name][0]
    flavor = [flavor for flavor in cs.flavors.list()
              if flavor.ram == 512][0]
    server1 = cs.servers.create('challenge11-1.example-mthode.org',
                                image.id,
                                flavor.id,
                                nics=networks)
    server2 = cs.servers.create('challenge11-2.example-mthode.org',
                                image.id,
                                flavor.id,
                                nics=networks)
    server3 = cs.servers.create('challenge11-3.example-mthode.org',
                                image.id,
                                flavor.id,
                                nics=networks)

    server1_pass = server1.adminPass
    server2_pass = server2.adminPass
    server3_pass = server3.adminPass

    #wait for instances to become active
    while not ((server1.status == 'ACTIVE') and (server2.status == 'ACTIVE') and (server3.status == 'ACTIVE')):
        sleep(10)
        server1 = cs.servers.get(server1.id)
        server2 = cs.servers.get(server2.id)
        server3 = cs.servers.get(server3.id)

    #attach block storage to instances
    vol1.attach_to_instance(server1, mountpoint='/dev/xvdb')
    vol2.attach_to_instance(server2, mountpoint='/dev/xvdb')
    vol3.attach_to_instance(server3, mountpoint='/dev/xvdb')

    #initialize load balancer settings
    node1 = clb.Node(address=server1.networks['private'][0],
                     port=80,
                     condition="ENABLED")
    node2 = clb.Node(address=server2.networks['private'][0],
                     port=80,
                     condition="ENABLED")
    node3 = clb.Node(address=server3.networks['private'][0],
                     port=80,
                     condition="ENABLED")
    vip = clb.VirtualIP(type="PUBLIC")

    #create load balancer and add ssl termination
    lb = clb.create("challenge11", port=80, protocol="HTTP",
                    nodes=[node1, node2, node3], virtual_ips=[vip])
    while lb.status != 'ACTIVE':
        sleep(5)
        lb = clb.get(lb.id)
    lb.add_ssl_termination(securePort=443,
                           enabled=True,
                           secureTrafficOnly=False,
                           certificate=statics.PUBKEY,
                           privatekey=statics.PRIVKEY)

    #set up dns
    dns_dict_list = [{'type': 'A',
                      'name': 'challenge11.example-mthode.org',
                      'data': lb.virtual_ips[0].address}]
    dns.create(name='challenge11.example-mthode.org',
               emailAddress='foo@bar.com',
               records=dns_dict_list)

    #print the server info
    print "ID:", server1.id
    print "Status:", server1.status
    print "Admin password:", server1_pass
    print "Networks:", server1.networks
    print
    print "ID:", server2.id
    print "Status:", server2.status
    print "Admin password:", server2_pass
    print "Networks:", server2.networks
    print
    print "ID:", server3.id
    print "Status:", server3.status
    print "Admin password:", server3_pass
    print "Networks:", server3.networks