from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from utils.dependencies import get_current_user

from config.database import get_db
from model.user_model import User
from schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate, TaskListResponse
from servicies.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tareas"])

@router.post("/", response_model= TaskResponse, status_code=status.HTTP_201_CREATED)
def post_tasks(task_data:TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = TaskService(db=db)
    return service.create(task_data,current_user.id)

@router.get("/", response_model = list[TaskListResponse])
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = TaskService(db=db)
    return service.get_my_tasks(current_user.id)

@router.get("/{id}", response_model = TaskResponse)
def view_detail(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = TaskService(db=db)
    return service.view_details(id,current_user.id)

@router.put("/{id}", response_model = TaskResponse)
def update_task(id:int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = TaskService(db=db)
    return service.update(id , task_data, current_user.id)

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_task(id:int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = TaskService(db=db)
    return service.delete(id, current_user.id)