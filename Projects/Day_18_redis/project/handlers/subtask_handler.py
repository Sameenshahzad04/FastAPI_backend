# # # handlers/task_handler.py

# # from sqlalchemy.orm import Session
# # from fastapi import HTTPException, status
# # from schemas.task_schema import tasksIn
# # from models.subtasks import Subtask
# # from schemas.subtasks_schema import SubtaskIn,SubtaskOut
# # from models.task import Task
# # from models.project import Project
# # from models.user import User
# # from utils.redis_service import cache_get, cache_set, cache_delete

# # from handlers.task_handler import get_task_by_id

# # def get_subtask_by_id(db: Session, subtask_id: int,user: User):
# #     """Get subtask by ID with caching"""
    
# #     # Check cache first
# #     cached = cache_get(f"subtask_id:{subtask_id}")
    
# #     if cached:
# #         print(f" Cache hit: subtask_id:{subtask_id}")
# #         return Subtask(**cached)
    
# #     # Cache miss - query database
# #     print(f" Cache miss: subtask_id:{subtask_id}")
# #     if user.role_name == "user":
# #         subtask = db.query(Subtask).join(Task).filter(Subtask.id == subtask_id,Task.assigned_to == user.id).first()
# #     else:
# #         subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    
# #     # Cache the result (10 minutes)
# #     if subtask:
# #         subtask_dict = {
# #             "id": subtask.id,
# #             "title": subtask.title,
# #             "description": subtask.description,
# #             "task_id": subtask.task_id,
            
# #             "status": subtask.status,
            
# #         }
# #         cache_set(f"subtask_id:{subtask_id}", subtask_dict, expire_seconds=600)
    
# #     return subtask


# # def get_subtasks_by_task_id(db: Session, task_id: int,user: User):
    
    
# #     # Check cache first
# #     cached = cache_get(f"subtask_task_id:{task_id}")
    
# #     if cached:
# #         print(f" Cache hit: subtasks_task:{task_id}")
# #         return cached
    
# #     # Cache miss - query database
# #     print(f" Cache miss: subtasks_task:{task_id}")
# #     if user.role_name == "user":
# #         subtask = db.query(Subtask).join(Task).filter(Subtask.id == subtask_id,Task.assigned_to == user.id).first()
# #     else:
        
# #         subtasks = db.query(Subtask).join(Task).filter(Subtask.task_id == task_id,Task.assigned_to == user.id).all()
    
    
# #     return subtasks


# # def create_subtask(db: Session, task_id: int, user: User, s:SubtaskIn):


# #     task =get_task_by_id(db, task_id)
# #     if not task:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Task not found or you are not assigned to it"
# #         )

# #     # Create subtask
# #     subtask = Subtask(
# #         title=s.title,
# #         description=s.description,
# #         status=s.status,
# #         task_id=task_id
# #     )
# #     db.add(subtask)
# #     db.commit()
# #     db.refresh(subtask)
# #     return subtask

# # def get_task_subtask(db: Session, task_id: int, user:User, page: int, no_records: int,search:str):
    
# #     query = get_subtasks_by_task_id(db, task_id, user)

# #     # If user is not admin, restrict to assigned subtasks
    

# #     # Apply search filter if provided
# #     if search:
# #         query = query.filter(
# #             Subtask.title.ilike(f"%{search}%")  # Search in title
# #             # Note: no need to re-check task_id — already filtered above
# #         )
# #     if query:
# #         subtask_dict = {
# #             "id": query.id,
# #             "title": query.title,
# #             "description": query.description,
# #             "task_id": query.task_id,
            
# #             "status": query.status,
            
# #         }
# #         cache_set(f"subtask_task_id:{task_id}", subtask_dict, expire_seconds=600)
    
# #     # Now get total count and apply pagination
# #     total = query.count()  # Total matching subtasks
# #     start = (page - 1) * no_records

# #     if start >= total:
# #         raise HTTPException(status_code=404, detail="Page out of range")






# # def update_subtask( subtask_id: int,s: SubtaskIn,db: Session, user: User):
# #     # Find subtask, ensure it's under a task assigned to the user
    
# #     subtask = get_subtask_by_id(db, subtask_id, user.id)
# #     if not subtask:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Subtask not found or you are not authorized to update it"
# #         )

    
# #     subtask.status = s.status
# #     subtask.title = s.title
# #     subtask.description = s.description

# #     db.commit()
# #     db.refresh(subtask)
# #     return subtask

# # def delete_subtask( subtask_id: int,db: Session, user: User):

# #     subtask = get_subtask_by_id(db, subtask_id, user.id)

# #     if not subtask:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Subtask not found or unauthorized"
# #         )

# #     db.delete(subtask)
# #     db.commit()

# #     return {"msg": f"Subtask {subtask_id} deleted"}

# # handlers/subtask_handler.py

# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status
# from schemas.task_schema import tasksIn
# from models.subtasks import Subtask
# from schemas.subtasks_schema import SubtaskIn,SubtaskOut
# from models.task import Task
# from models.project import Project
# from models.user import User
# from utils.redis_service import cache_get, cache_set, cache_delete

# from handlers.task_handler import get_task_by_id
# import logging

# logger = logging.getLogger(__name__)


# def get_subtask_by_id(db: Session, subtask_id: int):
#     """Get subtask by ID with caching"""
    
#     # Check cache first
#     cached = cache_get(f"subtask_id:{subtask_id}")
    
#     if cached:
#         print(f"Cache hit: subtask_id:{subtask_id}")
#         return Subtask(**cached)
    
#     # Cache miss - query database
#     print(f"Cache miss: subtask_id:{subtask_id}")
#     subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    
#     # Cache the result (10 minutes)
#     if subtask:
#         subtask_dict = {
#             "id": subtask.id,
#             "title": subtask.title,
#             "description": subtask.description,
#             "status": subtask.status,
#             "task_id": subtask.task_id
#         }
#         cache_set(f"subtask_id:{subtask_id}", subtask_dict, expire_seconds=600)
    
#     return subtask


# def get_subtasks_by_task_id(db: Session, task_id: int, current_user: User):
#     """Get subtasks by task ID with role-based access"""
    
#     task = db.query(Task).filter(Task.id == task_id).first()
#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )
    
#     # Role-based access control
#     query = db.query(Subtask).join(Task).join(Project).filter(Subtask.task_id == task_id, Task.assigned_to == user.id, Task.project_id == Project.id, Project.org_id == user.org_id)

#     # If user is not admin, restrict to assigned subtasks
#     if user.role_name == "user":
#         query = query.filter(Subtask.assigned_to == user.id)

    
#     return subtasks


# def create_subtask(db: Session, s: Subtask, task_id: int, user: User):
#     """Create new subtask"""
    
#     task = db.query(Task).filter(
#         Task.id == task_id,
#         Task.owner_id == user.id
#     ).first()
    
#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found or unauthorized"
#         )

#     new_subtask = Subtask(
#         title=s.title,
#         description=s.description,
#         status=s.status,
#         task_id=task_id
#     )

#     db.add(new_subtask)
#     db.commit()
#     db.refresh(new_subtask)
    
#     # Clear cache
#     cache_delete(f"subtask_id:{new_subtask.id}")
#     cache_delete(f"subtasks:{task_id}:*")
    
#     return new_subtask


# def get_task_subtask(db: Session, task_id: int, user: User, page: int, no_records: int, search: str):
#     """Get paginated list of subtasks for a task with caching"""
    
#     # Create dynamic cache key
#     cache_key = f"subtasks:{user.org_id}:{task_id}:page:{page}:size:{no_records}"
    
#     if search:
#         cache_key += f":search:{search}"
    
#     # Check cache first
#     cached = cache_get(cache_key)
    
#     if cached:
#         logger.info(f"Cache hit: {cache_key}")
#         return cached
    
#     logger.info(f"Cache miss: {cache_key}")
    
#     # Get subtasks query
#     subtasks_query = get_subtasks_by_task_id(db, task_id, user)
    
#     # Apply search filter
#     if search:
#         subtasks_query = subtasks_query.filter(
#             Subtask.title.ilike(f"%{search}%")
#         )
    
#     # Get total count BEFORE pagination
#     total = subtasks_query.count()
    
#     if total == 0:
#         result = {
#             "page": page,
#             "records": no_records,
#             "total": 0,
#             "pages": 0,
#             "data": []
#         }
#         cache_set(cache_key, result, expire_seconds=300)
#         return result
    
#     # Calculate pages
#     pages = (total + no_records - 1) // no_records
    
#     if page > pages:
#         raise HTTPException(status_code=404, detail="Page out of range")
    
#     # Apply pagination and execute query
#     start = (page - 1) * no_records
#     paginated_subtasks = subtasks_query.offset(start).limit(no_records).all()
    
#     # Convert to dict matching schema
#     subtasks_data = []
#     for subtask in paginated_subtasks:
#         subtasks_data.append({
#             "id": subtask.id,
#             "title": subtask.title,
#             "description": subtask.description,
#             "status": subtask.status,
#             "task_id": subtask.task_id
#         })
    
#     # Build complete response
#     result = {
#         "page": page,
#         "records": no_records,
#         "total": total,
#         "pages": pages,
#         "data": subtasks_data
#     }
    
#     # Cache the result
#     cache_set(cache_key, result, expire_seconds=600)
#     logger.info(f"Cached: {cache_key}")
    
#     return result


# def update_subtask(db: Session, subtask_id: int, user: User, s: SubtaskIn):
#     """Update subtask"""
    
#     subtask = get_subtask_by_id(db, subtask_id)
    
#     if not subtask:
#         raise HTTPException(status_code=404, detail="Subtask not found")
    
#     subtask.title = s.title
#     subtask.description = s.description
#     subtask.status = s.status
    
#     db.commit()
#     db.refresh(subtask)
    
#     # Clear cache
#     cache_delete(f"subtask_id:{subtask_id}")
    
#     return subtask


# def delete_subtask(db: Session, subtask_id: int, user: User):
#     """Delete subtask"""
    
#     subtask = get_subtask_by_id(db, subtask_id)
    
#     if not subtask:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Subtask not found or unauthorized"
#         )

#     db.delete(subtask)
#     db.commit()
    
#     # Clear cache
#     cache_delete(f"subtask_id:{subtask_id}")
    

#     return {"msg": f"subtask {subtask_id} deleted"}






# handlers/task_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from schemas.task_schema import tasksIn
from models.subtasks import Subtask
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
    
    if user.role_name == "org_admin":
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

        tasks_data=[]
        tasks_data.append({
            
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
        "data": tasks_data
        }
        
        
        # Cache the result
        cache_set(cache_key, result, expire_seconds=600)
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
            cache_set(cache_key, result, expire_seconds=300)
            return result
    
    start = (page - 1) * no_records

    if start >= total:
        raise HTTPException(status_code=404, detail="Page out of range")

    paginated_data = query.offset(start).limit(no_records).all()
    pages = (total + no_records - 1) // no_records
    

    if page > pages:
        raise HTTPException(status_code=404, detail="Page out of range")



    return {
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data": paginated_data
    }





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
