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
 Write an application that will:
 - Create 2 servers, supplying a ssh key to be installed at /root/.ssh/authorized_keys.
 - Create a load balancer
 - Add the 2 new servers to the LB
 - Set up LB monitor and custom error page.
 - Create a DNS record based on a FQDN for the LB VIP.
 - Write the error page html to a file in cloud files for backup.

 Worth 8 points!
"""

import pyrax
from time import sleep
from os.path import expanduser


if __name__ == '__main__':
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    #set the ssh key
    ssh_key = """ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu9VZU6tF6NDPdyAsi6zlBv0rvDRLIhDXo36Ly3GrSD7/ai66ec1K+AmUDAc2UInxgK+mGs+b+mo7IaZ3sZvPM3kuxm+hw2PWN1BtjGdXKrPhr6su0oqnHTE8HIE8EQ9Jqpj/8hpczhhfkL8ygfxQeJb2EFanF7OH+lOM0I54+PbBYNS+7+iVjDMmoL8mNTRnyJ0RhNnpEoxN88Ny/LiBU/8f5sN2PseGYoJh/h+H1W/qGuqBGCxyyseITWDcWUtaJGspIUWbzX7RuXotOnnaemKqGJm6DE2KUTGhHPKj4xV9ToKm4k88K2Tt727tZFDnvuBpaPPkaZoh8mIZxIWjYw=="""
    files = {"/root/.ssh/authorized_keys": ssh_key}

    #get the pyrax stuff out of the way
    cs = pyrax.cloudservers
    clb = pyrax.cloud_loadbalancers
    cf = pyrax.cloudfiles
    dns = pyrax.cloud_dns

    #get the image and flavor I want to use, then build the instances
    images = cs.images.list()
    image = [image for image in cs.images.list()
             if 'Gentoo 12.3' in image.name][0]
    flavor = [flavor for flavor in cs.flavors.list()
              if flavor.ram == 512][0]
    server1 = cs.servers.create('challenge10-1.example-mthode.org',
                                image.id,
                                flavor.id,
                                files=files)
    server2 = cs.servers.create('challenge10-2.example-mthode.org',
                                image.id,
                                flavor.id,
                                files=files)

    #wait for the servers networking to become configured
    while not (server1.networks and server2.networks):
        sleep(5)
        server1 = cs.servers.get(server1.id)
        server2 = cs.servers.get(server2.id)

    #set up the load balancer
    node1 = clb.Node(address=server1.networks['private'][0],
                     port=80,
                     condition="ENABLED")
    node2 = clb.Node(address=server2.networks['private'][0],
                     port=80,
                     condition="ENABLED")
    vip = clb.VirtualIP(type="PUBLIC")
    lb = clb.create("challenge10", port=80, protocol="HTTP",
                    nodes=[node1, node2], virtual_ips=[vip])

    #wait for it to become active and add health monitoring
    while lb.status != 'ACTIVE':
        sleep(5)
        lb = clb.get(lb.id)
    lb.add_health_monitor(type="CONNECT", delay=10, timeout=10,
                          attemptsBeforeDeactivation=5)
    sleep(5)
    while lb.status != 'ACTIVE':
        sleep(5)
        lb = clb.get(lb.id)
    lb_error_page = "<html><body>Sorry, something is amiss!</body></html>"
    lb.manager.set_error_page(lb, lb_error_page)

    #set up DNS entry point to the load balancer
    dns_dict_list = [{'type': 'A',
                      'name': 'challenge10.example-mthode.org',
                      'data': lb.virtual_ips[0].address}]
    dns.create(name='challenge10.example-mthode.org',
               emailAddress='foo@bar.com',
               records=dns_dict_list)

    #back up the lb error page
    cont = cf.create_container("challenge10")
    obj = cf.store_object("challenge10",
                          "challenge10-lb-error.html",
                          lb_error_page)
