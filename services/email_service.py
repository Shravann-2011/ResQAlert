"""
Email Alert Service using SendGrid
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Subject, PlainTextContent, HtmlContent
from config.settings import settings
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class EmailAlertService:
    def __init__(self):
        """Initialize SendGrid client"""
        try:
            self.api_key = settings.SENDGRID_API_KEY
            self.from_email = settings.FROM_EMAIL
            
            if self.api_key and self.api_key != "your_actual_sendgrid_api_key":
                self.client = SendGridAPIClient(api_key=self.api_key)
                logger.info("Email service initialized successfully")
            else:
                self.client = None
                logger.warning("Email service not configured - no API key")
                
        except Exception as e:
            logger.error(f"Failed to initialize email service: {e}")
            self.client = None
    
    def send_disaster_alert_email(self, to_email: str, name: str, disaster_type: str, 
                                risk_level: str, location: str, risk_score: float,
                                weather_data: Dict) -> Dict:
        """
        Send detailed disaster alert email
        
        Args:
            to_email: Recipient email address
            name: Recipient name
            disaster_type: flood, drought, heatwave
            risk_level: Low, Medium, High
            location: Location name
            risk_score: Risk probability (0.0 to 1.0)
            weather_data: Current weather conditions
            
        Returns:
            Dictionary with status and message info
        """
        if not self.client:
            return {"status": "error", "message": "Email service not initialized"}
        
        try:
            # Create email content
            html_content = self._create_html_alert(name, disaster_type, risk_level, 
                                                 location, risk_score, weather_data)
            plain_content = self._create_plain_alert(name, disaster_type, risk_level,
                                                   location, risk_score, weather_data)
            
            # Create email message
            message = Mail(
                from_email=From(self.from_email, "ResQAlert System"),
                to_emails=To(to_email, name),
                subject=Subject(f"🚨 ResQAlert: {risk_level} {disaster_type.title()} Risk - {location}"),
                plain_text_content=PlainTextContent(plain_content),
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            response = self.client.send(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "to": to_email,
                "sent_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "error", "message": f"Email failed: {str(e)}"}
    
    def _create_html_alert(self, name: str, disaster_type: str, risk_level: str,
                          location: str, risk_score: float, weather_data: Dict) -> str:
        """Create HTML email content"""
        
        # Risk level colors
        risk_colors = {
            "High": "#dc3545",
            "Medium": "#ffc107", 
            "Low": "#28a745"
        }
        
        color = risk_colors.get(risk_level, "#6c757d")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-box {{ background: #f8f9fa; border-left: 4px solid {color}; padding: 15px; margin: 20px 0; }}
                .weather-data {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .actions {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: {color}; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 ResQAlert Disaster Warning</h1>
                    <h2>{disaster_type.title()} Risk: {risk_level}</h2>
                </div>
                
                <div class="content">
                    <h3>Hello {name},</h3>
                    
                    <div class="alert-box">
                        <h4>⚠️ Alert Details</h4>
                        <p><strong>Disaster Type:</strong> {disaster_type.title()}</p>
                        <p><strong>Risk Level:</strong> {risk_level}</p>
                        <p><strong>Location:</strong> {location}</p>
                        <p><strong>Risk Score:</strong> {risk_score:.2f} / 1.00</p>
                        <p><strong>Alert Time:</strong> {datetime.now().strftime('%d %B %Y, %H:%M:%S')}</p>
                    </div>
                    
                    <div class="weather-data">
                        <h4>🌤️ Current Weather Conditions</h4>
                        <p><strong>Temperature:</strong> {weather_data.get('temperature', 'N/A')}°C</p>
                        <p><strong>Humidity:</strong> {weather_data.get('humidity', 'N/A')}%</p>
                        <p><strong>Precipitation:</strong> {weather_data.get('precipitation', 'N/A')} mm</p>
                        <p><strong>Wind Speed:</strong> {weather_data.get('wind_speed', 'N/A')} km/h</p>
                        <p><strong>Pressure:</strong> {weather_data.get('pressure', 'N/A')} hPa</p>
                    </div>
                    
                    <div class="actions">
                        <h4>🛡️ Recommended Actions</h4>
                        {self._get_disaster_actions_html(disaster_type)}
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" class="btn">📱 View Full Dashboard</a>
                        <a href="#" class="btn">🗺️ Find Safe Zones</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Emergency Contacts: Fire: 101 | Police: 100 | Medical: 108</p>
                    <p>This alert was generated by ResQAlert AI Disaster Prediction System</p>
                    <p>© 2025 ResQAlert - Keeping Communities Safe</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_plain_alert(self, name: str, disaster_type: str, risk_level: str,
                           location: str, risk_score: float, weather_data: Dict) -> str:
        """Create plain text email content"""
        
        plain_text = f"""
ResQAlert - Disaster Warning Alert

Hello {name},

ALERT DETAILS:
- Disaster Type: {disaster_type.title()}
- Risk Level: {risk_level}
- Location: {location}
- Risk Score: {risk_score:.2f} / 1.00
- Alert Time: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}

CURRENT WEATHER CONDITIONS:
- Temperature: {weather_data.get('temperature', 'N/A')}°C
- Humidity: {weather_data.get('humidity', 'N/A')}%
- Precipitation: {weather_data.get('precipitation', 'N/A')} mm
- Wind Speed: {weather_data.get('wind_speed', 'N/A')} km/h
- Pressure: {weather_data.get('pressure', 'N/A')} hPa

RECOMMENDED ACTIONS:
{self._get_disaster_actions_text(disaster_type)}

EMERGENCY CONTACTS:
- Fire: 101
- Police: 100
- Medical: 108

Stay safe and prepared!

ResQAlert AI Disaster Prediction System
© 2025 ResQAlert - Keeping Communities Safe
        """
        
        return plain_text
    
    def _get_disaster_actions_html(self, disaster_type: str) -> str:
        """Get HTML formatted disaster-specific actions"""
        actions = {
            "flood": """
                <ul>
                    <li>Move to higher ground immediately</li>
                    <li>Avoid walking or driving through flood water</li>
                    <li>Stay indoors and monitor emergency broadcasts</li>
                    <li>Prepare emergency kit with food and water</li>
                    <li>Keep important documents in waterproof container</li>
                </ul>
            """,
            "drought": """
                <ul>
                    <li>Conserve water - fix leaks, limit usage</li>
                    <li>Stay hydrated - drink plenty of water</li>
                    <li>Limit outdoor activities during heat</li>
                    <li>Monitor local water restrictions</li>
                    <li>Prepare for potential water shortages</li>
                </ul>
            """,
            "heatwave": """
                <ul>
                    <li>Stay indoors during hottest hours (10am-6pm)</li>
                    <li>Drink water regularly, avoid alcohol</li>
                    <li>Wear light-colored, loose clothing</li>
                    <li>Use fans or air conditioning</li>
                    <li>Check on elderly neighbors and relatives</li>
                </ul>
            """
        }
        return actions.get(disaster_type, actions["flood"])
    
    def _get_disaster_actions_text(self, disaster_type: str) -> str:
        """Get plain text disaster-specific actions"""
        actions = {
            "flood": """
- Move to higher ground immediately
- Avoid walking or driving through flood water
- Stay indoors and monitor emergency broadcasts
- Prepare emergency kit with food and water
- Keep important documents in waterproof container
            """,
            "drought": """
- Conserve water - fix leaks, limit usage
- Stay hydrated - drink plenty of water
- Limit outdoor activities during heat
- Monitor local water restrictions
- Prepare for potential water shortages
            """,
            "heatwave": """
- Stay indoors during hottest hours (10am-6pm)
- Drink water regularly, avoid alcohol
- Wear light-colored, loose clothing
- Use fans or air conditioning
- Check on elderly neighbors and relatives
            """
        }
        return actions.get(disaster_type, actions["flood"])
    
    def send_test_email(self, to_email: str, name: str = "Test User") -> Dict:
        """Send test email to verify email service"""
        if not self.client:
            return {"status": "error", "message": "Email service not initialized"}
        
        try:
            test_weather = {
                'temperature': 28,
                'humidity': 75,
                'precipitation': 5,
                'wind_speed': 15,
                'pressure': 1013
            }
            
            return self.send_disaster_alert_email(
                to_email=to_email,
                name=name,
                disaster_type="flood",
                risk_level="Medium",
                location="Test Location",
                risk_score=0.65,
                weather_data=test_weather
            )
            
        except Exception as e:
            return {"status": "error", "message": f"Test email failed: {str(e)}"}

# Create global email service instance
email_service = EmailAlertService()
