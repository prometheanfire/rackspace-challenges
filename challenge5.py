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
 Write a script that creates a Cloud Database
 instance. This instance should contain at least one database, and the
 database should have at least one user that can connect to it.

 *Worth 1 Point*
"""

import pyrax
from os.path import expanduser
from time import sleep


if __name__ == '__main__':
    pyrax.set_credential_file(expanduser("~/.rackspace_cloud_credentials"))
    cdb = pyrax.cloud_databases
    flavor = cdb.list_flavors()[0].name
    instance_name = 'name goes here'
    db_name = 'db_name_here'
    username = 'marx'
    password = 'what this is i don\'t even'
    inst = cdb.create(instance_name, flavor=flavor, volume=2)

    while True:
        sleep(60)
        instance_list = cdb.list()
        for instance in instance_list:
            if instance.id == inst.id:
                if instance.status == 'ACTIVE':
                    db = inst.create_database(db_name)
                    user = inst.create_user(name=username,
                                            password=password,
                                            database_names=[db])
                    break
        else:
            continue
        break
    print inst
    print db