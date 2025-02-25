# FastAPI To-Do App with Alembic and PostgreSQL

## Installation
To set up the project with Alembic and PostgreSQL, install the required dependencies:
```sh
pip install fastapi[all] alembic psycopg2-binary uvicorn
```

## New Project Setup
Follow these steps to initialize Alembic and configure it for database migrations:

1. **Initialize Alembic**
   ```sh
   alembic init alembic
   ```
2. **Set the Database URL**
   - Locate the `alembic.ini` file.
   - Modify the `sqlalchemy.url` entry to point to your PostgreSQL database, e.g.:
     ```ini
     sqlalchemy.url = postgresql+psycopg2://user:password@localhost/dbname
     ```

3. **Create SQLAlchemy Model**
   - Define a SQLAlchemy model for your table, for example:
     ```python
     from sqlalchemy import Column, Integer, String
     from sqlalchemy.ext.declarative import declarative_base

     Base = declarative_base()

     class Todo(Base):
         __tablename__ = 'todos'
         id = Column(Integer, primary_key=True, index=True)
         title = Column(String, nullable=False)
         description = Column(String, nullable=True)
     ```

4. **Set Target Metadata in Alembic**
   - Open `alembic/env.py` and update the target metadata:
     ```python
     from models import Base  # Import the model base
     target_metadata = Base.metadata
     ```

## Running Migrations
Whenever you make changes to your models, run the following commands:

1. **Generate Migration Script**
   ```sh
   alembic revision --autogenerate -m "create todos table"
   ```

2. **Apply Migrations**
   ```sh
   alembic upgrade head
   ```

This will create and apply the necessary database schema changes based on your models.

## CRUD Operations

### Create a To-Do
To create a new to-do item, define an endpoint in your FastAPI app:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Todo, Base
from database import engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)

class TodoCreate(BaseModel):
    title: str
    description: str = None

@app.post("/todos/", response_model=TodoCreate)
def create_todo(todo: TodoCreate, db: Session = SessionLocal()):
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
```

### Read To-Dos
To read all to-do items:
```python
@app.get("/todos/")
def read_todos(skip: int = 0, limit: int = 10, db: Session = SessionLocal()):
    todos = db.query(Todo).offset(skip).limit(limit).all()
    return todos
```

### Update a To-Do
To update an existing to-do item:
```python
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoCreate, db: Session = SessionLocal()):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo
```

### Delete a To-Do
To delete a to-do item:
```python
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = SessionLocal()):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"detail": "Todo deleted"}
```

## Running the Application
To run the FastAPI application with Uvicorn:
```sh
uvicorn main:app --reload
```

This will provide a complete CRUD interface for managing to-do items in your FastAPI application.
