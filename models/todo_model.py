from sqlalchemy import Column, Integer, String, Boolean 
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TodoModel(Base):
    __tablename__ = 'todos_table'

    id = Column(Integer, primary_key=True)  
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    completed = Column(Boolean, default=False)
 
    

