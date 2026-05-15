import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paylog.settings")
django.setup()

from users.services.sms_service import send_sms

def test_sms_sending():
    # Test phone number (use the one from the example)
    phone = "998945052402"
    message = "Test message from Paylog"
    
    print(f"Testing SMS sending to {phone}...")
    success = send_sms(phone, message)
    
    if success:
        print("SMS request sent successfully (check logs for response).")
    else:
        print("Failed to send SMS request.")

if __name__ == "__main__":
    test_sms_sending()
