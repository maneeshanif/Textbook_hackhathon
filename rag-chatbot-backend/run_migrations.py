"""
Run database migrations.
"""
import asyncio
import asyncpg
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


async def run_migration(migration_file: Path):
    """Run a single migration file"""
    print(f"Running migration: {migration_file.name}")
    
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    try:
        sql = migration_file.read_text()
        await conn.execute(sql)
        print(f"✅ Migration {migration_file.name} completed successfully")
    except Exception as e:
        print(f"❌ Migration {migration_file.name} failed: {e}")
        raise
    finally:
        await conn.close()


async def main():
    """Run all pending migrations"""
    migrations_dir = Path(__file__).parent / "migrations"
    
    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("No migrations found")
        return
    
    print(f"Found {len(migration_files)} migration(s)")
    
    for migration_file in migration_files:
        await run_migration(migration_file)
    
    print("\n✅ All migrations completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
