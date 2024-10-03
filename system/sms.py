'''
Sms alert sending function using africas talking api
'''
import africastalking
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the SDK
username = 'Mosesomo'
api_key = os.getenv('AFRICAS_TALKING_API_KEY')
if not api_key:
    print("API key not found! Make sure to set AFRICAS_TALKING_API_KEY environment variable.")

africastalking.initialize(username, api_key)

sms = africastalking.SMS

class SendSMS:

    def send_message(self, recipients, message):
        try:
            response = sms.send(message, recipients)
            print(f"SMS sent: {response}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

# sms_service = SendSMS()
# sms_service.send_message(["+254758171116"], "Test message from Africa's Talking sandbox.")
