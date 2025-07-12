import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError(
        "❌ DATABASE_URL environment variable is required!\n"
        "Create a .env file with:\n"
        "DATABASE_URL=postgresql://postgres:password@host:port/database\n"
        "See .env.example for the correct format."
    )

print(
    f"✅ Database configured: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}"
)
