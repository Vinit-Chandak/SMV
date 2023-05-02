import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    from_email = 'mspv.m474@gmail.com'
    password = 'ZGrvcTMwAf3P97xR'
    smtp_server = 'smtp-relay.sendinblue.com'
    smtp_port = 587  # Usually 587 for TLS

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

# Example usage
#send_email('Weather Alert', 'There is a weather alert in your area.', 'upadhyayshreya23@gmail.com')