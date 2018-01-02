#!/usr/bin/env python
import sys
import hmac
import hashlib


def check_digest(session, digest, key):
    h = hmac.new(key, session, hashlib.sha1)
    if h.hexdigest() == digest:
        return key
    else:
        return None

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: rails_secret_key cookie_file key_file'
        sys.exit()

    for line in open(sys.argv[1]):
        line = line.rstrip('\r\n')
        url, session, digest = line.split('::')
        session = session.replace('%0A', '\n')

        for line in open(sys.argv[2]):
            key = line.rstrip('\r\n')
            if check_digest(session, digest, key) is not None:
                print 'Found secret_token for {0}: {1}'.format(url, key)