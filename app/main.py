from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from . import crud, models, schemas, database

app = FastAPI()

# Разрешаем браузеру общаться с сервером
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

@app.get("/tasks", response_model=List[schemas.TaskResponse])
async def read_tasks(db: AsyncSession = Depends(get_db)):
    return await crud.get_tasks(db)

@app.post("/tasks", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_task(db=db, task=task)
