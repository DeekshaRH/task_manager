from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'task_manager'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[str]
    created_at: str
    updated_at: str

# Database connection
def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Initialize database
def init_db():
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
                priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
    except Error as e:
        print(f"Error initializing database: {e}")

# API Routes
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Task Manager API", "status": "running"}

@app.get("/api/tasks", response_model=List[Task])
def get_tasks(status: Optional[str] = None):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    if status:
        cursor.execute("SELECT * FROM tasks WHERE status = %s ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Convert datetime to string
    for task in tasks:
        task['created_at'] = task['created_at'].isoformat()
        task['updated_at'] = task['updated_at'].isoformat()
        if task['due_date']:
            task['due_date'] = task['due_date'].isoformat()
    
    return tasks

@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Convert datetime to string
    task['created_at'] = task['created_at'].isoformat()
    task['updated_at'] = task['updated_at'].isoformat()
    if task['due_date']:
        task['due_date'] = task['due_date'].isoformat()
    
    return task

@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """
        INSERT INTO tasks (title, description, status, priority, due_date)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (task.title, task.description, task.status, task.priority, task.due_date)
    )
    
    connection.commit()
    task_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    new_task = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    # Convert datetime to string
    new_task['created_at'] = new_task['created_at'].isoformat()
    new_task['updated_at'] = new_task['updated_at'].isoformat()
    if new_task['due_date']:
        new_task['due_date'] = new_task['due_date'].isoformat()
    
    return new_task

@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    existing_task = cursor.fetchone()
    
    if not existing_task:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Build update query dynamically
    update_fields = []
    update_values = []
    
    if task.title is not None:
        update_fields.append("title = %s")
        update_values.append(task.title)
    if task.description is not None:
        update_fields.append("description = %s")
        update_values.append(task.description)
    if task.status is not None:
        update_fields.append("status = %s")
        update_values.append(task.status)
    if task.priority is not None:
        update_fields.append("priority = %s")
        update_values.append(task.priority)
    if task.due_date is not None:
        update_fields.append("due_date = %s")
        update_values.append(task.due_date)
    
    if update_fields:
        update_values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(update_values))
        connection.commit()
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    updated_task = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    # Convert datetime to string
    updated_task['created_at'] = updated_task['created_at'].isoformat()
    updated_task['updated_at'] = updated_task['updated_at'].isoformat()
    if updated_task['due_date']:
        updated_task['due_date'] = updated_task['due_date'].isoformat()
    
    return updated_task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    
    if not task:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return {"message": "Task deleted successfully"}

@app.get("/api/stats")
def get_stats():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'pending'")
    pending = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'in_progress'")
    in_progress = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'")
    completed = cursor.fetchone()['count']
    
    cursor.close()
    connection.close()
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed
    }
