# create_super_admin.py

# to create super_Admin run this command:
# python create_super_admin.py
#
## super_admin.py

"""
Run this script once to:
1. Create roles: super_admin, org_admin, user
2. Create super admin user

Command: python super_admin.py
"""

from database import SessionLocal
from models.role import Role
from models.user import User
from jwt import get_pwd_hash


def create_roles_and_super_admin():
    db = SessionLocal()

    try:
        # Step 1: Create roles if they don't exist
        roles_to_create = ["super_admin", "org_admin", "user"]
        for role_name in roles_to_create:
            existing = db.query(Role).filter(Role.role_name == role_name).first()
            if not existing:
                db.add(Role(role_name=role_name))
                print(f"Role '{role_name}' created.")

        db.commit()

        # Step 2: Check if super admin already exists
        super_admin = db.query(User).filter(User.role_name == "super_admin").first()
        if super_admin:
            print(f" Super admin already exists: {super_admin.email}")
            return

        # Step 3: Create super admin
        hashed_password = get_pwd_hash("superadmin123")  # Change this in production!

        new_super_admin = User(
            username="superadmin",
            email="super@admin.com",
            password=hashed_password,
            role_name="super_admin",
            is_active=True,
            first_login_done=True, 
            org_id=0,
        )

        db.add(new_super_admin)
        db.commit()
        db.refresh(new_super_admin)

        print(" All roles created and Super Admin setup complete!")
        print(f"Login as: {new_super_admin.email} | Password: superadmin123")

    except Exception as e:
        print(f" Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_roles_and_super_admin()