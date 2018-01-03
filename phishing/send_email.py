import smtplib
import os.path
import email.mime.application as ema
import email.mime.multipart as emm
import email.mime.text as emt
import email.utils as eu
import dns.resolver

def get_mx_record(domain):
    records = dns.resolver.query(domain, 'MX')
    return str(records[0].exchange)


def send_mail(send_from, send_to, subject, text, filename=None):
    msg = emm.MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = eu.formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(emt.MIMEText(text))

    # Attach the given file.
    if filename is not None:
        with open(filename, "rb") as f:
            part = ema.MIMEApplication(f.read(), Name=os.path.basename(f))

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    # Get the recipient MX record.
    domain = send_to.split('@')[1]
    server = get_mx_record(domain)
    smtp = smtplib.SMTP(server)

    # Send
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


def usage():
    print("send_email.py from to subject text [attachment]")
    os.exit()


if len(sys.argv) == 5:
    send_mail(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if len(sys.argv) == 6:
    send_mail(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

usage()
