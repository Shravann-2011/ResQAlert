"""
User management system for ResQAlert
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database.models import User, SessionLocal
from sqlalchemy.exc import IntegrityError
import re
import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.db = SessionLocal()
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate Indian phone number format"""
        # Remove spaces and special characters
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        # Check for valid Indian mobile number patterns
        patterns = [
            r'^\+91[6-9]\d{9}$',  # +91xxxxxxxxxx
            r'^91[6-9]\d{9}$',    # 91xxxxxxxxxx
            r'^[6-9]\d{9}$'       # xxxxxxxxxx
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone_clean):
                return True
        return False
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        # Add +91 if not present
        if phone_clean.startswith('+91'):
            return phone_clean
        elif phone_clean.startswith('91') and len(phone_clean) == 12:
            return '+' + phone_clean
        elif len(phone_clean) == 10:
            return '+91' + phone_clean
        else:
            return phone_clean
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def register_user(self, name: str, email: str, phone: str, location_name: str, 
                     lat: float, lon: float) -> dict:
        """Register new user for alerts"""
        try:
            # Validate inputs
            if not self.validate_email(email):
                return {"status": "error", "message": "Invalid email format"}
            
            if not self.validate_phone_number(phone):
                return {"status": "error", "message": "Invalid phone number. Use format: +91xxxxxxxxxx"}
            
            # Format phone number
            formatted_phone = self.format_phone_number(phone)
            
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                return {"status": "error", "message": "User with this email already exists"}
            
            # Create new user
            new_user = User(
                name=name,
                email=email,
                phone=formatted_phone,
                latitude=lat,
                longitude=lon,
                location_name=location_name,
                alert_preferences='{"sms": true, "email": true}',  # JSON string
                created_at=datetime.utcnow()
            )
            
            self.db.add(new_user)
            self.db.commit()
            
            logger.info(f"User registered successfully: {email}")
            return {
                "status": "success", 
                "message": "Registration successful! You will receive disaster alerts.",
                "user_id": new_user.id
            }
        
        except IntegrityError:
            self.db.rollback()
            return {"status": "error", "message": "User with this email already exists"}
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering user: {e}")
            return {"status": "error", "message": f"Registration failed: {str(e)}"}
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_users_in_area(self, center_lat: float, center_lon: float, radius_km: float = 50):
        """Get all users within a specific radius (simplified)"""
        try:
            # Simplified radius calculation (for production, use proper geospatial queries)
            lat_range = radius_km / 111.0  # Approximate km to degrees
            lon_range = radius_km / (111.0 * abs(center_lat) * 0.017453)
            
            users = self.db.query(User).filter(
                User.latitude.between(center_lat - lat_range, center_lat + lat_range),
                User.longitude.between(center_lon - lon_range, center_lon + lon_range)
            ).all()
            
            return users
        
        except Exception as e:
            logger.error(f"Error getting users in area: {e}")
            return []
    
    def update_user_preferences(self, user_id: int, preferences: dict):
        """Update user alert preferences"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.alert_preferences = str(preferences)  # Convert to string
                self.db.commit()
                return {"status": "success", "message": "Preferences updated"}
            else:
                return {"status": "error", "message": "User not found"}
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating preferences: {e}")
            return {"status": "error", "message": f"Update failed: {str(e)}"}
    
    def get_all_users(self):
        """Get all registered users"""
        try:
            return self.db.query(User).all()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

# Global user manager instance
user_manager = UserManager()
