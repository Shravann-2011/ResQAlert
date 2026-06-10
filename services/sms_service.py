"""
SMS Alert Service using Twilio - Enhanced Error Handling
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException
from config.settings import settings
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class SMSAlertService:
    def __init__(self):
        """Initialize Twilio client"""
        self.client = None
        self.account_sid = None
        self.auth_token = None
        self.from_number = None
        self.is_configured = False
        self.is_trial_account = False
        self.verified_numbers = []
        
        try:
            # Get credentials from settings
            self.account_sid = settings.TWILIO_ACCOUNT_SID
            self.auth_token = settings.TWILIO_AUTH_TOKEN
            self.from_number = settings.TWILIO_PHONE_NUMBER
            
            # Validate credentials
            if not self._validate_credentials():
                logger.error("❌ Twilio credentials validation failed")
                return
            
            # Initialize Twilio client
            self.client = Client(self.account_sid, self.auth_token)
            
            # Test connection
            if self._test_connection():
                self.is_configured = True
                logger.info("✅ SMS Service initialized successfully")
                self._get_account_details()
            else:
                logger.error("❌ SMS Service connection test failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize SMS service: {e}")
    
    def _validate_credentials(self) -> bool:
        """Validate Twilio credentials"""
        if not self.account_sid or not self.auth_token or not self.from_number:
            return False
        
        if not self.account_sid.startswith('AC') or len(self.account_sid) != 34:
            return False
        
        if len(self.auth_token) != 32:
            return False
        
        return True
    
    def _test_connection(self) -> bool:
        """Test Twilio connection"""
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            logger.info(f"✅ Connected to Twilio: {account.friendly_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def _get_account_details(self):
        """Get account details and verified numbers"""
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            self.is_trial_account = account.status == 'trial'
            
            # Get verified numbers
            try:
                caller_ids = self.client.outgoing_caller_ids.list(limit=50)
                self.verified_numbers = [caller_id.phone_number for caller_id in caller_ids]
                logger.info(f"✅ Found {len(self.verified_numbers)} verified numbers")
            except Exception as e:
                logger.warning(f"Could not fetch verified numbers: {e}")
                self.verified_numbers = []
                
        except Exception as e:
            logger.error(f"Error getting account details: {e}")
    
    def _get_user_friendly_error(self, error: TwilioRestException) -> Dict:
        """Convert Twilio error codes to user-friendly messages"""
        error_code = error.code
        
        # Common Twilio error codes with helpful explanations
        error_messages = {
            21211: {
                "title": "Invalid Phone Number Format",
                "message": "The phone number format is incorrect.",
                "solution": "Use E.164 format: +[country code][number]\nExample for India: +919008769230"
            },
            21408: {
                "title": "Permission Denied",
                "message": "Cannot send SMS to this destination number.",
                "solution": "Check that:\n• Geographic permissions are enabled in Twilio Console\n• The destination country is allowed\n• Your Twilio account has proper permissions"
            },
            21606: {
                "title": "Invalid From Number",
                "message": "The 'From' phone number is not valid or not SMS-capable.",
                "solution": "Verify that your Twilio phone number:\n• Is correct in your .env file\n• Is SMS-capable\n• Is properly configured in Twilio Console"
            },
            21614: {
                "title": "Invalid Mobile Number",
                "message": "The 'To' number is not a valid mobile number.",
                "solution": "Ensure the recipient number:\n• Is a mobile phone (not landline)\n• Is in correct E.164 format\n• Includes country code"
            },
            30044: {
                "title": "Trial Account - Number Not Verified",
                "message": "For Twilio trial accounts, you can only send SMS to verified numbers.",
                "solution": "Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified\n• Click 'Add a new Caller ID'\n• Enter the recipient's phone number\n• Complete verification process"
            },
            21612: {
                "title": "Cannot Route to Phone Number",
                "message": "The 'To' number cannot receive SMS messages.",
                "solution": "Check that:\n• The number is SMS-capable\n• The carrier supports SMS\n• The number is not on a blocklist"
            },
            20003: {
                "title": "Authentication Error",
                "message": "Your Twilio credentials are incorrect.",
                "solution": "Verify your .env file has:\n• Correct TWILIO_ACCOUNT_SID\n• Correct TWILIO_AUTH_TOKEN\nGet credentials from: https://console.twilio.com/"
            },
            21610: {
                "title": "Message Blocked",
                "message": "Message was blocked (spam filter or carrier restrictions).",
                "solution": "Try:\n• Simplifying message text\n• Removing URLs and special characters\n• Using verified sender ID"
            },
            63016: {
                "title": "Geographic Permission Denied",
                "message": "Your account doesn't have permission to send SMS to this country.",
                "solution": "Enable geographic permissions:\n1. Go to Twilio Console\n2. Navigate to Messaging > Settings > Geo Permissions\n3. Enable the target country"
            }
        }
        
        # Get specific error info or use default
        error_info = error_messages.get(error_code, {
            "title": f"Twilio Error {error_code}",
            "message": str(error.msg),
            "solution": "Check Twilio documentation or console for more details."
        })
        
        # Add trial account hint if applicable
        if self.is_trial_account and error_code in [21408, 30044, 21612]:
            error_info["trial_hint"] = (
                "⚠️ TRIAL ACCOUNT DETECTED\n"
                "Trial accounts can only send to verified numbers.\n"
                "Verify numbers at: https://console.twilio.com/"
            )
        
        return {
            "status": "error",
            "error_code": error_code,
            "error_title": error_info["title"],
            "error_message": error_info["message"],
            "solution": error_info["solution"],
            "trial_hint": error_info.get("trial_hint"),
            "raw_error": str(error)
        }
    
    def _format_phone_number(self, phone: str) -> Optional[str]:
        """Format phone number correctly with validation"""
        # Remove all non-digit characters except +
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        # Handle different formats for Indian numbers
        if phone_clean.startswith('+91') and len(phone_clean) == 13:
            return phone_clean
        elif phone_clean.startswith('91') and len(phone_clean) == 12:
            return '+' + phone_clean
        elif len(phone_clean) == 10:
            return '+91' + phone_clean
        elif phone_clean.startswith('+') and len(phone_clean) >= 10:
            # Other countries in E.164 format
            return phone_clean
        else:
            return None
    
    def send_test_message(self, to_number: str) -> Dict:
        """Send test SMS message with enhanced error handling"""
        if not self.is_configured:
            return {
                "status": "error",
                "message": "SMS service not configured. Check your .env file for Twilio credentials."
            }
        
        # Validate and format phone number
        formatted_number = self._format_phone_number(to_number)
        if not formatted_number:
            return {
                "status": "error",
                "message": f"Invalid phone number format: '{to_number}'",
                "solution": "Use E.164 format: +[country code][number]\nExample: +919008769230"
            }
        
        # Check if trial account and number is verified
        if self.is_trial_account and formatted_number not in self.verified_numbers:
            return {
                "status": "error",
                "error_code": "TRIAL_UNVERIFIED",
                "message": f"Trial account: '{formatted_number}' is not verified.",
                "solution": (
                    "For trial accounts, verify the number first:\n"
                    "1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified\n"
                    "2. Click 'Add a new Caller ID'\n"
                    "3. Enter and verify the number"
                ),
                "verified_numbers": self.verified_numbers
            }
        
        try:
            message_body = f"""🚨 ResQAlert Test Alert

✅ SMS system working!
📱 Service: Active
🤖 AI Models: Ready
🌐 Monitoring: Online

Test: {datetime.now().strftime('%d/%m %H:%M')}

Stay safe!
- ResQAlert"""
            
            # Send message
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=formatted_number
            )
            
            logger.info(f"✅ Test SMS sent: {message.sid}")
            
            return {
                "status": "success",
                "message_sid": message.sid,
                "to": formatted_number,
                "message": "Test SMS sent successfully!",
                "sent_at": datetime.now()
            }
            
        except TwilioRestException as e:
            # Get user-friendly error message
            error_info = self._get_user_friendly_error(e)
            logger.error(f"❌ Twilio error {e.code}: {e.msg}")
            return error_info
            
        except Exception as e:
            logger.error(f"❌ Unexpected error sending test SMS: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def send_disaster_alert(self, to_number: str, disaster_type: str, risk_level: str,
                          location: str, risk_score: float) -> Dict:
        """Send disaster alert SMS with enhanced error handling"""
        if not self.is_configured:
            return {
                "status": "error",
                "message": "SMS service not configured. Check your .env file."
            }
        
        # Validate and format phone number
        formatted_number = self._format_phone_number(to_number)
        if not formatted_number:
            return {
                "status": "error",
                "message": f"Invalid phone number format: '{to_number}'",
                "solution": "Use E.164 format: +[country code][number]"
            }
        
        # Check trial account restrictions
        if self.is_trial_account and formatted_number not in self.verified_numbers:
            return {
                "status": "error",
                "error_code": "TRIAL_UNVERIFIED",
                "message": f"Cannot send to unverified number: {formatted_number}",
                "solution": "Verify this number in Twilio Console first."
            }
        
        try:
            # Create disaster alert message
            message_text = self._create_alert_message(disaster_type, risk_level, location, risk_score)
            
            # Send SMS
            twilio_message = self.client.messages.create(
                body=message_text,
                from_=self.from_number,
                to=formatted_number
            )
            
            logger.info(f"✅ Disaster alert sent: {twilio_message.sid}")
            
            return {
                "status": "success",
                "message_sid": twilio_message.sid,
                "to": formatted_number,
                "message": message_text,
                "sent_at": datetime.now()
            }
            
        except TwilioRestException as e:
            # Get user-friendly error message
            error_info = self._get_user_friendly_error(e)
            logger.error(f"❌ Twilio error {e.code}: {e.msg}")
            return error_info
            
        except Exception as e:
            logger.error(f"❌ Unexpected error sending disaster alert: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def _create_alert_message(self, disaster_type: str, risk_level: str,
                            location: str, risk_score: float) -> str:
        """Create SMS-filter-safe alert message"""
        # Use neutral language that passes SMS filters
        alert_types = {
            'flood': 'Rain Advisory',
            'drought': 'Weather Notice',
            'heatwave': 'Heat Advisory'
        }
        
        safety_tips = {
            'flood': 'Stay indoors. Check local conditions.',
            'drought': 'Monitor water usage.',
            'heatwave': 'Stay cool. Drink water regularly.'
        }
        
        alert_name = alert_types.get(disaster_type, 'Weather Advisory')
        safety_tip = safety_tips.get(disaster_type, 'Follow safety guidelines.')
        
        # Simple, filter-safe message (no emojis in critical alerts)
        message = f"""ResQAlert Weather Update

{alert_name}: {risk_level}
Area: {location}
Level: {risk_score:.1f}

Recommendation: {safety_tip}

Emergency help: 108
Time: {datetime.now().strftime('%d/%m %H:%M')}

ResQAlert Team"""
        
        return message
    
    def get_message_status(self, message_sid: str) -> dict:
        """Check message delivery status with enhanced error info"""
        if not self.client:
            return {"status": "error", "message": "SMS service not configured"}
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            # Map Twilio status to user-friendly status
            status_map = {
                "queued": "📤 Queued for sending",
                "sent": "📨 Sent to carrier",
                "delivered": "✅ Delivered successfully",
                "failed": "❌ Delivery failed",
                "undelivered": "❌ Not delivered",
                "receiving": "📥 Receiving",
                "received": "✅ Received"
            }
            
            friendly_status = status_map.get(message.status, message.status)
            
            result = {
                "status": "success",
                "message_sid": message_sid,
                "to": message.to,
                "delivery_status": message.status,
                "friendly_status": friendly_status,
                "date_sent": message.date_sent
            }
            
            # Add error details if delivery failed
            if message.error_code:
                result["error_code"] = message.error_code
                result["error_message"] = message.error_message
                
                # Provide solution for common delivery failures
                if message.error_code == 30044:
                    result["solution"] = "Number not verified. Verify in Twilio Console."
                elif message.error_code == 30008:
                    result["solution"] = "Unknown destination number or carrier issue."
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"Could not get status: {str(e)}"}
    
    def get_account_info(self) -> dict:
        """Get account information"""
        if not self.client or not self.is_configured:
            return {"status": "error", "message": "SMS service not configured"}
        
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            
            # Refresh verified numbers
            try:
                caller_ids = self.client.outgoing_caller_ids.list(limit=50)
                self.verified_numbers = [caller_id.phone_number for caller_id in caller_ids]
            except:
                pass
            
            return {
                "status": "success",
                "account_name": account.friendly_name,
                "account_status": account.status,
                "phone_number": self.from_number,
                "is_trial": account.status == 'trial',
                "verified_numbers": self.verified_numbers,
                "verified_count": len(self.verified_numbers)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to get account info: {str(e)}"}

# Create global SMS service instance
sms_service = SMSAlertService()
