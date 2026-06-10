"""
Configuration settings for ResQAlert system
"""
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        # Application Settings
        self.APP_NAME = "ResQAlert - AI Disaster Prediction System"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
        self.GEMINI_MODEL = 'gemini-2.5-pro'  # Fast and free model
        
        # Database Settings
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///resqalert.db")
        
        # Weather API Settings
        self.OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
        self.WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"
        self.WEATHER_UPDATE_INTERVAL = 300  # 5 minutes in seconds
        
        # Twilio SMS Settings
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") 
        self.TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        
        # SendGrid Email Settings
        self.SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
        self.FROM_EMAIL = os.getenv("FROM_EMAIL", "alerts@resqalert.com")
        
        # Validate critical settings
        self._validate_settings()
        
        # Alert Settings
        self.ALERT_THRESHOLDS = {
            'flood': {'low': 0.3, 'medium': 0.6, 'high': 0.8},
            'drought': {'low': 0.3, 'medium': 0.6, 'high': 0.8},
            'heatwave': {'low': 0.3, 'medium': 0.6, 'high': 0.8}
        }
        
        # Safe Zone Settings
        self.SAFE_ZONE_RADIUS = 50  # kilometers
        self.MAX_SAFE_ZONES = 10
        
        # Chatbot Settings
        self.MAX_CONVERSATION_HISTORY = 10
        self.CHATBOT_CONFIDENCE_THRESHOLD = 0.7
    
    def _validate_settings(self):
        """Validate that required settings are present with detailed error messages"""
        errors = []
        warnings = []
        
        # Check OpenWeatherMap API key
        if not self.OPENWEATHER_API_KEY:
            errors.append("❌ OPENWEATHER_API_KEY not found in .env file")
            errors.append("   → Get free API key at: https://openweathermap.org/api")
        elif self.OPENWEATHER_API_KEY in ["your_openweather_api_key_here", "your_actual_openweather_api_key_here"]:
            errors.append("❌ OPENWEATHER_API_KEY is still using placeholder value")
            errors.append("   → Replace with your actual API key from OpenWeatherMap")
        else:
            logger.info("✅ OpenWeatherMap API key configured")
        
        # Check Twilio settings (optional but recommended)
        twilio_missing = []
        if not self.TWILIO_ACCOUNT_SID or self.TWILIO_ACCOUNT_SID in ["your_twilio_account_sid_here", "your_actual_twilio_account_sid"]:
            twilio_missing.append("TWILIO_ACCOUNT_SID")
        
        if not self.TWILIO_AUTH_TOKEN or self.TWILIO_AUTH_TOKEN in ["your_twilio_auth_token_here", "your_actual_twilio_auth_token_here"]:
            twilio_missing.append("TWILIO_AUTH_TOKEN")
        
        if not self.TWILIO_PHONE_NUMBER or self.TWILIO_PHONE_NUMBER in ["your_twilio_phone_number", "your_actual_twilio_phone_number", "+1234567890"]:
            twilio_missing.append("TWILIO_PHONE_NUMBER")
        
        if twilio_missing:
            warnings.append(f"⚠️  Twilio SMS not configured - Missing: {', '.join(twilio_missing)}")
            warnings.append("   → SMS alerts will be disabled")
            warnings.append("   → Sign up at: https://www.twilio.com/try-twilio")
            warnings.append("   → For trial accounts, verify numbers at: https://console.twilio.com/")
        else:
            logger.info("✅ Twilio SMS credentials configured")
        
        # Check SendGrid settings (optional)
        if not self.SENDGRID_API_KEY or self.SENDGRID_API_KEY in ["your_sendgrid_api_key_here", "your_actual_sendgrid_api_key"]:
            warnings.append("⚠️  SendGrid API key not configured (Email alerts disabled)")
        else:
            logger.info("✅ SendGrid API key configured")
        
        # Display errors (will stop app if critical errors exist)
        if errors:
            error_msg = "\n".join(errors)
            logger.error(f"\n{'='*60}\n⚠️  CONFIGURATION ERRORS:\n{'='*60}\n{error_msg}\n{'='*60}")
            logger.error("\n💡 Solution: Update your .env file with valid API keys")
            logger.error("📝 See .env.example for required format\n")
            raise ValueError(f"Missing required configuration. Please check your .env file.")
        
        # Display warnings (won't stop app)
        if warnings:
            warning_msg = "\n".join(warnings)
            logger.warning(f"\n{'='*60}\n⚠️  CONFIGURATION WARNINGS:\n{'='*60}\n{warning_msg}\n{'='*60}\n")
    
    def get_twilio_config(self) -> dict:
        """Get Twilio configuration for debugging"""
        return {
            "account_sid": self.TWILIO_ACCOUNT_SID,
            "auth_token": "***" + (self.TWILIO_AUTH_TOKEN[-4:] if self.TWILIO_AUTH_TOKEN else "None"),
            "phone_number": self.TWILIO_PHONE_NUMBER,
            "configured": bool(
                self.TWILIO_ACCOUNT_SID and 
                self.TWILIO_AUTH_TOKEN and 
                self.TWILIO_PHONE_NUMBER and
                self.TWILIO_ACCOUNT_SID not in ["your_twilio_account_sid_here", "your_actual_twilio_account_sid"] and
                self.TWILIO_AUTH_TOKEN not in ["your_twilio_auth_token_here", "your_actual_twilio_auth_token_here"] and
                self.TWILIO_PHONE_NUMBER not in ["your_twilio_phone_number", "your_actual_twilio_phone_number", "+1234567890"]
            )
        }

# Create global settings instance
settings = Settings()

# Print configuration status on import
if __name__ == "__main__":
    print("\n🔧 ResQAlert Configuration Status:")
    print("=" * 60)
    
    # Weather API
    weather_status = "✅ Configured" if settings.OPENWEATHER_API_KEY else "❌ Missing"
    print(f"Weather API: {weather_status}")
    if settings.OPENWEATHER_API_KEY:
        print(f"  → API Key: {settings.OPENWEATHER_API_KEY[:8]}...{settings.OPENWEATHER_API_KEY[-4:]}")
    
    # Twilio 
    twilio_config = settings.get_twilio_config()
    twilio_status = "✅ Configured" if twilio_config["configured"] else "❌ Not configured"
    print(f"\nTwilio SMS: {twilio_status}")
    
    if twilio_config["configured"]:
        print(f"  → Account SID: {twilio_config['account_sid'][:8]}...")
        print(f"  → Auth Token: {twilio_config['auth_token']}")
        print(f"  → Phone: {twilio_config['phone_number']}")
    
    # SendGrid
    email_configured = settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY not in ["your_sendgrid_api_key_here", "your_actual_sendgrid_api_key"]
    email_status = "✅ Configured" if email_configured else "⚠️  Not configured (Optional)"
    print(f"\nSendGrid Email: {email_status}")
    
    print("=" * 60)
    print("✅ Configuration loaded successfully!\n")
