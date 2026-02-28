"""Seed database with minimal data (categories, admin user). Run after migrations."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def seed() -> None:
    """Create minimal seed data."""
    from app import create_app
    from database import db
    from models import User, Category
    from utils.security import hash_password
    from sqlalchemy.exc import OperationalError

    app = create_app("development")
    with app.app_context():
        try:
            if Category.query.first() is not None:
                print("Already seeded; skip.")
                return
        except OperationalError as e:
            if "no such table" in str(e).lower():
                print("Database tables are missing. Run migrations first:")
                print("  flask db upgrade")
                print("Then run this script again.")
                sys.exit(1)
            raise
        c1 = Category(name="Electronics")
        c2 = Category(name="Clothing")
        db.session.add_all([c1, c2])
        admin = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        admin.password_hash = hash_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Seed done: 2 categories, 1 admin (admin@example.com / admin123).")


if __name__ == "__main__":
    seed()
