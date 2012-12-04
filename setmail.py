import smtpd
import smtplib
import asyncore
import dns.resolver

port = 2525
debug = True

def get_mx_record(domain):
    records = dns.resolver.query(domain, 'MX')
    return str(records[0].exchange)

class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        for rcptto in rcpttos:
            domain = rcptto.split('@')[1]
            print domain
            mx = get_mx_record(domain)
            print mx
            server = smtplib.SMTP(mx, 25)
            if debug:
                server.set_debuglevel(True)
            try:
                server.sendmail(mailfrom, rcptto, data)
            finally:
                server.quit()

server = CustomSMTPServer(('127.0.0.1', port), None)
print 'Server listening on port {0}'.format(port)
asyncore.loop()