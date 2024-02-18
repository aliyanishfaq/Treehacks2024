from twilio.rest import Client
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

def send_emergency_call(phone_number, message):
    """
    Sends a call with a specified message to a given phone number using Twilio.
    Link to add verified caller ids: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
    Parameters:
    phone_number (str): The phone number to call, in E.164 formatting.
    message (str): The message to be read during the call.
    """
    # Twilio credentials - ideally, fetch from environment variables or a secure config
    # Fetch Twilio credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    # Create the call with TwiML to say the emergency message
    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        to=phone_number,
        from_='+18667643449'  # Your Twilio number
    )

    print(f"Call initiated with SID: {call.sid}")

# Example usage
if __name__ == "__main__":
    phone_number = '+14156361256'  # The phone number to call
    message = 'Dear Aryan, An alert has been triggered for Aliyan at 10:15 PM. Fall detected in the common area. Staff have been notified and are responding. Please contact the care facility for more details or to speak with Aliyan. Your peace of mind is our priority. - CareSafe AI Monitoring Team'
    send_emergency_call(phone_number, message)
