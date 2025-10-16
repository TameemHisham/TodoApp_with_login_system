from db.db_config import SessionLocal, Base, engine
from db.models import Admin as AdminDB
from auth.hashing import hash_password
from datetime import datetime

Base.metadata.create_all(bind=engine)


def create_admin(username: str, password: str):
    """Create an admin user with properly hashed password."""
    with SessionLocal() as session:
        # Check if admin already exists
        existing_admin = session.query(AdminDB).filter(
            AdminDB.username == username
        ).first()

        if existing_admin:
            print(f"Admin '{username}' already exists!")
            return

        # Create new admin
        admin = AdminDB(
            username=username,
            password=hash_password(password),
            role="admin",
            created_at=datetime.now()
        )

        session.add(admin)
        session.commit()
        session.refresh(admin)

        print(f"Admin '{username}' created successfully with ID: {admin.id}")


if __name__ == "__main__":
    create_admin("admin", "admin123")
