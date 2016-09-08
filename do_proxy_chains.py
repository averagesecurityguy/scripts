#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016, LCI Technology Group, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of LCI Technology Group, LLC nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import requests
import random
import json
import time
import sys
import subprocess
import os

"""
This script creates a 512Mb DigitalOcean droplet using a random image in a
random datacenter. The script will also use the SSH key specified in KEY_NAME.
Before using this script you will need to create a DigitalOcean account, an
API key (https://www.digitalocean.com/help/api/), and add the SSH key you
want to use to your account (https://www.digitalocean.com/community/tutorials
/how-to-use-ssh-keys-with-digitalocean-droplets). Enter the API key for your
account below along with the name of the SSH key you added to your account.
Other than that, no other changes should be made to the script.
"""

KEY_NAME = 'proxy'
API_KEY = ''


def send(method, endpoint, data=None):
    """
    Send an API request.

    Send the any provided data to the API endpoint using the specified method.
    Process the API response and print any error messages.
    """
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(API_KEY)}

    url = 'https://api.digitalocean.com/v2/{0}'.format(endpoint)
    resp = None

    if method in ['POST', 'DELETE', 'PUT']:
        data = json.dumps(data)

    if method == 'POST':
        resp = requests.post(url, headers=headers, data=data)
    elif method == 'DELETE':
        resp = requests.delete(url, headers=headers, data=data)
    elif method == 'PUT':
        resp = requests.put(url, headers=headers, data=data)
    else:
        resp = requests.get(url, headers=headers, params=data)

    if resp.content != b'':
        data = resp.json()

    if resp.status_code in range(400, 499):
        print('[-] Request Error: {0}'.format(data['message']))
        return None

    if resp.status_code in range(500, 599):
        print('[-] Server Error: {0}'.format(data['message']))
        return None

    return data


def random_str(size):
    """
    Create a random string of the specified size.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    str = ''.join([random.SystemRandom().choice(chars) for _ in range(size)])

    return str


def get_images():
    """
    Get a list of DigitalOcean images and the regions in which they are
    available.
    """
    print('[*] Getting image list.')
    resp = send('GET', 'images', {'type': 'distribution'})
    images = []

    if resp is not None:
        for image in resp['images']:
            images.append((image['slug'], image['regions']))

    return images


def get_ssh_key(key_name):
    """
    Get a list of SSH key names and fingerprints. Return the fingerprint that
    matches the name we want.
    """
    print('[*] Getting SSH key {0}'.format(key_name))
    resp = send('GET', 'account/keys')

    if resp is not None:
        for s in resp['ssh_keys']:
            if s['name'] == key_name:
               return s['name'], s['fingerprint']

    return None, None


def get_droplet_ip(droplet_id):
    """
    Get the status of a particular droplet.
    """
    print('[*] Getting droplet IP')
    resp = send('GET', 'droplets/{0}'.format(droplet_id))

    while resp['droplet']['status'] != 'active':
        print('[*] Waiting for droplet to become active.')
        time.sleep(10)
        resp = send('GET', 'droplets/{0}'.format(droplet_id))

    return resp['droplet']['networks']['v4'][0]['ip_address']


def create_droplet(images, fingerprint):
    """
    Create a new droplet.
    """
    print('[*] Creating new droplet.')

    image, regions = random.SystemRandom().choice(images)

    droplet = {'name': random_str(8),
               'region': random.SystemRandom().choice(regions),
               'size': '512mb',
               'image': image,
               'ssh_keys': [fingerprint],
               'backups': False,
               'ipv6': False,
               'user_data': None,
               'private_networking': None}

    resp = send('POST', 'droplets', droplet)

    if resp is not None:
        droplet_id = resp['droplet']['id']
        print('[+] Successfully created droplet {0}.'.format(droplet_id))
        ip = get_droplet_ip(droplet_id)
        return droplet_id, ip

    else:
        print('[-] Unable to create droplet.')
        return None, None


def delete_droplet(droplet_id):
    """
    Delete the specified droplet.
    """
    print('[*] Deleting droplet.')
    resp = send('DELETE', 'droplets/{0}'.format(droplet_id))

    if resp is not None:
        print('[+] Successfully deleted image {0}.'.format(droplet_id))
    else:
        print('[-] Unable to delete image {0}.'.format(droplet_id))


def usage():
    """
    Print the usage information.
    """
    u = '''
    Usage:
        ./do_proxy_chains.py create number droplet_id_file
        ./do_proxy_chains.py delete droplet_id_file
    '''
    print(u)

    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'create':
        images = get_images()
        name, fingerprint = get_ssh_key(KEY_NAME)
        droplets = {}

        if (images != []) and  (fingerprint is not None):
            # Launch our DigitalOcean machines
            for i in range(int(sys.argv[2])):
                droplet_id, ip = create_droplet(images, fingerprint)
                droplets[droplet_id] = {'ip': ip, 'key': name}

            # Save our droplet ids to a file so we can delete them later.
            with open(sys.argv[3], 'w') as f:
                f.write('{0}'.format('\n'.join([str(k) for k in droplets])))

            # Launch our SSH Proxies
            port = 10080
            home = os.path.expanduser('~')
            for k, v in droplets.items():

                ssh_key = '{0}/.ssh/{1}'.format(home, v['key'])
                server = 'root@{0}'.format(v['ip'])
                accept = '-oStrictHostKeyChecking=no'
                cmd = 'ssh -Nf -i ~/.ssh/{0} -D {1} root@{2}'

                res = subprocess.run(['ssh', accept, '-Nf', '-i', ssh_key, '-D', str(port), server])
                while res.returncode != 0:
                    port += 1
                    res = subprocess.run(['ssh', accept, '-Nf', '-i', ssh_key, '-D', str(port), server])

                print('[+] Successfully created SSH proxy on {0}'.format(port))
                v['port'] = port
                port += 1


            # Write our proxy chains file
            with open('/etc/proxychains.conf', 'w') as f:
                f.write('random_chain\n')
                f.write('chain_len=1\n')
                f.write('[ProxyList]\n')
                for k, v in droplets.items():
                    f.write('socks5 127.0.0.1 {0}\n'.format(v['port']))


    elif len(sys.argv) == 3 and sys.argv[1] == 'delete':
        try:
            with open(sys.argv[2]) as f:
                for line in f:
                    delete_droplet(line.rstrip('\r\n'))

            print('[*] Removing {0}'.format(sys.argv[2]))
            os.remove(sys.argv[2])
            print('[*] Removing /etc/proxychains.conf')
            os.remove('/etc/proxychains.conf')

        except FileNotFoundError as e:
            print('[-] {0}'.format(e))

    else:
        usage()
