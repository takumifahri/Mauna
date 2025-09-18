"""
CLI Commands for SMT 5 FastAPI Application
Usage: python cli.py <command>
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from src.database.seeder import run_all_seeders, run_seeder
from src.database.db import db_config, Base
from sqlalchemy import text

def reset_alembic():
    """Reset alembic migration files"""
    try:
        versions_path = Path("alembic/versions")
        
        if versions_path.exists():
            # Hapus semua file migration kecuali __init__.py
            for file in versions_path.glob("*.py"):
                if file.name is not "__init__.py":
                    file.unlink()
                    print(f"🗑️ Removed migration: {file.name}")
            
            # Pastikan __init__.py ada
            init_file = versions_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
        
        print("✅ Alembic migration files reset")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting alembic: {e}")
        return False

def drop_all_tables():
    """Drop all tables in database including alembic_version"""
    try:
        print("🗑️ Dropping all tables...")
        
        with db_config.engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Drop all tables and recreate schema
                conn.execute(text("""
                    DROP SCHEMA public CASCADE;
                    CREATE SCHEMA public;
                    GRANT ALL ON SCHEMA public TO postgres;
                    GRANT ALL ON SCHEMA public TO public;
                """))
                
                # Commit transaction
                trans.commit()
                print("✅ All tables and schema dropped successfully")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error in transaction: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False

def run_alembic_command(command_args):
    """Run alembic command"""
    try:
        result = subprocess.run(['alembic'] + command_args, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Alembic command failed: {' '.join(command_args)}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def migrate_fresh():
    """Drop all tables and re-run migrations"""
    try:
        print("🔄 Starting fresh migration...")
        
        # Step 1: Drop all tables
        print("📋 Step 1: Dropping all tables and recreating schema...")
        if not drop_all_tables():
            return False
        
        # Step 2: Reset alembic migration files
        print("📋 Step 2: Resetting alembic migration files...")
        if not reset_alembic():
            return False
        
        # Step 3: Create fresh migration
        print("📋 Step 3: Creating fresh migration...")
        if not run_alembic_command(['revision', '--autogenerate', '-m', 'Initial migration']):
            return False
        
        # Step 4: Apply migration
        print("📋 Step 4: Applying migration...")
        if not run_alembic_command(['upgrade', 'head']):
            return False
        
        print("✅ Fresh migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Fresh migration failed: {e}")
        return False

def migrate_fresh_seed():
    """Fresh migration with seeders"""
    try:
        print("🔄 Starting fresh migration with seeders...")
        
        # Run fresh migration
        if migrate_fresh():
            print("🌱 Running seeders...")
            run_all_seeders()
            print("✅ Fresh migration with seeders completed!")
        else:
            print("❌ Fresh migration failed, skipping seeders")
            
    except Exception as e:
        print(f"❌ Fresh migration with seeders failed: {e}")

def show_help():
    """Show available commands"""
    print("""
SMT 5 CLI Commands:

Migration Commands (Alembic):
  migrate                    Run pending migrations
  migrate:create <message>   Create new migration
  migrate:upgrade           Upgrade to latest migration  
  migrate:downgrade         Downgrade one migration
  migrate:fresh             Drop all tables and re-run migrations
  migrate:fresh-seed        Fresh migration with seeders
  migrate:history           Show migration history
  migrate:current           Show current migration
  migrate:reset             Reset to base (downgrade all)

Seeder Commands:
  db:seed                   Run all database seeders
  db:seed <SeederName>      Run specific seeder

Development Commands:
  dev                       Start development server

Examples:
  python cli.py migrate:create "Add new column to users"
  python cli.py migrate:fresh
  python cli.py migrate:fresh-seed
  python cli.py migrate
  python cli.py db:seed
  python cli.py dev
    """)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    try:
        # Migration commands using Alembic
        if command == 'migrate':
            print("🔄 Running migrations...")
            run_alembic_command(['upgrade', 'head'])
            
        elif command == 'migrate:create':
            if len(sys.argv) < 3:
                print("❌ Please provide migration message")
                print("Example: python cli.py migrate:create 'Create users table'")
                return
            message = sys.argv[2]
            print(f"📝 Creating migration: {message}")
            run_alembic_command(['revision', '--autogenerate', '-m', message])
            
        elif command == 'migrate:upgrade':
            print("⬆️ Upgrading to latest migration...")
            run_alembic_command(['upgrade', 'head'])
            
        elif command == 'migrate:downgrade':
            print("⬇️ Downgrading one migration...")
            run_alembic_command(['downgrade', '-1'])
            
        elif command == 'migrate:fresh':
            migrate_fresh()
            
        elif command == 'migrate:fresh-seed':
            migrate_fresh_seed()
            
        elif command == 'migrate:history':
            print("📋 Migration history:")
            run_alembic_command(['history'])
            
        elif command == 'migrate:current':
            print("📍 Current migration:")
            run_alembic_command(['current'])
            
        elif command == 'migrate:reset':
            print("🔄 Resetting all migrations...")
            run_alembic_command(['downgrade', 'base'])
            
        # Seeder commands
        elif command == 'db:seed':
            if len(sys.argv) > 2:
                # Specific seeder
                seeder_name = sys.argv[2]
                print(f"🌱 Running seeder: {seeder_name}")
                run_seeder(seeder_name)
            else:
                # All seeders
                print("🌱 Running all seeders...")
                run_all_seeders()
                
        # Development commands
        elif command == 'dev':
            print("🚀 Starting development server...")
            subprocess.run(['uvicorn', 'src.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'])
            
        elif command == 'help' or command == '--help' or command == '-h':
            show_help()
            
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()