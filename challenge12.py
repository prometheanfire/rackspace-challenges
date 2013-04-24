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
 Write an application that will create a route in mailgun so that when an email is sent to
   <YourSSO>@apichallenges.mailgun.org it calls your Challenge 1 script that builds 3 servers.

 Assumptions:
 Assume that challenge 1 can be kicked off by accessing http://cldsrvr.com/challenge1
   (I am aware this doesn't work. You just need to make sure that your message is getting posted to that URL)
 We have an internal mailgun account for this challenge. The API key is "lol-nope".
   DO NOT PUT THE API KEY IN YOUR SCRIPT. Assume the Mailgun API key exists at ~/.mailgunapi.
   Assume no formatting, the api key will be the only data in the file.

 Worth 3 points
"""

from __future__ import print_function
from os.path import expanduser
from urllib import urlencode
import urllib2
import base64


def create_route(apikey,
                 target_email,
                 target_url='http://cldsrvr.com/challenge1'):
    """
    returns a urllib2 response
    :param apikey: string containing the mailgun api key
    :param target_email: string containing the trigger email
    :param target_url: string containing an optional url specifying where data is sent
    """

    auth = base64.standard_b64encode('api:%s' % apikey.replace('\n', ''))
    data = urlencode({'priority': '1',
                      'description': 'challenge12-prometheanfire',
                      'expression': 'match_recipient(\'%s\')' % target_email,
                      'action': ['forward("%s")' % target_url,
                                 'stop()']}, doseq=True)
    headers = {'Authorization': 'Basic %s' % auth}
    uri = 'https://api.mailgun.net/v2/routes?' + data

    request = urllib2.Request(uri, '', headers=headers)
    return urllib2.urlopen(request).read()


def get_routes(apikey):
    """
    returns the currently used routes
    :param apikey: string containing the mailgun api key
    """
    auth = base64.standard_b64encode('api:%s'% apikey.replace('\n', ''))
    headers = {'Authorization': 'Basic %s' % auth}

    request = urllib2.Request('https://api.mailgun.net/v2/routes', headers=headers)
    return urllib2.urlopen(request).read()


if __name__ == '__main__':
    with open(expanduser('~/.mailgunapi')) as api_keys:
        mailgun_apikey = api_keys.readline()

    print('current routes\n', get_routes(mailgun_apikey), '\n\n')

    result = create_route(mailgun_apikey,
                          'matt.thode@apichallenges.mailgun.org')
    print('post response\n', result)