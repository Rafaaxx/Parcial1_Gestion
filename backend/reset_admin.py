"""Reset admin user in database - cleans and recreates admin."""
import logging
import os
import re

import psycopg2
import bcrypt

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:tutuca05@localhost:5432/food_store_db")

# Parse the database URL into components for psycopg2
match = re.match(r'postgresql\+asyncpg://(?:(?P<user>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:]+)(?::(?P<port>\d+))?/(?P<dbname>.+)', DATABASE_URL)
if match:
    user = match.group('user') or 'postgres'
    password = match.group('password') or ''
    host = match.group('host') or 'localhost'
    port = match.group('port') or '5432'
    dbname = match.group('dbname') or 'food_store_db'
    SYNC_DB_URL = f"host={host} port={port} dbname={dbname} user={user} password={password}"
else:
    SYNC_DB_URL = "host=localhost port=5432 dbname=food_store_db user=postgres password=tutuca05"

ADMIN_EMAIL = "admin@foodstore.com"
ADMIN_PASSWORD = "Admin1234!"
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "User"

def reset_admin():
    """Delete existing admin and create new one with correct password."""
    conn = psycopg2.connect(SYNC_DB_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                # Delete existing admin user and roles
                logger.info("🗑️  Cleaning existing admin user...")
                cur.execute("DELETE FROM usuarios_roles WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = %s)", (ADMIN_EMAIL,))
                cur.execute("DELETE FROM usuarios WHERE email = %s", (ADMIN_EMAIL,))
                logger.info("  ✅  Existing admin deleted")

                # Create new admin with proper bcrypt hashing
                logger.info("👤  Creating new admin user...")
                salt = bcrypt.gensalt(rounds=12)  # Use rounds=12 to match security.py
                password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), salt).decode('utf-8')

                cur.execute(
                    """INSERT INTO usuarios (email, password_hash, nombre, apellido, activo, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, true, NOW(), NOW())
                       RETURNING id""",
                    (ADMIN_EMAIL, password_hash, ADMIN_NOMBRE, ADMIN_APELLIDO)
                )
                admin_id = cur.fetchone()[0]
                logger.info(f"  ✅  Admin user created (id={admin_id})")

                # Assign admin role
                cur.execute(
                    "INSERT INTO usuarios_roles (usuario_id, rol_codigo, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                    (admin_id, "ADMIN")
                )
                logger.info("  ✅  Admin role assigned")

                # Verify the password was stored correctly
                cur.execute("SELECT password_hash FROM usuarios WHERE email = %s", (ADMIN_EMAIL,))
                stored_hash = cur.fetchone()[0]

                # Test verification
                test_result = bcrypt.checkpw(ADMIN_PASSWORD.encode('utf-8'), stored_hash.encode('utf-8'))
                logger.info(f"  ✅  Password verification test: {'PASS' if test_result else 'FAIL'}")

        logger.info("🎉  Admin reset complete!")
        logger.info(f"   Email: {ADMIN_EMAIL}")
        logger.info(f"   Password: {ADMIN_PASSWORD}")

    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin()