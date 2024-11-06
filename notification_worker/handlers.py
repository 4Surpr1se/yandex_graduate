import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pydantic import BaseSettings

class NotificationHandler:
    def send(self, data):
        raise NotImplementedError("Must override send method")

class EmailNotificationHandler(NotificationHandler):
    def __init__(self, api_key, all_users_email_list=None):
        self.api_key = api_key
        self.all_users_email_list = all_users_email_list or []
        
        # Инициализация конфигурации и API-клиента Sendinblue
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_email(self, to, subject, body):
        # Создание и настройка сообщения
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to}],
            sender={"email": "your_email@example.com"},
            subject=subject,
            text_content=body
        )

        try:
            response = self.api_instance.send_transac_email(email)
            print(f"Email sent to {to}. Status: {response['messageId']}")
        except ApiException as e:
            print(f"Failed to send email to {to}: {str(e)}")

    def send(self, data):
        subject = data.get("subject", "No Subject")
        body = data.get("body", "")
        recipient = data.get("recipient")

        if recipient == "all_users":
            for email in self.all_users_email_list:
                self.send_email(email, subject, body)
        else:
            self.send_email(recipient, subject, body)
