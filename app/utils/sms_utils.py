from twilio.rest import Client
import os

def send_sms_alert(phone, message):
    account_sid = os.getenv('TWILIO_SID')
    auth_token = os.getenv('TWILIO_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_=os.getenv('TWILIO_NUMBER'),
        to=phone
    )
    return message.sid