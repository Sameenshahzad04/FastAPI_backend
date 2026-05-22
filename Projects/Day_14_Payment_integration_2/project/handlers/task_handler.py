# handlers/task_handler.py

from sqlalchemy.orm import Session, join, joinedload
from fastapi import HTTPException, status
from schemas.task_schema import TaskOut,tasksIn
from models.task import Task
from models.project import Project
from models.user import User

def create_task(db: Session, title: str, des: str, status_value: str, project_id: int, user: User):
     
    
    proj = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
        Project.org_id == user.org_id
        ).first()
    
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    new_task = Task(
        title=title,
        des=des,
        status=status_value,
        project_id=project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def assign_task_to_user(db: Session, task_id: int, user_id: int,assigner: User):

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = db.query(User).filter(User.id == user_id, User.role_name == "user",User.org_id == assigner.org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or not a normal user")

    task.assigned_to = user.id
    db.commit()
    db.refresh(task)
    return task

def get_project_tasks(db: Session, project_id: int, user:User, page: int, no_records: int,search:str):

    tasks = db.query(Task).join(Project).filter.filter(Task.project_id == project_id,Project.org_id == user.org_id)
    
    if user.role_name=="user":

        tasks = db.query(Task).join(Project).filter(Task.project_id == project_id, Task.assigned_to == user.id,Project.org_id == user.org_id)
   


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

    total = tasks.count()
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
    
    
    return {
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data": paginated_data
    }


def update_task(db: Session, task_id: int, user: User,t:tasksIn):

    if user.role_name=="org_admin":
        task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user.id,
        Project.org_id == user.org_id
        ).first()
        task.title = t.title
        task.des = t.des
    else:
        task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Task.assigned_to == user.id,
        Project.org_id == user.org_id
        ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    if user.role_name == "org_admin":
        # Admin can update everything
        task.title = t.title
        task.des   = t.des
        task.status = t.status
    else:
        # Regular user → only status
        task.status = t.status
        #  warning if client tried to change other fields
        if t.title != task.title or t.des != task.des:
            
             raise HTTPException(422, "Regular users can only update status")

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, user: User):

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user.id,
        Project.org_id == user.org_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    db.delete(task)
    db.commit()

    return {"msg": f"task {task_id} deleted"}
