"""
Database setup and initialization
"""
from database.models import create_tables, SessionLocal, User, Alert, SafeZone, WeatherData, DisasterPrediction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        # Create all tables
        create_tables()
        logger.info("✅ Database tables created successfully")
        
        # Create sample safe zones for Bangalore
        create_sample_safe_zones()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def create_sample_safe_zones():
    """Create sample safe zones for demonstration"""
    db = SessionLocal()
    
    try:
        # Check if safe zones already exist
        existing_zones = db.query(SafeZone).count()
        if existing_zones > 0:
            logger.info("✅ Safe zones already exist")
            return
        
        # Sample safe zones for Bangalore area
        sample_zones = [
            {
                'name': 'Manipal Hospital Whitefield',
                'location_type': 'hospital',
                'latitude': 12.9698,
                'longitude': 77.7500,
                'capacity': 500,
                'contact_number': '080-6969-8969',
                'address': 'HCMR Wing, Survey No. 10P & 12P, Kadugodi, Whitefield'
            },
            {
                'name': 'Brigade Millennium Community Center',
                'location_type': 'community_center',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'capacity': 1000,
                'contact_number': '080-2234-5678',
                'address': 'JP Nagar, Bangalore'
            },
            {
                'name': 'Government High School',
                'location_type': 'school',
                'latitude': 12.9352,
                'longitude': 77.6245,
                'capacity': 800,
                'contact_number': '080-3456-7890',
                'address': 'Electronic City, Bangalore'
            },
            {
                'name': 'Kanteerava Indoor Stadium',
                'location_type': 'sports',
                'latitude': 12.9692,
                'longitude': 77.5955,
                'capacity': 2000,
                'contact_number': '080-4567-8901',
                'address': 'Kasturba Road, Bangalore'
            },
            {
                'name': 'Fire Station - Koramangala',
                'location_type': 'emergency',
                'latitude': 12.9279,
                'longitude': 77.6271,
                'capacity': 100,
                'contact_number': '101',
                'address': 'Koramangala, Bangalore'
            }
        ]
        
        # Add safe zones to database
        for zone_data in sample_zones:
            safe_zone = SafeZone(**zone_data)
            db.add(safe_zone)
        
        db.commit()
        logger.info(f"✅ Created {len(sample_zones)} sample safe zones")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating safe zones: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🗄️ Initializing ResQAlert Database...")
    success = initialize_database()
    if success:
        print("✅ Database setup complete!")
    else:
        print("❌ Database setup failed!")
