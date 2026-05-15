import json
import logging
import urllib.parse
import urllib.request
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone, message):
    """
    Sends SMS using devsms.uz API.
    """
    url = "https://devsms.uz/api/send_sms.php"
    token = getattr(settings, "DEVSMS_TOKEN", "")
    
    if not token:
        logger.error("DEVSMS_TOKEN is not set in settings or .env")
        return False
        
    # Ensure phone number is in correct format (e.g., 998945052402)
    # The API example shows 998... format.
    clean_phone = "".join(filter(str.isdigit, phone))
    
    payload = {
        "phone": clean_phone,
        "message": message
    }
    
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = response.read().decode("utf-8")
            logger.info(f"SMS sent to {clean_phone}. Response: {result}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        logger.error(f"Failed to send SMS to {clean_phone}: HTTP Error {e.code}: {e.reason}. Response body: {error_body}")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS to {clean_phone}: {str(e)}")
        return False
