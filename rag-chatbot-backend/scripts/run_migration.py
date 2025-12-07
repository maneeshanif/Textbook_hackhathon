#!/usr/bin/env python3
"""
Run database migrations using asyncpg.
"""
import asyncio
import asyncpg


async def run_migration():
    """Execute the auth tables migration."""
    connection_string = 'postgresql://neondb_owner:npg_ugoGsJ8j2czZ@ep-lucky-glitter-ads9dks5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
    
    # Read migration SQL
    with open('migrations/002_auth_tables.sql', 'r') as f:
        migration_sql = f.read()
    
    # Remove triple-quoted comment blocks
    lines = []
    in_comment = False
    for line in migration_sql.split('\n'):
        if '"""' in line:
            in_comment = not in_comment
            continue
        if not in_comment:
            lines.append(line)
    
    clean_sql = '\n'.join(lines)
    
    # Connect and run migration
    print("Connecting to database...")
    conn = await asyncpg.connect(connection_string)
    
    try:
        print("Running migration...")
        await conn.execute(clean_sql)
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'accounts', 'auth_sessions', 'user_preferences')
            ORDER BY table_name;
        """)
        
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
