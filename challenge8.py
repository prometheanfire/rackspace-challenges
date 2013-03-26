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
 Write a script that will create a static webpage served
 out of Cloud Files. The script must create a new container, cdn enable
 it, enable it to serve an index file, create an index file object,
 upload the object to the container, and create a CNAME record pointing
 to the CDN URL of the container.

 Worth 3 Points
"""

import pyrax
from os.path import expanduser
import urlparse


INDEX = '''<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>

<p>My first paragraph.</p>

</body>
</html>'''

if __name__ == '__main__':
    #initialize pyrax and create variables
    pyrax.set_credential_file(expanduser('~/.rackspace_cloud_credentials'))
    cf = pyrax.cloudfiles
    cont = cf.create_container('example')
    cf.make_container_public('example', ttl=900)
    cf.set_container_web_index_page('example', 'index.html')
    obj = cont.store_object('index.html', INDEX)
    dns_dict_list = [{'type': 'A',
                      'name': 'example-mthode.org',
                      'data': '1.2.3.4'},
                     {'type': 'CNAME',
                      'name': 'site.example-mthode.org',
                      'data': urlparse.urlparse(cont.cdn_uri).hostname}]
    dns = pyrax.cloud_dns
    dns.create(name='example-mthode.org',
               emailAddress='foo@bar.com',
               records=dns_dict_list)