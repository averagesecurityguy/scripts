#!/bin/sh
#
# Taken from: http://www.nta-monitor.com/wiki/index.php/Ike-scan_User_Guide
# Usage: generate-transforms.sh | xargs --max-lines=8 ike-scan 10.0.0.0/24

# Encryption algorithms: DES, Triple-DES, AES/128, AES/192 and AES/256
ENCLIST="1 5 7/128 7/192 7/256"
# Hash algorithms: MD5 and SHA1
HASHLIST="1 2"
# Authentication methods: Pre-Shared Key, RSA Signatures, Hybrid Mode and XAUTH
AUTHLIST="1 3 64221 65001"
# Diffie-Hellman groups: 1, 2 and 5
GROUPLIST="1 2 5"
#
for ENC in $ENCLIST; do
   for HASH in $HASHLIST; do
      for AUTH in $AUTHLIST; do
         for GROUP in $GROUPLIST; do
            echo "--trans=$ENC,$HASH,$AUTH,$GROUP"
         done
      done
   done
done