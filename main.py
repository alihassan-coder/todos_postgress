from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from config.database import SessionLocal, engine
from models.todo_model import Base, TodoModel
from pydantic import BaseModel

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for validation
class TodoCreate(BaseModel):
    title: str
    description: str = None  # type: ignore
    completed: bool = False

class TodoResponse(TodoCreate):
    id: int

    class Config:
        orm_mode = True

# ✅ Create a new Todo with exception handling
@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    try:
        db_todo = TodoModel(title=todo.title, description=todo.description, completed=todo.completed)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ✅ Get all Todos with exception handling
@app.get("/todos/", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    try:
        return db.query(TodoModel).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ✅ Get a Todo by ID with exception handling
@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ✅ Update a Todo with exception handling
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoCreate, db: Session = Depends(get_db)):
    try:
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        todo.title = todo_update.title
        todo.description = todo_update.description
        todo.completed = todo_update.completed
        db.commit()
        db.refresh(todo)
        return todo
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ✅ Delete a Todo with exception handling
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        db.delete(todo)
        db.commit()
        return {"message": "Todo deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
