# # database.py

# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import Session, sessionmaker, declarative_base
# from fastapi import HTTPException
# from dotenv import load_dotenv
# import os
# from config.config import DATABASE_URL
# from contextlib import contextmanager
# import logging

# logger = logging.getLogger(__name__)
# from models.organization import Organization

# # Create engine
# engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # ─── Shared DB (public schema) ───
# # @contextmanager
# def get_db():
#     """Get DB session for shared tables (users, organizations, roles)"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ─── Tenant DB (org-specific schema) ───
# # @contextmanager
# def get_tenant_db(org_id: int):

    
#     try:
#         # SUPER ADMIN (org_id=None) - Access to ALL schemas
#         if org_id is None:
#             logger.info("Super Admin accessing all organization schemas")
            
#             # Use public schema connection (can query any schema)
#             connection = engine.execution_options(
#                 schema_translate_map={None: "public"}
#             )
#             db_session = sessionmaker(bind=connection)
#             db = db_session()
            
#             # Verify super_admin can access organization metadata
#             try:
#                 result = db.execute(
#                     text("SELECT id, name FROM public.organization LIMIT 1")
#                 ).first()
#                 logger.info(f"Super Admin connected - Found organizations")
#             except Exception as e:
#                 logger.warning(f"Organization query check: {str(e)}")
            
#             yield db
        
#         #  REGULAR USER - Access to specific organization schema only
#         else:
#             schema_name = f"org_{org_id}"
#             logger.info(f"Connecting to schema: {schema_name}")
            
#             # Check if schema exists
#             with SessionLocal() as check_db:
#                 result = check_db.execute(
#                     text("""
#                         SELECT schema_name 
#                         FROM information_schema.schemata 
#                         WHERE schema_name = :schema
#                     """),
#                     {"schema": schema_name}
#                 ).first()
                
#                 if not result:
#                     raise HTTPException(
#                         status_code=404, 
#                         detail=f"Organization schema {schema_name} not found"
#                     )
            
#             # Create session with schema translation
#             connection = engine.execution_options(
#                 schema_translate_map={None: schema_name}
#             )
#             tenant_session = sessionmaker(bind=connection)
#             db = tenant_session()
            
#             yield db
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Database connection error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    
#     finally:
#         if db:
#             db.close()
#             logger.info("Database session closed")

# # ─── Create Schema for New Org ───
# def create_org_schema(org_id: int):
#     """Create a new schema for organization"""
#     db = SessionLocal()
#     try:
#         schema_name = f"org_{org_id}"
        
#         # Create schema
#         db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        
#         # Create tenant tables in this schema
#         db.execute(text(f"""
#             CREATE TABLE IF NOT EXISTS {schema_name}.projects (
#                 id SERIAL PRIMARY KEY,
#                 name VARCHAR(100) NOT NULL,
#                 des TEXT,
#                 owner_id INTEGER,
#                 org_id INTEGER,
#                 created_at TIMESTAMP DEFAULT NOW()
#             )
#         """))
        
#         db.execute(text(f"""
#             CREATE TABLE IF NOT EXISTS {schema_name}.task (
#                 id SERIAL PRIMARY KEY,
#                 title VARCHAR(100) NOT NULL,
#                 des TEXT,
#                 status VARCHAR(50) DEFAULT 'pending',
#                 assigned_to INTEGER,
#                 project_id INTEGER,
#                 created_at TIMESTAMP DEFAULT NOW()
#             )
#         """))
        
#         db.execute(text(f"""
#             CREATE TABLE IF NOT EXISTS {schema_name}.subtasks (
#                 id SERIAL PRIMARY KEY,
#                 title VARCHAR(100) NOT NULL,
#                 description TEXT,
#                 status VARCHAR(50) DEFAULT 'pending',
#                 task_id INTEGER,
#                 created_at TIMESTAMP DEFAULT NOW()
#             )
#         """))
        
#         db.commit()
#         print(f" Created schema: {schema_name}")
        
#     except Exception as e:
#         db.rollback()
#         print(f" Error: {e}")
#         raise
#     finally:
#         db.close()

# def get_all_from_all_schemas(
#     table_name: str,
#     page: int,
#     no_records: int,
#     search: str = None,
#     search_column: str = "name"
# ):
    
#     all_data = []
    
#     # Step 1: Get all organizations from public schema
#     try:
#         with SessionLocal() as db:
#             orgs = db.query(Organization).all()
#             logger.info(f" Found {len(orgs)} organizations in public.organization")
            
#             # Debug: Print org IDs
#             for org in orgs:
#                 logger.info(f"   - Org ID: {org.id}, Name: {org.name}")
#     except Exception as e:
#         logger.error(f" Failed to query organizations: {str(e)}")
#         return {
#             "page": page,
#             "records": no_records,
#             "total": 0,
#             "pages": 0,
#             "data": []
#         }
    
#     if not orgs:
#         logger.warning(" No organizations found in public.organization table!")
#         return {
#             "page": page,
#             "records": no_records,
#             "total": 0,
#             "pages": 0,
#             "data": []
#         }
    
#     # Step 2: Query EACH organization's schema
#     for org in orgs:
#         schema_name = f"org_{org.id}"
#         logger.info(f" Querying schema: {schema_name}")
        
#         try:
#             # Check if schema exists
#             with SessionLocal() as check_db:
#                 schema_check = check_db.execute(
#                     text("""
#                         SELECT schema_name 
#                         FROM information_schema.schemata 
#                         WHERE schema_name = :schema
#                     """),
#                     {"schema": schema_name}
#                 ).first()
                
#                 if not schema_check:
#                     logger.warning(f" Schema {schema_name} does NOT exist!")
#                     continue
#                 else:
#                     logger.info(f" Schema {schema_name} exists")
            
#             # Create schema-specific connection
#             connection = engine.execution_options(
#                 schema_translate_map={None: schema_name}
#             )
#             schema_session = sessionmaker(bind=connection)()
            
#             # Check if table exists in schema
#             table_check = schema_session.execute(
#                 text("""
#                     SELECT table_name 
#                     FROM information_schema.tables 
#                     WHERE table_schema = :schema 
#                     AND table_name = :table
#                 """),
#                 {"schema": schema_name, "table": table_name}
#             ).first()
            
#             if not table_check:
#                 logger.warning(f" Table {table_name} does NOT exist in schema {schema_name}!")
#                 schema_session.close()
#                 continue
            
#             logger.info(f" Table {table_name} exists in schema {schema_name}")
            
#             # Build query
#             if search:
#                 query = text(f"""
#                     SELECT * FROM {table_name}
#                     WHERE {search_column} ILIKE :search
#                 """)
#                 result = schema_session.execute(query, {"search": f"%{search}%"}).fetchall()
#                 logger.info(f"   Found {len(result)} rows with search '{search}'")
#             else:
#                 query = text(f"""
#                     SELECT * FROM {table_name}
#                 """)
#                 result = schema_session.execute(query).fetchall()
#                 logger.info(f"   Found {len(result)} rows")
            
#             # Convert to dict list
#             for row in result:
#                 row_dict = dict(row._mapping)
#                 row_dict['org_name'] = org.name
#                 all_data.append(row_dict)
            
#             schema_session.close()
            
#         except Exception as e:
#             logger.error(f" Failed to query schema {schema_name}: {str(e)}")
#             continue
    
#     logger.info(f" Total records found across all schemas: {len(all_data)}")
    
#     # Step 3: Pagination
#     total = len(all_data)
    
#     if total == 0:
#         return {
#             "page": page,
#             "records": no_records,
#             "total": 0,
#             "pages": 0,
#             "data": []
#         }
    
#     pages = (total + no_records - 1) // no_records
    
#     if page > pages:
#         raise HTTPException(status_code=404, detail="Page out of range")
    
#     start = (page - 1) * no_records
#     end = start + no_records
#     paginated_data = all_data[start:end]
    
#     return {
#         "page": page,
#         "records": no_records,
#         "total": total,
#         "pages": pages,
#         "data": paginated_data
#     }

# database.py

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
    """Get DB session for tenant tables (projects, tasks, subtasks)"""
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
            CREATE TABLE IF NOT EXISTS {schema_name}.task (
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