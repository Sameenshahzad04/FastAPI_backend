# handlers/task_handler.py

from turtle import title
from unittest import result

from sqlalchemy.orm import Session, join, joinedload
from fastapi import HTTPException, status
from schemas.task_schema import TaskOut,tasksIn
from models.task import Task
from models.project import Project
from models.user import User
from utils.redis_service import cache_get, cache_set, cache_delete
import logging

from database import SessionLocal
logger = logging.getLogger(__name__)


def get_task_by_id(db: Session, task_id: int,user: User):
   
    if user.role_name == "user":
        task = db.query(Task).filter(Task.id == task_id, Task.assigned_to == user.id).first()
    else:
        task = db.query(Task).filter(Task.id == task_id).all()
    
    
    return task
    


def get_tasks_by_project_id(db: Session, project_id: int, current_user: User):
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Role-based access control
    if current_user.role_name.lower()=="user":
        # Regular user - only show tasks assigned to them or created by them
        tasks = db.query(Task).filter(
            Task.project_id == project_id,
            (Task.assigned_to == current_user.id)
        ).first()
    else:
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tasks not found"
        )
    
    return tasks
 

def create_task(db: Session, t:Task, project_id: int, user: User):
     
    
    proj = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
        
        ).first()
    
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    new_task = Task(
        title=t.title,
        des=t.des,
        status=t.status,
        project_id=project_id 
        # org_id=user.org_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def assign_task_to_user(db: Session, task_id: int, user_id: int,assigner: User):



    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Use SessionLocal() to query public schema (users table)
    with SessionLocal() as public_db:
        user = public_db.query(User).filter(
            User.id == user_id,
            User.role_name == "user",
            User.org_id == assigner.org_id
        ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found or not a normal user")

    task.assigned_to = user_id
    db.commit()
    db.refresh(task)
    result = {
        "id": task.id,
        "title": task.title,
        "des": task.des,
        "status": task.status,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "assigned_user": None      }
    
    # Clear cache
    cache_delete(f"task_id:{task_id}")
    
    return result



def get_project_tasks(db: Session, project_id: int, user:User, page: int, no_records: int,search:str):

    
    
    
    cache_key = f"tasks:{user.org_id}:{project_id or 'all'}:page:{page}:size:{no_records}"
    
    if search:
        cache_key += f":search:{search}"
    
    # Check cache first
    cached = cache_get(cache_key)
    
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached
    
    
    logger.info(f"Cache miss: {cache_key}")
    


    
    tasks = get_tasks_by_project_id(db, project_id, user)
    
    


    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )

    if search:
        tasks = tasks.filter(
            (Task.title.ilike(f"%{search}%")) |
            (Task.project_id == project_id) |
            (Task.assigned_to == user.id)
        )
    
    if type(tasks) == Task:

        tasks_data=[]
        tasks_data.append({
            "id": tasks.id,
            "title": tasks.title,
            "des": tasks.des,
            "status": tasks.status,
            "project_id": tasks.project_id,
            "assigned_to": tasks.assigned_to,
            "assigned_user": None
        })
        result ={
        "page": page,
        "records": no_records,
        "total": 1,
        "pages": 1,
        "data": tasks_data
        }
        
        
        # Cache the result
        cache_set(cache_key, result, expire_seconds=120)
        logger.info(f"Cached: {cache_key}")
        
        return result 
    else:    
        total = len(tasks)
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
       
            paginated_data = tasks[start:end]
        else:
             paginated_data = tasks
        pages = (total + no_records - 1) // no_records
        if page > pages:
            raise HTTPException(status_code=404, detail="Page out of range")
        tasks_data =[]
        for task in paginated_data:
        # Load assigned_user if assigned_to exists
            assigned_user_data = None
            if task.assigned_to:
                with SessionLocal() as public_db:
                    assigned_user = public_db.query(User).filter(User.id == task.assigned_to).first()
                if assigned_user:
                    assigned_user_data = {
                    "id": assigned_user.id,
                    "username": assigned_user.username,
                    "email": assigned_user.email,
                    "org_id": assigned_user.org_id
                }
        
        tasks_data.append({
            "id": task.id,
            "title": task.title,
            "des": task.des,
            "status": task.status,
            "project_id": task.project_id,
            "assigned_user": assigned_user_data
        })
            
        result = {
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data": tasks_data
    }
        
        # Cache the result
        cache_set(cache_key, result, expire_seconds=120)
        logger.info(f"Cached: {cache_key}")
        
        return result 
    
   


def update_task(db: Session, task_id: int, user: User,t:tasksIn):

  
    task = get_task_by_id(db, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = t.title
    task.des = t.des
    task.status = t.status
    
    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, user: User):

    
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    db.delete(task)
    db.commit()

    return {"msg": f"task {task_id} deleted"}
