from sqlalchemy.orm import Session
from .db import db_config
from ..config.hash import hash_password, verify_password  # Ubah dari .hash
from ..models.user import User, UserRole
from datetime import datetime

class BaseSeeder:
    """Base seeder class"""
    
    def __init__(self):
        self.db = db_config.SessionLocal()
    
    def run(self):
        """Override this method in child classes"""
        raise NotImplementedError("Subclass must implement run method")
    
    def close(self):
        """Close database session"""
        self.db.close()

class UserSeeder(BaseSeeder):
    """User table seeder"""
    
    def run(self):
        try:
            users_data = [
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": hash_password("admin123"),
                    "first_name": "Admin",
                    "last_name": "User",
                    "role": UserRole.ADMIN,
                    "is_active": True,
                    "is_verified": True
                },
                {
                    "username": "user1",
                    "email": "user1@example.com", 
                    "password": hash_password("user123"),
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": UserRole.USER,
                    "is_active": True,
                    "is_verified": True
                },
                {
                    "username": "moderator",
                    "email": "moderator@example.com",
                    "password": hash_password("mod123"),
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "role": UserRole.MODERATOR,
                    "is_active": True,
                    "is_verified": True
                }
            ]
            
            for user_data in users_data:
                existing_user = self.db.query(User).filter(
                    User.email == user_data["email"]
                ).first()
                
                if not existing_user:
                    user = User(**user_data)
                    self.db.add(user)
            
            self.db.commit()
            print("✅ Users seeded successfully")
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ User seeding failed: {e}")

# Seeder registry
SEEDERS = [
    UserSeeder,
]

def run_all_seeders():
    """Run all registered seeders"""
    print("🌱 Starting database seeding...")
    
    for SeederClass in SEEDERS:
        try:
            print(f"🌱 Running {SeederClass.__name__}...")
            seeder = SeederClass()
            seeder.run()
            seeder.close()
        except Exception as e:
            print(f"❌ Seeder {SeederClass.__name__} failed: {e}")
    
    print("✅ Database seeding completed")

def run_seeder(seeder_name: str):
    """Run specific seeder"""
    seeder_map = {seeder.__name__: seeder for seeder in SEEDERS}
    
    if seeder_name in seeder_map:
        try:
            print(f"🌱 Running {seeder_name}...")
            seeder = seeder_map[seeder_name]()
            seeder.run()
            seeder.close()
            print(f"✅ {seeder_name} completed")
        except Exception as e:
            print(f"❌ {seeder_name} failed: {e}")
    else:
        print(f"❌ Seeder {seeder_name} not found")
        print(f"Available seeders: {list(seeder_map.keys())}")