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

require 'gserver'
require 'resolv'
require 'net/smtp'
require 'openssl'

PORT = 25         # Set the port for the SMTP server to listen on.
$debug = false     # Set the debug mode, true or false

# WARNING! THIS IMPLEMENTS AN OPEN SMTP RELAY USE CAUTIOUSLY!

# Modify the built in NET::SMTP class to support TLS (encryption). The SMTP 
# library is used to send out bound email messages. I don't remember where I 
# found the code but it appears to be in the public domain.
Net::SMTP.class_eval do
	private
	def do_start(helodomain, user, secret, authtype)
		raise IOError, 'SMTP session already started' if @started
		check_auth_args user, secret, authtype if user or secret

		sock = timeout(@open_timeout) { TCPSocket.open(@address, @port) }
		@socket = Net::InternetMessageIO.new(sock)
		@socket.read_timeout = 60 #@read_timeout
		if $debug then @socket.debug_output = STDERR end #@debug_output

		check_response(critical { recv_response() })
		do_helo(helodomain)

		raise 'openssl library not installed' unless defined?(OpenSSL)
		starttls
		ssl = OpenSSL::SSL::SSLSocket.new(sock)
		ssl.sync_close = true
		ssl.connect
		@socket = Net::InternetMessageIO.new(ssl)
		@socket.read_timeout = 60 #@read_timeout
		if $debug then @socket.debug_output = STDERR end #@debug_output
		do_helo(helodomain)

		authenticate user, secret, authtype if user
		@started = true
		ensure
			unless @started
				# authentication failed, cancel connection.
				@socket.close if not @started and @socket and not @socket.closed?
	      			@socket = nil
	    	end
	end

	def do_helo(helodomain)
		begin
			if @esmtp
				ehlo helodomain
			else
				helo helodomain
		end
		rescue Net::ProtocolError
			if @esmtp
				@esmtp = false
				@error_occured = false
				retry
			end
      			raise
		end
	end

	def starttls
		getok('STARTTLS')
	end

	def quit
		begin
			getok('QUIT')
		rescue EOFError
		end
	end
end

# This is the SMTP server that listens on the port specified above. I found 
# the code here: https://github.com/aarongough/mini-smtp-server. It is under 
# the MIT license. I had to modify the code to add fake AUTH support (it
# responds ok to any credentials) and support for a SUBJECT line. I needed to  
# make a few other minor tweaks to make it work with SET.
class MiniSmtpServer < GServer

	def initialize(port = 2525, host = "127.0.0.1", max_connections = 4, *args)
		super(port, host, max_connections, *args)
	end
  
	def serve(io)
		Thread.current[:data_mode] = false
		Thread.current[:message] = {:data => ""}
		Thread.current[:message][:subject] = ""
		Thread.current[:message][:to] = Array.new
		Thread.current[:connection_active] = true
		io.print "220 hello\r\n"
		loop do
			if IO.select([io], nil, nil, 0.1)
				data = io.readpartial(4096)
				log("<<< " + data) if(@audit)
				output = process_line(data)
				log(">>> " + output) if(@audit && !output.empty?)
				io.print(output) unless output.empty?
			end
			break if(!Thread.current[:connection_active] || io.closed?)
		end
		io.print "221 bye\n"
		io.close
		Thread.current[:message][:data].gsub!(/\r\n\Z/, '').gsub!(/\.\Z/, '')
		new_message_event(Thread.current[:message])
	end

	def process_line(line)
		# Handle specific messages from the client 
		case line
		when (/^(HELO|EHLO|helo|ehlo)/)
			return "250-ESMTP localhost\r\n250 AUTH PLAIN\r\n"
		when (/^(QUIT|quit)/)
			Thread.current[:connection_active] = false
			return "\r\n"
		when (/^(MAIL FROM\:|mail from\:|mail FROM\:)/)
			Thread.current[:message][:from] = line.gsub(/^(MAIL FROM\:|mail from\:|mail FROM\:)/, '').strip
			return "250 OK\r\n"
		when (/^(RCPT TO\:|rcpt to\:|rcpt TO\:)/) 
			Thread.current[:message][:to] << line.gsub(/^(RCPT TO\:|rcpt to\:|rcpt TO\:)/, '').strip
			return "250 OK\r\n"
		when (/^(SUBJECT\:|subject\:)/)
			Thread.current[:message][:subject] = line.gsub(/^(SUBJECT\:|subject\:)/, '').strip
			return "250 OK\r\n"
		when (/^(DATA|data)/)
			Thread.current[:data_mode] = true
			return "354 Enter message, ending with \".\" on a line by itself\r\n"
		when (/^(AUTH|auth)/)
			return "235 Authentication successful...\r\n"
		end
    
		# If we are in data mode and the entire message consists
		# solely of a period on a line by itself then we
		# are being told to exit data mode
		if((Thread.current[:data_mode]) && (line.chomp =~ /^\.$/))
			Thread.current[:message][:data] += line
			Thread.current[:data_mode] = false
			Thread.current[:connection_active] = false
			return "250 OK\r\n"
		end
    
		# If we are in date mode then we need to add
		# the new data to the message
		if(Thread.current[:data_mode])
			Thread.current[:message][:data] += line
			return ""
		else
			# If we somehow get to this point then
			# we have encountered an error
            if $debug then puts "There was an error." end
			return "500 ERROR\r\n"
		end
	end
  
	def new_message_event(message_hash)
		if $debug then puts "super: new_message_event" end
	end
end


# When the server receives a new message, it attempts to lookup the MX record
# for each recipient and then sends the message to that recipient using the 
# mail server for the domain.
class CustomSMTPServer < MiniSmtpServer
    
	# Returns the highest priority MX record server for a domain or nil.
	#
	#   get_MX_server('mydomain.com') # => 'smtp.mydomain.com'
	def get_MX_server(domain)
        if $debug then puts "Looking for MX record." end
		mx = nil
		Resolv::DNS.open do |dns|
			mail_servers = dns.getresources(domain, Resolv::DNS::Resource::IN::MX)
			return nil unless mail_servers and not mail_servers.empty?
			highest_priority = mail_servers.first
			mail_servers.each do |server|
				highest_priority = server if server.preference < highest_priority.preference
			end
			mx = highest_priority.exchange.to_s
            if $debug then puts "Found MX record " + mx end
		end
  		return mx
	end
	
	def strip_brackets(str)
		return str.gsub(/</, '').gsub(/>/, '')
	end

	def build_message(f, t, s, m)
        if $debug then puts "Building message to " + t end
		msg = "From: #{f}\r\n"
		msg += "To: #{t}\r\n"
		msg += "Subject: #{s}\r\n"
		msg += m
		return msg
	end

    ##
    # Processes the email message sent to SETmail and sends it to the correct 
    # recipients.
	def new_message_event(message_hash)
		puts "Processing new message..."
		message_hash[:to].each do |rcpt|
			to = strip_brackets(rcpt)
			from = strip_brackets(message_hash[:from])
			subj = message_hash[:subject]
			msg = build_message(from, to, subj, message_hash[:data])
			domain = to.split('@')[1]
			mx = get_MX_server(domain)
			Net::SMTP.start(mx) do |smtp|
                if $debug then puts "Sending message to " + to end
				smtp.send_message(msg, from, to)
			end
		end
	end
end

server = CustomSMTPServer.new(PORT)
server.start
puts "SETmail started on port " + PORT.to_s
server.join  

