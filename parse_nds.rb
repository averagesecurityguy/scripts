#!/usr/bin/ruby
#Copyright (C) 2011 Stephen Haywood aka Averagesecurityguy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

require 'rexml/document'
require 'rextable'
require 'openssl'
require 'base64'

def usage
    puts "parse_nds reads a ColdFusion neo-datasoure.xml file, finds the "
    puts "encrypted passwords, and decrypts them. The encrypted and decrypted "
	puts "passwords are output as a table."
    puts
    puts "Usage: parse_nds.rb file"
end

def decrypt(cpass)
	des = OpenSSL::Cipher::Cipher.new('des-ede3')
    des.decrypt
    des.key = '0yJ!@1$r8p0L@r1$6yJ!@1rj'
    return des.update(Base64.decode64(cpass)) + des.final
end

def get_passwords(data)
	pwds = Array.new
    data.scan(/\<string\>([a-zA-Z0-9\+\/]+==)\<\/string>/m) do |m|
        pwds << m[0]
	end
    return pwds
end

#-----------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------
if ARGV.length < 1 then
    usage
    exit(1)
end

data = File.new(ARGV[0], 'r').read
passwords = get_passwords(data)
tbl = RexTable::Table.new('Columns' => ["Encrypted", "Decrypted"],
			'Header'=> 'Passwords')

passwords.each do |p|
	tbl << [p, decrypt(p)]
end

puts tbl.to_s
