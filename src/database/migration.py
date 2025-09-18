import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.exc import SQLAlchemyError
from .db import db_config, Base
from .seeder import run_all_seeders

class MigrationManager:
    """Migration manager similar to Laravel Artisan"""
    
    def __init__(self):
        self.engine = db_config.engine
        self.metadata = MetaData()
        
    def create_migration_table(self):
        """Create migrations table to track executed migrations"""
        try:
            # Bind metadata to engine
            self.metadata.bind = self.engine # type: ignore
            
            migration_table = Table(
                'migrations',
                self.metadata,
                Column('id', Integer, primary_key=True),
                Column('migration', String(255), unique=True),
                Column('batch', Integer),
                Column('executed_at', DateTime, default=datetime.utcnow),
                extend_existing=True  # Add this to avoid conflicts
            )
            
            self.metadata.create_all(self.engine)
            print("✅ Migration table created")
            
        except Exception as e:
            print(f"❌ Error creating migration table: {e}")
            raise
    
    def migrate(self):
        """Run all pending migrations"""
        try:
            print("🔄 Running migrations...")
            self.create_migration_table()
            
            # Create all tables from models
            Base.metadata.create_all(bind=self.engine)
            
            # Record migration
            self._record_migration("initial_migration")
            
            print("✅ Migration completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def migrate_fresh(self, with_seed=False):
        """Drop all tables and migrate fresh"""
        try:
            print("🔄 Running fresh migration...")
            
            # Drop all tables
            self._drop_all_tables()
            
            # Run migration
            if self.migrate():
                print("✅ Fresh migration completed")
                
                # Run seeders if requested
                if with_seed:
                    print("🌱 Running seeders...")
                    run_all_seeders()
                    print("✅ Fresh migration with seeders completed")
            else:
                print("❌ Fresh migration failed")
                
        except Exception as e:
            print(f"❌ Fresh migration failed: {e}")
            raise
    
    def migrate_fresh_seed(self):
        """Fresh migration with seeder"""
        self.migrate_fresh(with_seed=True)
    
    def migrate_rollback(self):
        """Rollback last migration batch"""
        try:
            print("↩️ Rolling back migrations...")
            self._drop_all_tables()
            print("✅ Rollback completed")
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            raise
    
    def migrate_reset(self):
        """Reset all migrations"""
        try:
            print("🔄 Resetting all migrations...")
            self._drop_all_tables()
            print("✅ Migration reset completed")
            
        except Exception as e:
            print(f"❌ Migration reset failed: {e}")
            raise
    
    def migrate_status(self):
        """Show migration status"""
        try:
            with self.engine.connect() as conn:
                # Check if migration table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'migrations'
                    )
                """))
                
                row = result.fetchone()
                if row and row[0]:
                    # Show executed migrations
                    migrations = conn.execute(text("SELECT migration, batch, executed_at FROM migrations ORDER BY executed_at"))
                    
                    print("=== Migration Status ===")
                    for migration in migrations:
                        print(f"✅ {migration.migration} (Batch: {migration.batch}) - {migration.executed_at}")
                    print("========================")
                else:
                    print("❌ No migrations table found")
                    
        except Exception as e:
            print(f"❌ Error checking migration status: {e}")
    
    def _drop_all_tables(self):
        """Drop all tables in database"""
        try:
            with self.engine.connect() as conn:
                # Disable foreign key checks temporarily
                conn.execute(text("SET session_replication_role = replica;"))
                
                # Get all table names
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                
                tables = [row[0] for row in result]
                
                # Drop each table
                for table in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"🗑️ Dropped table: {table}")
                
                # Re-enable foreign key checks
                conn.execute(text("SET session_replication_role = DEFAULT;"))
                conn.commit()
                
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            raise
    
    def _record_migration(self, migration_name):
        """Record executed migration"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO migrations (migration, batch, executed_at) 
                    VALUES (:migration, 1, :executed_at)
                    ON CONFLICT (migration) DO NOTHING
                """), {
                    'migration': migration_name,
                    'executed_at': datetime.utcnow()
                })
                conn.commit()
                
        except Exception as e:
            print(f"Warning: Could not record migration: {e}")

# Create global migration manager
migration_manager = MigrationManager()

# Convenience functions (unchanged)
def migrate():
    """Run migrations"""
    return migration_manager.migrate()

def migrate_fresh(with_seed=False):
    """Fresh migration"""
    migration_manager.migrate_fresh(with_seed)

def migrate_fresh_seed():
    """Fresh migration with seeders"""
    migration_manager.migrate_fresh_seed()

def migrate_rollback():
    """Rollback migrations"""
    migration_manager.migrate_rollback()

def migrate_reset():
    """Reset migrations"""
    migration_manager.migrate_reset()

def migrate_status():
    """Show migration status"""
    migration_manager.migrate_status()