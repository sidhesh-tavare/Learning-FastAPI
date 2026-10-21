import os
import json
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException,status,Response
from psycopg.rows import dict_row
from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    title : str 
    description : str | None = None

class TaskUpdate(BaseModel):
    is_completed : bool
    updated_desc : str

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Task API")

def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )

@app.get("/",status_code=status.HTTP_200_OK)
def home()->None:
    return {"message" : "we are home"}
# print(DATABASE_URL)

@app.get("/tasks",status_code=status.HTTP_200_OK)
def get_tasks():
    conn = get_connection()
    with conn:
        curr = conn.cursor()
        with curr:
            query = """SELECT id, title , description, is_completed FROM tasks ORDER BY id DESC;"""
            curr.execute(query)
            tasks = curr.fetchall()
    return json.dumps(tasks)

@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def post_tasks(task:TaskCreate):
    conn = get_connection()
    curr = conn.cursor()
    with conn:
        with curr:
            query =  """
                            INSERT INTO tasks (title,description)
                            VALUES (%s,%s)
                            RETURNING id,title,description,is_completed,created_at;
                            """
            curr.execute(query,(task.title , task.description))
            new_task = curr.fetchone()
            print(type(new_task),new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id:int , task:TaskUpdate):
    conn = get_connection()
    curr = conn.cursor()
    with conn:
        with curr:
            query = """
                        UPDATE tasks
                        SET is_completed = %s, description  = %s
                        WHERE id = %s
                        RETURNING *
                    """
            params = (task.is_completed,task.updated_desc , task_id)
            curr.execute(query,params)
            updated_task = curr.fetchone()

    if updated_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    return updated_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id : int):
    conn = get_connection()
    curr = conn.cursor()
    with conn:
        with curr:
            query = """ DELETE FROM tasks WHERE id = %s RETURNING * """
            params = (task_id,)
            curr.execute(query,params)
            deleted_task = curr.fetchone()

    if deleted_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task Not Found"
        )
    
    return {"message" : "Task deleted successfully" , "deleted_task" : deleted_task}