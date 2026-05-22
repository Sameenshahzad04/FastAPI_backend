
from base import SessionLocal, engine, Base
from models.roles import Role
from models.user import User
from jwt import get_pwd_hash

def create_tables():
    """Create all database tables"""
    print(" Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(" Database tables created!")

def create_roles():
    """Create default roles"""
    print(" Creating roles...")
    db = SessionLocal()
    try:
        for role_name in ["super_admin", "org_admin", "user"]:
            role = db.query(Role).filter(Role.role_name == role_name).first()
            if not role:
                role = Role(role_name=role_name)
                db.add(role)
                print(f"    Created role: {role_name}")
        
        db.commit()
        print(" Roles created!")
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()

def create_super_admin():
    """Create super admin user"""
    print("Creating super admin...")
    db = SessionLocal()
    try:
        # Check if super admin exists
        super_admin = db.query(User).filter(User.role_name == "super_admin").first()
        if super_admin:
            print(f"  Super admin already exists: {super_admin.username}")
            return
        
        # Create super admin
        hashed_password = get_pwd_hash("admin123")
        
        super_admin = User(
            username="super_admin",
            email="super@admin.com",
            password=hashed_password,
            role_name="super_admin",
            org_id=None,
            is_active=True,
            first_login_done=True
        )
        
        db.add(super_admin)
        db.commit()
        
        print(" Super Admin created!")
        print("   Username: super_admin")
        print("   Email: admin@pms.com")
        print("   Password: admin123")
        print("   ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")
        
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print(" Setting up Multi-Tenant PMS Database")
    print("=" * 60)
    
    try:
        # Step 1: Create tables
        create_tables()
        
        # Step 2: Create roles
        create_roles()
        
        # Step 3: Create super admin
        create_super_admin()
        
        print("=" * 60)
        print(" Setup complete!")
        print("=" * 60)
        print("\nNext: python run_server.py")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print(f" Setup failed: {e}")
        print("=" * 60)