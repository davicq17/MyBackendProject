from sqlalchemy.orm import Session
from model.task_model import Task

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == id).first()

    def get_by_id_and_user(self, task_id:int, user_id:int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id, Task.owner_user == user_id).first()
    
    def get_by_user_id(self, user_id: int) -> list[Task]:
        return self.db.query(Task).filter(Task.owner_user == user_id).all()
    
    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return(task)

    def delete(self, task: Task):
        self.db.delete(task)
        self.db.commit()

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return(task)