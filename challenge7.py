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
 Write a script that will create 2 Cloud Servers and add
 them as nodes to a new Cloud Load Balancer.

 Worth 3 Points
"""


from __future__ import print_function
import pyrax
from os.path import expanduser
from time import sleep


if __name__ == '__main__':
    #initialize pyrax and create variables
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cs = pyrax.cloudservers
    clb = pyrax.cloud_loadbalancers
    image = [image for image in cs.images.list()
             if "Gentoo 13.1" in image.name][0]
    flavor = [flavor for flavor in cs.flavors.list()
              if flavor.ram == 512][0]
    #create the servers
    server1 = cs.servers.create("server1", image, flavor)
    server2 = cs.servers.create("server2", image, flavor)
    #get their network info
    while not (server1.networks and server2.networks):
        sleep(5)
        server1 = cs.servers.get(server1.id)
        server2 = cs.servers.get(server2.id)
    #get the service net IPs of the instances
    server1_ip = server1.networks["private"][0]
    server2_ip = server2.networks["private"][0]
    #create the LB nodes
    node1 = clb.Node(address=server1_ip, port=80, condition="ENABLED")
    node2 = clb.Node(address=server2_ip, port=80, condition="ENABLED")
    vip = clb.VirtualIP(type="PUBLIC")
    lb = clb.create("example_lb", port=80, protocol="HTTP",
                    nodes=[node1, node2], virtual_ips=[vip])
    print([(lb.name, lb.id) for lb in clb.list()])