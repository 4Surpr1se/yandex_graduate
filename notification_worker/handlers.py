import smtplib
from email.message import EmailMessage
from getpass import getpass

class NotificationHandler:
    def send(self, data):
        raise NotImplementedError("Must override send method")

class EmailNotificationHandler(NotificationHandler):
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        
    def send(self, data):
        subject = data.get("subject", "No Subject")
        body = data.get("body", "")
        recipient = data.get("to", "")

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = recipient
        msg.set_content(body)

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
