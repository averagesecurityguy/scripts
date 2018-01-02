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

require 'rubygems'
require 'libxml'
require 'rextable'
require 'optparse'

Wap = Struct.new(:mac, :ssid, :power, :channel, :encryption, :quality)

def sort_wap_list(wap_list, sort)
	case sort.downcase
		when 'ssid'
			return wap_list.sort_by {|w| [w.ssid, w.mac]}
		when 'mac'
			return wap_list.sort_by {|w| w.mac}
		when 'channel'
			return wap_list.sort_by {|w| [w.channel.to_i, w.mac]}
		when 'encryption'
			return wap_list.sort_by {|w| [w.encryption, w.mac]}
	end
end

def split_wap_list(wap_list, split)
	hash = Hash.new
	wap_list.each do |entry|
		case split.downcase
			when 'ssid'
				key = entry.ssid
			when 'mac'
				key = entry.mac
			when 'channel'
				key = entry.channel
			when 'encryption'
				key = entry.encryption
		end
	
		unless hash[key]
			hash[key] = Array.new
			hash[key] << entry
		else
			hash[key] << entry
		end
		
	end

	return hash
end

#-----------------------------------------------------------------------------
# Process command line arguments
#-----------------------------------------------------------------------------
options = {}

optparse = OptionParser.new do|opts|
	# Usage banner
	opts.banner =  "Gpx_view is a ruby script that reads a GPX file and outputs "
	opts.banner += "the wireless access points identified in the file. The "
	opts.banner += "output format can be short or long. The short format prints "
	opts.banner += "each wireless access point once while the long format "
	opts.banner += "prints each instance of the wireless access point. The " 
	opts.banner += "default format is short. Wireless access points can be "
	opts.banner += "sorted by MAC address, SSID, channel or encryption type.\n\n"

	# GPX file to read
	options[:gpx] = ""
	opts.on('-g', '--gpx FILE', "GPX file to parse.") do |g|
		options[:gpx] = g
	end
	
	# Report format to use
	options[:format] = "short"
	opts.on( '-f', '--format FORMAT', "Report format to use. Must be 'short' or 'long'" ) do |f|
		options[:format] = f
	end

	# Sort method
	options[:sort] = "mac"
	opts.on( '-s', '--sort METHOD', "Sort method for access points. Must be 'mac', 'ssid', 'channel', or 'encryption'" ) do |s|
		options[:sort] = s
	end

	# This displays the help screen.
	opts.on( '-h', '--help', 'Display this screen' ) do
		puts opts
		exit
	end
end

optparse.parse!


#-----------------------------------------------------------------------------
# Validate command line arguments
#-----------------------------------------------------------------------------

# Ensure GPX file exists
unless File.exists?(options[:gpx])
	puts "[ERROR] GPX file does not exist."
	exit
end

# Ensure GPX file is a file
unless File.file?(options[:gpx])
	puts "[ERROR] GPX file is not a file."
	exit
end

# Ensure GPX file is not empty
if File.zero?(options[:gpx])
	puts "[ERROR] GPX file is empty."
	exit
end

# Ensure a valid sort option was given
unless ['ssid', 'mac', 'channel', 'encryption'].include?(options[:sort].downcase)
	raise OptionParser::InvalidArgument("The sort value must be 'ssid', 'mac', 'channel', or 'encryption'.")
end

# Ensure a valid format option was given
unless ['short', 'long'].include?(options[:format].downcase)
	raise OptionParser::InvalidArgument("The format value must be either 'short' or 'long'.")
end


#-----------------------------------------------------------------------------
# Begin Main Program
#-----------------------------------------------------------------------------

# Open the GPX file with libxml
doc = LibXML::XML::Document.file(options[:gpx])
wap_list = Array.new
entries = doc.root.find('wpt')

# Process WAP entries
entries.each do |wpt|
    mac = wpt.find_first('extensions/MAC').content
    ssid = wpt.find_first('extensions/SSID').content
    if not ssid then ssid = "<No SSID>" end
    if ssid =~ /&amp;#0;+/ then ssid = "<No SSID>" end
    power = wpt.find_first('extensions/RSSI').content
    channel = wpt.find_first('extensions/ChannelID').content

    # The security settings could be in the privacy tag or the security tag
    if wpt.find_first('extensions/privacy')
	encryption = wpt.find_first('extensions/privacy').content
    end
    if wpt.find_first('extensions/security')
        encryption = wpt.find_first('extensions/security').content
    end

    quality = wpt.find_first('extensions/signalQuality').content
    
    wap = Wap.new(mac, ssid, power, channel, encryption, quality) 
	
	wap_list << wap
	
end

# Sort the wap_list based on the sort value
wap_list = sort_wap_list(wap_list, options[:sort])

if options[:format].downcase == 'short'
    tbl = RexTable::Table.new('Columns' => ["MAC", "SSID", "Power", "Channel", "Encryption", "Quality"])

	prev_mac = ''
	wap_list.each do |w|
		next if w.mac == prev_mac
        tbl << [w.mac, w.ssid, w.power, w.channel, w.encryption, w.quality]
		prev_mac = w.mac
    end
    
    puts tbl.to_s
end

if options[:format].downcase == 'long'
	waps = split_wap_list(wap_list, options[:sort])
	
	waps.keys.sort.each do |k|
		
        tbl = RexTable::Table.new(	'Header' => k, 
									'Columns' => ["MAC", "SSID", "Power", "Channel", "Encryption", "Quality"])

		prev_mac = ''
		waps[k].each do |w|
			next if w.mac == prev_mac
            tbl << [w.mac, w.ssid, w.power, w.channel, w.encryption, w.quality]
			prev_mac = w.mac
        end
		
        puts tbl.to_s
        puts
        puts
    end
end
