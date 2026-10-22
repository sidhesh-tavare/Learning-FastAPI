import os
import json
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Response
from psycopg.rows import dict_row
from datetime import datetime
from models.models import TaskCreate, TaskUpdate
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Sets the minimum severity level to log
    format="%(asctime)s - %(levelname)s - %(message)s",  # How the log line looks
    handlers=[
        logging.FileHandler("app.log"),  # Saves logs to a file named app.log
        logging.StreamHandler()         # Displays logs in your terminal window
    ]
)

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Task API")

def get_connection():
    # Opened in block execution to ensure it returns a cleanly closeable object
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )

@app.get("/", status_code=status.HTTP_200_OK)
def home() -> dict:
    logging.info("User checked by root dir ")
    return {"message": "we are home"}


@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_tasks(skip: int = 0, limit: int = 10):
    # 'with get_connection()' ensures the connection closes even if errors occur
    with get_connection() as conn:
        with conn.cursor() as curr:
            query = """SELECT id, title, description, is_completed FROM tasks ORDER BY id DESC;"""
            curr.execute(query)
            tasks = curr.fetchall()
    logging.info(f"User fetched all tasks skip ={skip} and limit = {limit}")
    return tasks[skip:skip + limit] # Fixed standard pagination logic
    

@app.get("/tasks/{task_id}",status_code=status.HTTP_200_OK)
def get_by_id(task_id : int , response : Response):
    with get_connection() as conn:
        with conn.cursor() as curr:
            query = """SELECT id,title,description,is_completed FROM tasks WHERE id = %s"""
            params = (task_id,)
            curr.execute(query,params)
            fetched_task = curr.fetchone()
        if not fetched_task : 
            response.status_code = status.HTTP_404_NOT_FOUND
        else : 
            response.status_code=status.HTTP_200_OK
    return {"fetched_task" : fetched_task , "response" : response} if fetched_task is not None else {"message" : "NOT Found" , "response" : response}



@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def post_tasks(task: TaskCreate):
    with get_connection() as conn:
        with conn.cursor() as curr:
            query = """
                INSERT INTO tasks (title, description)
                VALUES (%s, %s)
                RETURNING id, title, description, is_completed, created_at;
            """
            curr.execute(query, (task.title, task.description))
            new_task = curr.fetchone()
            conn.commit()  # <-- CRITICAL: Must commit transaction to free database locks
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    with get_connection() as conn:
        with conn.cursor() as curr:
            query = """
                UPDATE tasks
                SET is_completed = %s, description = %s
                WHERE id = %s
                RETURNING *;
            """
            # Assumed task.description fallback if task.updated_desc is empty
            desc_to_update = getattr(task, 'updated_desc', getattr(task, 'description', None))
            params = (task.is_completed, desc_to_update, task_id)
            
            curr.execute(query, params)
            updated_task = curr.fetchone()
            conn.commit()  # <-- CRITICAL: Saves changes and ends transaction safely

    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        with conn.cursor() as curr:
            query = """ DELETE FROM tasks WHERE id = %s RETURNING *; """
            params = (task_id,)
            curr.execute(query, params)
            deleted_task = curr.fetchone()
            conn.commit()  # <-- CRITICAL: Finalizes the row deletion

    if deleted_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task Not Found"
        )
    
    return {"message": "Task deleted successfully", "deleted_task": deleted_task}
