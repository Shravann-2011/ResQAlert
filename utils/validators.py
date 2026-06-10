import re

def validate_email(email):
    """Validate email address format"""
    import re
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return {"valid": False, "message": "❌ Email is required"}
    
    if not re.match(email_pattern, email):
        return {"valid": False, "message": "❌ Invalid email format. Use: name@example.com"}
    
    if len(email) > 100:
        return {"valid": False, "message": "❌ Email too long (max 100 characters)"}
    
    return {"valid": True, "message": "✅ Valid email"}

def validate_phone(phone):
    """Validate phone number format"""
    import re
    
    if not phone:
        return {"valid": False, "message": "❌ Phone number is required"}
    
    # Remove all spaces, dashes, parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check for E.164 format (+country code + number)
    if not phone_clean.startswith('+'):
        return {
            "valid": False,
            "message": "❌ Phone must start with + and country code",
            "hint": "Example for India: +919008769230"
        }
    
    # Remove + for length check
    phone_digits = phone_clean[1:]
    
    # Check if only digits after +
    if not phone_digits.isdigit():
        return {
            "valid": False,
            "message": "❌ Phone can only contain digits after +",
            "hint": "Format: +[country code][number]"
        }
    
    # Check length (international phone numbers are 10-15 digits)
    if len(phone_digits) < 10:
        return {
            "valid": False,
            "message": "❌ Phone number too short (min 10 digits)",
            "hint": "Include country code. Example: +919008769230"
        }
    
    if len(phone_digits) > 15:
        return {
            "valid": False,
            "message": "❌ Phone number too long (max 15 digits)"
        }
    
    # Special check for Indian numbers
    if phone_clean.startswith('+91'):
        if len(phone_digits) != 12:  # 91 + 10 digits
            return {
                "valid": False,
                "message": "❌ Indian numbers must be 10 digits after +91",
                "hint": "Format: +91XXXXXXXXXX (10 digits)"
            }
    
    return {"valid": True, "message": "✅ Valid phone number"}
