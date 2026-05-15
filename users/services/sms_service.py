import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone, message):
    """
    Sends SMS using devsms.uz API using the requests library.
    Better handled on PythonAnywhere due to automatic proxy detection.
    """
    url = "https://devsms.uz/api/send_sms.php"
    token = getattr(settings, "DEVSMS_TOKEN", "")
    
    if not token:
        logger.error("DEVSMS_TOKEN is not set in settings or .env")
        return False
    
    # Ensure phone number is in correct format (e.g., 998945052402)
    clean_phone = "".join(filter(str.isdigit, phone))
    
    payload = {
        "phone": clean_phone,
        "message": message
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # PythonAnywhere environment variables for proxy are automatically picked up by requests
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"SMS sent to {clean_phone}. Response: {result}")
            return True
        else:
            logger.error(f"Failed to send SMS to {clean_phone}: HTTP {response.status_code}. Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send SMS to {clean_phone}: {str(e)}")
        return False
