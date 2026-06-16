from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.task_model import Task
from repositories.task_repository import TaskRepository
from schemas.task_schema import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, db: Session):
        self.task_repository = TaskRepository(db=db)
    
    def create(self, task: TaskCreate, user_id: int):
        new_task = Task(
            title = task.title,
            description = task.description,
            priority = task.priority,
            owner_user = user_id
        )
        return self.task_repository.create(new_task)
    
    def get_my_tasks(self, user_id:int):
        return self.task_repository.get_by_user_id(user_id)
    
    def view_details(self, task_id: int, user_id:int):
        belong_task = self.task_repository.get_by_id_and_user(task_id, user_id)
        if not belong_task:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail="La tarea no fue encontrada"
            )
        return belong_task
    
    def update(self, task_id:int, task: TaskUpdate, user_id: int):
        belong_task = self.task_repository.get_by_id_and_user(task_id, user_id)
        if not belong_task:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail="La tarea no fue encontrada"
            )
        belong_task.title = task.title
        belong_task.description = task.description
        belong_task.status = task.status
        belong_task.priority = task.priority
        return self.task_repository.update(belong_task)
    
    def delete(self, task_id: int, user_id: int):
        belong_task = self.task_repository.get_by_id_and_user(task_id, user_id)
        if not belong_task:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail="La tarea no fue encontrada"
            )
        return self.task_repository.delete(belong_task)
