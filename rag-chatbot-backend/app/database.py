"""
PostgreSQL connection pool manager using asyncpg.
Provides async database connection handling with connection pooling.
"""

import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import settings


class DatabasePool:
    """Manages asyncpg connection pool for Neon Postgres."""
    
    def __init__(self):
        self.pool: asyncpg.Pool | None = None
    
    async def connect(self) -> None:
        """Create connection pool on startup."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=settings.neon_connection_string,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                command_timeout=60,
                server_settings={
                    'application_name': 'rag-chatbot-backend',
                }
            )
    
    async def disconnect(self) -> None:
        """Close connection pool on shutdown."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Acquire a database connection from the pool.
        
        Usage:
            async with db_pool.acquire() as conn:
                result = await conn.fetch("SELECT * FROM users")
        """
        if self.pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query without returning results (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query with $1, $2, ... placeholders
            *args: Query parameters
        
        Returns:
            Status string from database
        """
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        """
        Execute a query and return all results.
        
        Args:
            query: SQL query with $1, $2, ... placeholders
            *args: Query parameters
        
        Returns:
            List of database records
        """
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        """
        Execute a query and return a single row.
        
        Args:
            query: SQL query with $1, $2, ... placeholders
            *args: Query parameters
        
        Returns:
            Single database record or None if not found
        """
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args, column: int = 0):
        """
        Execute a query and return a single value.
        
        Args:
            query: SQL query with $1, $2, ... placeholders
            *args: Query parameters
            column: Column index to return (default: 0)
        
        Returns:
            Single value from the specified column
        """
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args, column=column)
    
    async def health_check(self) -> bool:
        """
        Check database connectivity and health.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            if self.pool is None:
                return False
            
            async with self.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False


# Global database pool instance
db_pool = DatabasePool()
