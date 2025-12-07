"""
Shared FastAPI dependencies.
Placed in a separate module to avoid circular imports.
"""

from app.database import db_pool


def get_db_pool():
    """
    Dependency to get database pool.
    
    Returns:
        asyncpg.Pool: The database connection pool.
    """
    return db_pool.pool
