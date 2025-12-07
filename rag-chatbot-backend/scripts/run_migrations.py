#!/usr/bin/env python3
"""
Run database migrations against Neon Postgres.
Usage: python run_migrations.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_pool
from app.config import settings


async def run_migrations():
    """Execute all SQL migration files in order."""
    
    print("🔄 Starting database migrations...")
    print(f"   Database: {settings.neon_connection_string.split('@')[1].split('/')[0]}")
    print()
    
    # Connect to database
    await db_pool.connect()
    
    # Get migration files in order
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("❌ No migration files found in migrations/")
        return
    
    print(f"Found {len(migration_files)} migration files")
    print()
    
    # Run each migration
    for migration_file in migration_files:
        print(f"📝 Running: {migration_file.name}")
        
        try:
            # Read migration SQL
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute migration
            async with db_pool.acquire() as conn:
                await conn.execute(sql)
            
            print(f"   ✅ Success")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            if "already exists" in str(e).lower():
                print(f"   ℹ️  Table already exists, continuing...")
            else:
                print(f"   ⚠️  Migration failed, stopping...")
                break
        
        print()
    
    # Cleanup
    await db_pool.disconnect()
    
    print("✨ Migration process completed!")


if __name__ == "__main__":
    asyncio.run(run_migrations())
