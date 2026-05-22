

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.organization import Organization
from models.task import Task
from models.project import Project
from models.user import User

from utils.redis_service import cache_get, cache_set, cache_delete
from database import get_db, get_tenant_db  

# from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def get_project_by_id(db: Session, project_id: int):
    
    
    # Check cache first
    cached = cache_get(f"project_id:{project_id}")
    
    if cached:
        print(f" Cache hit: project_id:{project_id}")
        return Project(**cached)
    
    # Cache miss - query database
    print(f" Cache miss: project_id:{project_id}")
    project = db.query(Project).filter(Project.id == project_id).first()
    
    # Cache the result (10 minutes)
    if project:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "des": project.des,
            "org_id": project.org_id,
            "owner_id": project.owner_id,
           
        }
        cache_set(f"project_id:{project_id}", project_dict, expire_seconds=120)
    
    return project


def get_projects_by_org_id(db: Session, org_id: int, current_user: User):

  
   return db.query(Project).all()

def create_project(db: Session,p:Project,user: User):
    
   
    proj = Project(
        name=p.name,
        des=p.des,
        owner_id=user.id,
        org_id=user.org_id
    )
     
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


def get_user_projects(db: Session, user: User, page: int, no_records: int,search:str):
  


    cache_key = f"users_project:{user.role_name.lower()}:{user.org_id or 'all'}:page:{page}:size:{no_records}"
    
    if search:
        cache_key += f":search:{search}"
    
    # Check cache first
    cached = cache_get(cache_key)
    
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached 
    
    
    logger.info(f" Cache miss: {cache_key}")
    
    if user.role_name.lower() == "super_admin":
        all_projects = []
        orgs = db.query(Organization).all()
        for org in orgs:
            try:
                with next(get_tenant_db(org.id)) as tenant_db:
                    projects = tenant_db.query(Project).all()
                    all_projects.extend(projects)
            except Exception as e:
                logger.error(f"Error fetching projects for org {org.id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        # Convert list to query-like object for filtering/pagination
        projects = all_projects
    else:
        if not user.org_id:
            raise HTTPException(status_code=400, detail="User not in any organization")
        
        projects=get_projects_by_org_id(db, user.org_id, user)
        

    if search:
         projects = projects.filter(
            (Project.name.ilike(f"%{search}%")) 
            
        )
    total = len(projects) if isinstance(projects, list) else projects.count()
   
    start = (page - 1) * no_records
    if total == 0:
        result = {
            "page": page,
            "records": no_records,
            "total": 0,
            "pages": 0,
            "data": []
        }
        cache_set(cache_key, result, expire_seconds=300)
        return result
    

    
    if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
    end = start + no_records

        # Slice the data
    if total>=no_records:
       
            paginated_data = projects[start:end]
    else:
             paginated_data = projects
    pages = (total + no_records - 1) // no_records

    if page > pages:
        raise HTTPException(status_code=404, detail="Page out of range")

    result ={
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
       "data": [
                {"id": p.id, "name": p.name, "des": p.des, "owner_id": p.owner_id, "org_id": p.org_id}
                for p in paginated_data
            ]
    }

    cache_set(cache_key, result, expire_seconds=120)
    logger.info(f" Cached: {cache_key}")
    
    return result 
   


def get_single_project(db: Session, project_id: int, user: User):
   
    
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


def delete_project(db: Session, project_id: int, user: User):
    
    
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    cache_delete(f"project_id:{project_id}")
    db.commit()
    
    return {"message": "Project deleted"}