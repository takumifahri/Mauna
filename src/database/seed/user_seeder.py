from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

# Import dari project modules dengan try-except untuk robustness
try:
    from src.models.user import User, UserRole
    from src.config.hash import hash_password
    from src.database.seeder import BaseSeeder
except ImportError:
    # Fallback ke relative imports jika absolute gagal
    from ...models.user import User, UserRole
    from ...config.hash import hash_password
    from ..seeder import BaseSeeder

class UserSeeder(BaseSeeder):
    """Seed initial users into the database"""
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """Run user seeding"""
        try:
            print("🌱 Seeding users...")
            
            users_data = [
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": "AdminPass123!",
                    "nama" : "Site Admin",
                    "telpon": "123-456-7890",
                    "role": UserRole.ADMIN,
                    "is_active": True,
                    "is_verified": True,
                    "bio": "Administrator account"
                },
                {
                    "username": "moderator",
                    "email": "moderator@example.com",
                    "password": "ModPass123!",
                    "nama": "Site Moderator",
                    "telpon": "098-765-4321",
                    "role": UserRole.MODERATOR,
                    "is_active": True,
                    "is_verified": True,
                    "bio": "Moderator account"
                },
                {
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "password": "Password123",
                    "nama": "John Doe",
                    "telpon": "123-456-7890",
                    "role": UserRole.USER,
                    "is_active": True,
                    "is_verified": False,
                    "bio": "Sample user account"
                },
                {
                    "username": "janedoe",
                    "email": "jane.doe@example.com",
                    "password": "Password123",
                    "nama": "Jane Doe",
                    "telpon": "321-654-0987",
                    "role": UserRole.USER,
                    "is_active": True,
                    "is_verified": True,
                    "bio": "Another sample user"
                }
            ]
            
            created_count = 0
            for user_data in users_data:
                existing_user = self.db.query(User).filter(
                    (User.email == user_data["email"]) | 
                    (User.username == user_data["username"])
                ).first()
                
                if not existing_user:
                    # Hash password before creating user
                    user_data["password"] = hash_password(user_data["password"])
                    
                    user = User(**user_data)
                    self.db.add(user)
                    created_count += 1
                    print(f"  ✅ Created user: {user_data['username']} ({user_data['email']})")
                else:
                    print(f"  ⚠️ User already exists: {user_data['username']} ({user_data['email']})")
            
            self.db.commit()
            print(f"✅ User seeding completed. Created {created_count} new users.")
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"User seeding failed: {e}")

# Utility functions tetap sama...
def create_user_if_not_exists(db: Session, data: Dict[str, Any]) -> User:
    """Helper function: Create a user if email/username not present."""
    existing = db.query(User).filter(
        (User.email == data["email"]) | (User.username == data["username"])
    ).first()
    
    if existing:
        return existing

    if not data["password"].startswith("$2b$"):
        data["password"] = hash_password(data["password"])

    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def seed_users(db: Session) -> List[User]:
    """Legacy function - use UserSeeder class instead"""
    seeder = UserSeeder()
    seeder.db = db
    seeder.run()
    return db.query(User).all()