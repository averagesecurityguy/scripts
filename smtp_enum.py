#!/usr/bin/env python3
# Copyright (c) 2015, LCI Technology Group, LLC
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
#  Neither the name of LCI Technology Group, LLC nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
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

import smtplib
import sys


def load_emails(filename):
    """
    Load the target email addresses from a file.
    """
    emails = []
    print('[*] Loading email addresses.')
    with open(filename) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('#'):
                continue
            if line == '':
                continue

            emails.append(line)

    return emails


def usage():
    """
    Print usage statement and exit.
    """
    print('Usage: smtp_enum.py mx_server port email_file')
    sys.exit()


if __name__ == '__main__':
    """
    Enumerate the target email addresses.

    Use the EXPN, VRFY, or RCPT TO method to enumerate email addresses.
    """ 
    if len(sys.argv) != 4:
        usage()

    debug = False
    helo = 'mail.example.com'
    mail_from = 'user@example.com'
    mx = sys.argv[1]
    port = int(sys.argv[2])
    emails = load_emails(sys.argv[3])

    try:
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(debug)

        smtp.connect(mx, port)
        smtp.ehlo(helo)

        if smtp.has_extn('vrfy') is True:
            print('[*] Using VRFY to enumerate email addresses.')
            check = smtp.vrfy
        elif smtp.has_extn('expn') is True:
            print('[*] Using EXPN to enumerate email addresses.')
            check = smtp.expn
        else:
            print('[*] Using RCPT to enumerate email addresses.')
            smtp.mail(mail_from)
            check = smtp.rcpt

        for email in emails:
            code, _ = check(email)
            if code == 250:
                print('[+] {0}'.format(email))
            else:
                print('[-] {0}'.format(email))

        smtp.quit()

    except smtplib.SMTPDataError as e:
        print('[-] {0}'.format(str(e[1])))

    except smtplib.SMTPServerDisconnected as e:
        print('[-] {0}'.format(str(e)))

    except smtplib.SMTPConnectError as e:
        print('[-] {0}'.format(str(e[1])))

    except smtplib.SMTPSenderRefused as e:
        print('[-] {0}'.format(str(e)))
