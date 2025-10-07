import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class GmailSMTPClient:
    def __init__(self):
        """
        Initialize the Gmail SMTP client.

        :param email: Sender's Gmail address
        :param app_password: App password generated via Google Account
        :param use_tls: Use TLS (port 587) or SSL (port 465)
        """
        self.email = os.environ.get("SMPT_EMAIL")
        self.app_password = os.environ.get("SMTP_PASSCODE")
        self.use_tls = True
        self.smtp_server = "smtp.gmail.com"
        self.port = 587 if self.use_tls else 465

    def send_self_email(self, subject: str, body: str, body_type="plain"):
        self.send_email(self.email, subject, body, body_type)

    def send_email(self, to_email: str, subject: str, body: str,
                   body_type="html"):
        """
        Send an email via Gmail SMTP.

        :param to_email: Recipient email address
        :param subject: Subject of the email
        :param body: Body content of the email
        :param body_type: 'plain' or 'html'
        """
        # Construct the email
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, body_type))

        try:
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.starttls()
                    server.login(self.email, self.app_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                    server.login(self.email, self.app_password)
                    server.send_message(message)

            print("✅ Email sent successfully!")
        except Exception as e:
            print("❌ Failed to send email:", e)
