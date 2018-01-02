#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, LCI Technology Group, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
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

import BaseHTTPServer
import random

SERVER = '10.230.229.11'
PORT = 8080

def get_filename():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    fn = ''.join([random.choice(chars) for i in xrange(12)])

    return fn


class PostHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))

        fn = get_filename()
        with open(fn, 'w') as fh:
            fh.write(data.decode())

        self.send_response(200)

        return

    def do_GET(self):
        page = '''
        <h1>Upload a File</h1>
        <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="file" placeholder="Enter a filename."></input><br />
        <input type="submit" value="Import">
        </form>
        '''

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page)


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer((SERVER, PORT), PostHandler)
    print 'Starting server on {0}:{1}, use <Ctrl-C> to stop'.format(SERVER, PORT)
    server.serve_forever()
