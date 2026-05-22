
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from schemas.task_schema import tasksIn
from models.subtasks import Subtask
from models.organization import Organization
from database import get_db, get_tenant_db
from schemas.subtasks_schema import SubtaskIn,SubtaskOut
from models.task import Task
from models.project import Project
from models.user import User
from utils.redis_service import cache_get, cache_set, cache_delete
from handlers.task_handler import get_task_by_id
import logging

logger = logging.getLogger(__name__)

def get_subtask_by_task_id(db: Session, task_id: int,user: User):

    task = db.query(Task).filter(
        Task.id == task_id,
        
    ).first()

    return task  


def create_subtask(db: Session, task_id: int, user: User, s:SubtaskIn):
    


    cache=cache_get(f"subtask_by_task_id:{task_id}")
    if cache:
        logger.info(f"Cache hit: task_id:{task_id}")
        task = cache
    else:
        logger.info(f"Cache miss: subtask_by_task_id:{task_id}")
        task = get_subtask_by_task_id(db, task_id, user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you are not assigned to it"
        )

    # Create subtask
    subtask = Subtask(
        title=s.title,
        description=s.description,
        status=s.status,
        task_id=task_id
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask

def get_task_subtask(db: Session, task_id: int, user:User, page: int, no_records: int,search:str):

    
    cache_key = f"subtasks:{user.org_id}:{task_id or 'all'}:page:{page}:size:{no_records}"
    
    if search:
        cache_key += f":search:{search}"
    
    # Check cache first
    cached = cache_get(cache_key)
    
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached
    
    
    logger.info(f"Cache miss: {cache_key}")
    
    if user.role_name.lower() == "super_admin":
        all_subtasks = []
        orgs = db.query(Organization).all()
        for org in orgs:
            try:
                with next(get_tenant_db(org.id)) as tenant_db:
                    query = tenant_db.query(Subtask).all()
                    all_subtasks.extend(query)
            except Exception as e:
                logger.error(f"Error fetching substasks for org {org.id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        query = all_subtasks
    elif user.role_name == "org_admin":
        query = db.query(Subtask).join(Task).join(Project).filter(Subtask.task_id == task_id).all()
    else:
        query = db.query(Subtask).join(Task).join(Project).filter(Subtask.task_id == task_id, Task.assigned_to == user.id).first()

    # Apply search filter if provided
    if search:
        query = query.filter(
            Subtask.title.ilike(f"%{search}%")  # Search in title
            # Note: no need to re-check task_id — already filtered above
        )

      
    if type(query) == Subtask:

        subtasks_data=[]
        subtasks_data.append({
            
            "title": query.title,
            "description": query.description,
            "status": query.status,
            "task_id": query.task_id,
          
        })
        result ={
        "page": page,
        "records": no_records,
        "total": 1,
        "pages": 1,
        "data": subtasks_data
        }
        
        
        # Cache the result
        cache_set(cache_key, result, expire_seconds=120)
        logger.info(f"Cached: {cache_key}")
        
        return result 
    else:    
        total = len(query)
        if total == 0:
            result = {
            "page": page,
            "records": no_records,
            "total": 0,
            "pages": 0,
            "data": []
        }
            cache_set(cache_key, result, expire_seconds=120)
            return result
    
    start = (page - 1) * no_records

    if start >= total:
        raise HTTPException(status_code=404, detail="Page out of range")
    end = start + no_records

        # Slice the data
    if total>=no_records:
       
            paginated_data = query[start:end]
    else:
             paginated_data = query

    pages = (total + no_records - 1) // no_records
    

    if page > pages:
        raise HTTPException(status_code=404, detail="Page out of range")

    result={
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data":[
                {"id": s.id, "title": s.title, "description": s.description, "status": s.status, "task_id": s.task_id}
                for s in paginated_data]
                
            }
    cache_set(cache_key, result, expire_seconds=300)
    return result





def update_subtask( subtask_id: int,s: SubtaskIn,db: Session, user: User):
    # Find subtask, ensure it's under a task assigned to the user
    subtask = db.query(Subtask).join(Task).join(Project).filter(
        Subtask.id == subtask_id,
        # Task.id == s.task_id,
        Task.assigned_to == user.id,
        Project.org_id == user.org_id
    ).first()
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found or you are not authorized to update it"
        )

    
    subtask.status = s.status
    subtask.title = s.title
    subtask.description = s.description

    db.commit()
    db.refresh(subtask)
    return subtask

def delete_subtask( subtask_id: int,db: Session, user: User):

    subtask = db.query(Subtask).join(Task).join(Project).filter(
        Subtask.id == subtask_id,
        Task.assigned_to == user.id,
        Project.org_id == user.org_id
    ).first()

    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found or unauthorized"
        )

    db.delete(subtask)
    db.commit()

    return {"msg": f"Subtask {subtask_id} deleted"}
