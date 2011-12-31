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

require 'rubygems'
require 'libxml'
require 'rextable'

Wap = Struct.new(:ssid, :power, :channel, :encryption, :quality)

def usage
    puts "gpx_view reads the gpxfile and outputs the wireless access points "
    puts "identified in the file. The output format can be short or long. "
    puts "The short format prints each wireless access point once while the "
    puts "long format prints each instance of the wireless access point. The "
    puts "default format is short. "
    puts
    puts "Usage: gpx_view.rb gpxfile [short|long]"
end

if ARGV.length < 1 then
    usage
    exit(1)
end

case ARGV[1]
when nil
    format = "short"
when "short"
    format = "short"
when "long"
    format = "long"
else
    usage
    exit(1)
end

doc = LibXML::XML::Document.file(ARGV[0])
waps = Hash.new
entries = doc.root.find('wpt')

entries.each do |wpt|
    mac = wpt.find_first('extensions/MAC').content
    ssid = wpt.find_first('extensions/SSID').content
    if not ssid then ssid = "<No SSID>" end
    if ssid =~ /&amp;#0;+/ then ssid = "<No SSID>" end
    power = wpt.find_first('extensions/RSSI').content
    channel = wpt.find_first('extensions/ChannelID').content
    encryption = wpt.find_first('extensions/privacy').content
    quality = wpt.find_first('extensions/signalQuality').content
    
    wap = Wap.new(ssid, power, channel, encryption, quality) 
    
    if not waps[mac] then
        waps[mac] = Array.new
        waps[mac] << wap
    else
        waps[mac] << wap
    end
end

if format == "short"
    tbl = RexTable::Table.new('Columns' => ["MAC Address", "SSID", "RSSI", "Channel", "Encryption", "Quality"])
    waps.each do |k, v|
        tbl << [k, v[0].ssid, v[0].power, v[0].channel, v[0].encryption, v[0].quality]
    end
    
    puts tbl.to_s
else
    waps.each do |k, v|
        tbl = RexTable::Table.new('Header' => k, 'Columns' => ["SSID", "RSSI", "Channel", "Encryption", "Quality"])
        v.each do |w|
            tbl << [w.ssid, w.power, w.channel, w.encryption, w.quality]
        end
        puts tbl.to_s
        puts
        puts
    end
end
