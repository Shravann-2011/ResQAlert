"""
Alert Manager for ResQAlert - Fixed and Streamlined
"""
import streamlit as st
from services.sms_service import sms_service
from app.user_management import user_manager
from database.models import Alert, SessionLocal
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.db = SessionLocal()
    
    def should_send_alert(self, disaster_type: str, risk_level: str, risk_score: float) -> bool:
        """Determine if alert should be sent"""
        return risk_level in ['Medium', 'High'] or risk_score >= 0.5
    
    def send_disaster_alert(self, disaster_type: str, risk_level: str, risk_score: float,
                          location: str, lat: float, lon: float, weather_data: dict) -> dict:
        """Send disaster alerts to all registered users"""
        
        if not self.should_send_alert(disaster_type, risk_level, risk_score):
            return {
                "status": "skipped",
                "message": f"Risk level {risk_level} (score: {risk_score:.2f}) is below alert threshold",
                "risk_level": risk_level,
                "risk_score": risk_score
            }
        
        try:
            # Get all registered users
            all_users = user_manager.get_all_users()
            
            if not all_users:
                return {
                    "status": "no_users",
                    "message": "No users registered for alerts yet"
                }
            
            results = {
                "status": "success",
                "total_users": len(all_users),
                "sms_sent": 0,
                "sms_failed": 0,
                "details": []
            }
            
            # Send SMS to each user
            for user in all_users:
                if user.phone:
                    # THIS IS THE CORRECT METHOD CALL
                    sms_result = sms_service.send_disaster_alert(
                        to_number=user.phone,
                        disaster_type=disaster_type,
                        risk_level=risk_level,
                        location=location,
                        risk_score=risk_score
                    )
                    
                    if sms_result["status"] == "success":
                        results["sms_sent"] += 1
                        
                        # Log successful alert
                        self.log_alert(user.id, disaster_type, risk_level, "sms", 
                                     f"Alert sent for {disaster_type} risk in {location}")
                        
                        results["details"].append({
                            "user": user.name,
                            "phone": user.phone,
                            "status": "sent",
                            "message_id": sms_result.get("message_sid")
                        })
                    else:
                        results["sms_failed"] += 1
                        results["details"].append({
                            "user": user.name,
                            "phone": user.phone,
                            "status": "failed",
                            "error": sms_result.get("message", "Unknown error")
                        })
                else:
                    # User has no phone number
                    results["sms_failed"] += 1
                    results["details"].append({
                        "user": user.name,
                        "phone": "N/A",
                        "status": "failed",
                        "error": "No phone number registered"
                    })
            
            return results
        
        except Exception as e:
            logger.error(f"Error sending disaster alerts: {e}")
            return {
                "status": "error",
                "message": f"Alert system error: {str(e)}"
            }
    
    def log_alert(self, user_id: int, disaster_type: str, risk_level: str, 
                  alert_type: str, message: str):
        """Log alert in database"""
        try:
            alert = Alert(
                user_id=user_id,
                disaster_type=disaster_type,
                risk_level=risk_level,
                message=message,
                alert_type=alert_type,
                sent_at=datetime.utcnow(),
                status="sent"
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging alert: {e}")
    
    def get_alert_history(self, limit: int = 50):
        """Get recent alert history"""
        try:
            alerts = self.db.query(Alert).order_by(Alert.sent_at.desc()).limit(limit).all()
            return alerts
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []

# Global alert manager
alert_manager = AlertManager()
