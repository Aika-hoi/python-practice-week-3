from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

try:
    from app import crud, models, schemas, database
except ImportError:
    import crud, models, schemas, database
app = FastAPI(title="Task Manager API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db():
    async with database.SessionLocal() as session:
        yield session


@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/tasks", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_task(db=db, task=task)

@app.get("/tasks", response_model=List[schemas.TaskResponse])
async def read_tasks(completed: bool = None, db: AsyncSession = Depends(get_db)):
    return await crud.get_tasks(db, completed=completed)

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: int, task_update: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)):
    db_task = await crud.update_task(db, task_id=task_id, task_update=task_update)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}