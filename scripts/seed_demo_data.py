"""
TalentForge AI — Demo Data Seeder (Phase 2 Placeholder)
========================================================
This script will seed the database with demo data in Phase 2.

Phase 1: This is a placeholder skeleton that confirms the database
         connection is working and prints a helpful message.

Phase 2 will implement:
  - Demo company creation
  - 10 employee records
  - 8 candidate records
  - Sample performance records
  - Sample training records
  - Sample attrition risk values
  - Sample job roles
  - Sample onboarding records

Usage:
    python scripts/seed_demo_data.py
"""

from __future__ import annotations

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def seed_demo_data() -> None:
    """
    Main seeder function.
    Phase 1: Verifies DB connection only.
    Phase 2: Creates all demo data.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    print("=" * 60)
    print("TalentForge AI — Demo Data Seeder")
    print("=" * 60)
    print()

    # Phase 1: Test DB connectivity
    print("Phase 1 — Checking database connection...")
    try:
        from app.db.session import check_database_connection
        db_ok = await check_database_connection()
        if db_ok:
            print("  ✓ Database connection: OK")
        else:
            print("  ✗ Database connection: FAILED")
            print()
            print("  Please verify:")
            print("  1. DATABASE_URL is set in .env")
            print("  2. Neon database is accessible")
            print("  3. Alembic migrations have been run: alembic upgrade head")
            sys.exit(1)
    except Exception as exc:
        print(f"  ✗ Database connection error: {type(exc).__name__}")
        print("  Check your .env configuration.")
        sys.exit(1)

    print()
    print("Phase 2 demo data seeding is not yet implemented.")
    print("Run this script again after Phase 2 is complete.")
    print()
    print("To run migrations:")
    print("  alembic upgrade head")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
