
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from config.config import DATABASE_URL
from contextlib import contextmanager

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── Shared DB (public schema) ───
# @contextmanager
def get_db():
    """Get DB session for shared tables (users, organizations, roles)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── Tenant DB (org-specific schema) ───
# @contextmanager
def get_tenant_db(org_id: int):
  
    schema_name = f"org_{org_id}"
    
    # Check if schema exists
    with SessionLocal() as db:
        result = db.execute(
            text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
            {"schema": schema_name}
        ).first()
        
        if not result:
            raise HTTPException(404, f"Organization schema {schema_name} not found")
    
    # Create session with schema
    connection = engine.execution_options(
        schema_translate_map={None: schema_name}
    )
    tenant_session = sessionmaker(bind=connection)
    
    try:
        db = tenant_session()
        yield db
    finally:
        db.close()

# ─── Create Schema for New Org ───
def create_org_schema(org_id: int):
    """Create a new schema for organization"""
    db = SessionLocal()
    try:
        schema_name = f"org_{org_id}"
        
        # Create schema
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        
        # Create tenant tables in this schema
        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                des TEXT,
                owner_id INTEGER,
                org_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                des TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                assigned_to INTEGER,
                project_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.subtasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                task_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        db.commit()
        print(f" Created schema: {schema_name}")
        
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()