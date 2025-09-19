## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials
```

## Migration Commands

```bash
# Create new migration
python cli.py migrate:create "Add new column to users table"

# Run pending migrations
python cli.py migrate

# Fresh migration (drop all tables and re-run)
python cli.py migrate:fresh

# Fresh migration with seeders
python cli.py migrate:fresh-seed

# Show migration history
python cli.py migrate:history

# Show current migration
python cli.py migrate:current

# Rollback one migration
python cli.py migrate:downgrade

# Reset all migrations
python cli.py migrate:reset
# List semua seeders yang tersedia
python cli.py db:seed --list

# Jalankan semua seeders
python cli.py db:seed

# Jalankan seeder specific
python cli.py db:seed UserSeeder

# Fresh migration dengan seeder
python cli.py migrate:fresh --seed
```

## Seeder Commands

```bash
# Run all seeders
python cli.py db:seed

# Run specific seeder
python cli.py db:seed UserSeeder
```

## Development

```bash
# Start development server
python cli.py dev

# Or manually
uvicorn src.main:app --reload

# Test application
curl http://localhost:8000
curl http://localhost:8000/health
```

## Common Workflow

### 1. Mengubah Model/Schema
```bash
# 1. Edit model di src/models/
# 2. Generate migration
python cli.py migrate:create "Update user model"
# 3. Run migration
python cli.py migrate
```

### 2. Fresh Start Development
```bash
# Drop everything and start fresh
python cli.py migrate:fresh-seed
```

### 3. Production Deployment
```bash
# Only run migrations (never fresh in production!)
python cli.py migrate
```

## Alternative Fresh Migration

```bash
# Using dedicated script with confirmation
python migrate_fresh.py

# With seeders
python migrate_fresh.py --seed

# Force without confirmation
python migrate_fresh.py --force --seed
```

# SMT 5 FastAPI Application

## Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd smt-5

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# 6. Create database (if not exists)
createdb -U postgres manpro

# 7. Initialize and run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 8. Seed database
python cli.py db:seed

# 9. Start development server
python cli.py dev
```

## Migration Workflow

### For New Developers
```bash
# Clone and setup
git clone <repo>
cd smt-5
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env

# Fresh setup
python cli.py migrate:fresh-seed
```

### For Development
```bash
# Make model changes
# Generate migration
python cli.py migrate:create "Your migration message"

# Review generated migration file in alembic/versions/

# Apply migration
python cli.py migrate
```

### Production Deployment
```bash
# Only run existing migrations
python cli.py migrate

# Never use migrate:fresh in production!
```

## Why Migration Files Are Not Tracked?

- ✅ **Team Collaboration**: Menghindari conflict saat multiple developers buat migration
- ✅ **Environment Specific**: Migration bisa berbeda antara dev/staging/prod
- ✅ **Fresh Setup**: Setiap developer bisa mulai dengan clean slate
- ✅ **Auto-Generate**: Migration di-generate otomatis dari model changes

## Git Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create fresh migration (if needed)
python cli.py migrate:fresh-seed

# 3. Make your changes to models

# 4. Generate migration for your changes
python cli.py migrate:create "Add new feature"

# 5. Test migration
python cli.py migrate:fresh-seed

# 6. Commit model changes (not migration files)
git add src/models/
git commit -m "Add new user fields"

# 7. Push
git push origin feature-branch
```