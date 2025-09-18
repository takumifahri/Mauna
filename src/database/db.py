import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from dotenv import load_dotenv
from typing import Generator, Optional
from sqlalchemy.orm import sessionmaker, Session
# Load environment variables from a .env file
load_dotenv()

Base = declarative_base()

class DatabaseConfig:
    """Database configuration class to manage database connections and metadata."""

    def __init__(self):
        self.hostname = os.getenv("DATABASE_HOSTNAME", "localhost")
        self.port = os.getenv("DATABASE_PORT", "5432")
        self.username = os.getenv("DATABASE_USERNAME", "postgres")
        self.password = os.getenv("DATABASE_PASSWORD", "postgres")
        self.database_name = os.getenv("DATABASE_NAME", "mauna")
        
        # Validate required environment variables
        if not all([self.hostname, self.port, self.username, self.password, self.database_name]):
            raise ValueError("Missing required database configuration")
        
        # Construct database URL
        self.database_url = f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database_name}"
        
        # SQLAlchemy setup
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = Base  # Use the global Base
        
        # Async database for FastAPI
        self.database = Database(self.database_url)
        self.metadata = MetaData()
        
    # Kita ambil Datbaase yg diinginkan
    def get_db(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        db: Optional[Session] = None
        try:
            db = self.SessionLocal()
            yield db
        finally:
            if db is not None:
                db.close()
                
    async def connect_db(self):
        """Connect to the database."""
        try:
            await self.database.connect()
            print(f"✅ Database connected: {self.hostname}:{self.port}/{self.database_name}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    async def disconnect_db(self):
        """Disconnect from database (async)"""
        try:
            await self.database.disconnect()
            print("✅ Database disconnected")
        except Exception as e:
            print(f"❌ Error disconnecting database: {e}")
            
    async def test_connection(self):
        """Test database connection (async)"""
        try:
            await self.database.connect()
            query = "SELECT 1"
            result = await self.database.fetch_one(query)
            if result and result[0] == 1:
                print("✅ Database connection test successful")
            else:
                print("❌ Database connection test failed")
        except Exception as e:
            print(f"❌ Database connection test error: {e}")
        finally:
            await self.database.disconnect()
            
    def create_tables(self):
        """Create database tables based on the defined models."""
        try:
            self.Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            

# Create global database instance
db_config = DatabaseConfig()

# Export commonly used objects
engine = db_config.engine
SessionLocal = db_config.SessionLocal
database = db_config.database
metadata = db_config.metadata
get_db = db_config.get_db

# Export Base untuk Alembic
__all__ = ['db_config', 'Base', 'engine', 'SessionLocal', 'database', 'metadata', 'get_db']
