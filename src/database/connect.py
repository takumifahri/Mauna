import os
from dotenv import load_dotenv
from .db import db_config

# Load environment variables
load_dotenv()

# JWT Configuration
class JWTConfig:
    """JWT configuration class"""
    
    def __init__(self):
        self.secret = os.getenv("SECRET_KEY", "your_jwt_secret_key")
        self.expiration = int(os.getenv("JWT_EXPIRATION", "3600"))
        self.algorithm = "HS256"
    
    def get_settings(self) -> dict:
        """Get JWT settings as dictionary"""
        return {
            "secret": self.secret,
            "expiration": self.expiration,
            "algorithm": self.algorithm
        }

# Create global JWT config instance
jwt_config = JWTConfig()

# Export database objects - Import dari db.py yang sudah diperbaiki
from .db import engine, SessionLocal, Base, database, metadata, get_db

# Export JWT settings
JWT_SECRET = jwt_config.secret
JWT_EXPIRATION = jwt_config.expiration
JWT_ALGORITHM = jwt_config.algorithm

# Database URL for external use
DATABASE_URL = db_config.database_url

# Connection functions
async def connect_db():
    """Connect to database"""
    await db_config.connect_db()

async def disconnect_db():
    """Disconnect from database"""
    await db_config.disconnect_db()

async def test_connection():
    """Test database connection"""
    return await db_config.test_connection()

def create_tables():
    """Create database tables"""
    db_config.create_tables()

def print_config():
    """Print configuration (for debugging)"""
    print("=== Database Configuration ===")
    print(f"Host: {db_config.hostname}")
    print(f"Port: {db_config.port}")
    print(f"Database: {db_config.database_name}")
    print(f"User: {db_config.username}")
    print(f"JWT Expiration: {JWT_EXPIRATION} seconds")
    print("===============================")