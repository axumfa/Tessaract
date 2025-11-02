"""
Database connection and session management for PostgreSQL
"""
import os
import logging
from contextlib import contextmanager
from typing import Generator, Optional
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)

# Database configuration from environment variables
# Safely get environment variables with proper encoding handling
def get_env_safe(key: str, default: str = "") -> str:
    """Safely get environment variable, handling encoding issues"""
    try:
        value = os.getenv(key)
        if value is None:
            return default
        
        # Handle different encodings safely
        if isinstance(value, bytes):
            # Try UTF-8 first, then latin-1, then replace errors
            try:
                return value.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return value.decode('latin-1')
                except UnicodeDecodeError:
                    return value.decode('utf-8', errors='replace')
        
        # If it's already a string, ensure it's valid
        if isinstance(value, str):
            # Check for problematic characters and handle them
            try:
                value.encode('utf-8')
                return value
            except UnicodeEncodeError:
                # If encoding fails, try to fix it
                return value.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
        
        return str(value)
    except Exception as e:
        logger.debug(f"Error reading env var {key}: {str(e)}, using default")
        return default

DB_HOST = get_env_safe("DB_HOST", "localhost")
DB_NAME = get_env_safe("DB_NAME", "fraud_detection")
DB_USER = get_env_safe("DB_USER", "postgres")
DB_PASSWORD = get_env_safe("DB_PASSWORD", "postgres")
DB_PORT = get_env_safe("DB_PORT", "5432")

# Connection pool
_connection_pool: Optional[pool.ThreadedConnectionPool] = None
_db_available: bool = False


def init_db():
    """Initialize database connection pool and create tables"""
    global _connection_pool, _db_available
    
    # Check if database credentials are provided
    if not DB_PASSWORD or DB_PASSWORD == "":
        logger.info("Database password not set, skipping database initialization")
        _db_available = False
        _connection_pool = None
        return False
    
    try:
        # Ensure port is an integer
        try:
            db_port = int(DB_PORT)
        except (ValueError, TypeError):
            db_port = 5432
            logger.warning(f"Invalid DB_PORT '{DB_PORT}', using default 5432")
        
        # Create connection pool with explicit encoding handling
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            host=str(DB_HOST),
            database=str(DB_NAME),
            user=str(DB_USER),
            password=str(DB_PASSWORD),
            port=db_port,
            cursor_factory=RealDictCursor,
            connect_timeout=5  # 5 second timeout
        )
        
        # Test connection
        with get_db_connection() as conn:
            create_tables(conn)
        
        _db_available = True
        logger.info("Database connection pool initialized successfully")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        # More user-friendly error messages
        if "connection" in error_msg.lower() or "could not connect" in error_msg.lower():
            logger.warning(f"Database connection failed: Could not connect to PostgreSQL. "
                         f"Please check if PostgreSQL is running and credentials are correct.")
        else:
            logger.warning(f"Database connection failed: {error_msg}")
        _db_available = False
        _connection_pool = None
        return False
    except UnicodeDecodeError as e:
        logger.warning(f"Database initialization failed: Encoding error when reading database credentials. "
                      f"Please ensure your password contains only ASCII characters or set it using: "
                      f"set_db_env.bat")
        _db_available = False
        _connection_pool = None
        return False
    except Exception as e:
        error_msg = str(e)
        # Handle encoding errors specifically
        if "codec" in error_msg.lower() or "decode" in error_msg.lower() or "utf-8" in error_msg.lower():
            logger.warning(f"Database initialization failed: Encoding error. "
                          f"This usually means the database password contains special characters. "
                          f"Try setting credentials again with: set_db_env.bat")
        else:
            logger.warning(f"Database initialization failed: {error_msg}")
        _db_available = False
        _connection_pool = None
        return False


def is_db_available() -> bool:
    """Check if database is available"""
    return _db_available and _connection_pool is not None


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Get a database connection from the pool.
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ...")
    """
    if not _connection_pool:
        raise RuntimeError("Database connection pool not initialized")
    
    conn = _connection_pool.getconn()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        _connection_pool.putconn(conn)


@contextmanager
def get_db_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Get a database cursor with automatic commit/rollback.
    Usage:
        with get_db_cursor() as cur:
            cur.execute("INSERT INTO ...")
            # Auto-commit on success, rollback on error
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                yield cur
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise


def create_tables(conn: psycopg2.extensions.connection):
    """Create database tables if they don't exist"""
    with conn.cursor() as cur:
        # Create predictions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(50) UNIQUE,
                transaction_data JSONB,
                prediction BOOLEAN NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on transaction_id for faster lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_transaction_id 
            ON predictions(transaction_id)
        """)
        
        # Create index on timestamp for faster time-based queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
            ON predictions(timestamp)
        """)
        
        # Create index on prediction for faster fraud queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_prediction 
            ON predictions(prediction)
        """)
        
        conn.commit()
        logger.info("Database tables created successfully")


def close_db_pool():
    """Close all database connections in the pool"""
    global _connection_pool, _db_available
    
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        _db_available = False
        logger.info("Database connection pool closed")


def log_prediction(transaction_id: str, transaction_data: dict, 
                   prediction: bool, confidence: float) -> bool:
    """
    Log a prediction to the database.
    Returns True if successful, False otherwise.
    """
    if not is_db_available():
        logger.warning("Database not available, prediction not logged")
        return False
    
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO predictions 
                (transaction_id, transaction_data, prediction, confidence)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (transaction_id) 
                DO UPDATE SET 
                    transaction_data = EXCLUDED.transaction_data,
                    prediction = EXCLUDED.prediction,
                    confidence = EXCLUDED.confidence,
                    timestamp = CURRENT_TIMESTAMP
            """, (
                transaction_id,
                Json(transaction_data),
                prediction,
                confidence
            ))
        
        logger.info(f"Prediction logged for transaction {transaction_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log prediction: {str(e)}")
        return False


def get_recent_transactions(limit: int = 100) -> list:
    """Get recent transactions from database"""
    if not is_db_available():
        raise RuntimeError("Database not available")
    
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    transaction_id,
                    transaction_data,
                    prediction,
                    confidence,
                    timestamp
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cur.fetchall()]
            
    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        raise


def get_fraud_stats() -> dict:
    """Get fraud statistics from database"""
    if not is_db_available():
        raise RuntimeError("Database not available")
    
    try:
        with get_db_cursor() as cur:
            # Get total transactions and fraud count
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count
                FROM predictions
            """)
            stats = cur.fetchone()
            total = stats['total'] or 0
            fraud_count = stats['fraud_count'] or 0
            
            # Get fraud by hour
            cur.execute("""
                SELECT 
                    EXTRACT(HOUR FROM timestamp)::INTEGER as hour,
                    COUNT(*) as count,
                    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count
                FROM predictions
                GROUP BY hour
                ORDER BY hour
            """)
            hourly_stats = []
            for row in cur.fetchall():
                hourly_stats.append({
                    "hour": int(row['hour']),
                    "total": row['count'],
                    "fraud_count": row['fraud_count'] or 0,
                    "fraud_percentage": (row['fraud_count'] or 0) / row['count'] * 100 if row['count'] > 0 else 0
                })
            
            # Get recent trend (last 7 days)
            cur.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as count,
                    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count
                FROM predictions
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY date
                ORDER BY date
            """)
            daily_stats = []
            for row in cur.fetchall():
                daily_stats.append({
                    "date": row['date'].isoformat(),
                    "total": row['count'],
                    "fraud_count": row['fraud_count'] or 0,
                    "fraud_percentage": (row['fraud_count'] or 0) / row['count'] * 100 if row['count'] > 0 else 0
                })
            
            return {
                "total_transactions": total,
                "fraud_count": fraud_count,
                "fraud_percentage": (fraud_count / total * 100) if total > 0 else 0,
                "hourly_stats": hourly_stats,
                "daily_stats": daily_stats
            }
            
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise

