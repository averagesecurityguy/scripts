#!/usr/bin/env python
# Copyright (c) 2012, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this 
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice, 
#  this list of conditions and the following disclaimer in the documentation 
#  and/or other materials provided with the distribution.
#
#  Neither the name of AverageSecurityGuy nor the names of its contributors may
#  be used to endorse or promote products derived from this software without
#  specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.

import smtpd
import asyncore

MAILFILE = 'mailfile.txt'
SERVER = '127.0.0.1'
PORT = 2525

def save_message(fr, to, msg):
    with open(MAILFILE, 'a') as mf:
        mf.write('FROM: {0}\nTO: {1}\nMSG:\n{2}\n\n'.format(fr, to, msg))


class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        print '[*] Saving message for {0}.'.format(rcpttos)
        
        try:
            save_message(mailfrom, rcpttos, data)
        except:
            pass

server = CustomSMTPServer((SERVER, PORT), None)
print '[+] Server listening on port {0}'.format(PORT)
asyncore.loop()