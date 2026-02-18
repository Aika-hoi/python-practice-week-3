import asyncio
from typing import List
from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas, database

app = FastAPI(title="Task Manager Full API")

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
    print("Ждем базу...")
    await asyncio.sleep(5)
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("База готова!")




@app.get("/tasks", response_model=List[schemas.TaskResponse], tags=["Tasks"])
async def read_tasks(db: AsyncSession = Depends(get_db)):
    """Получить все задачи"""
    return await crud.get_tasks(db)


@app.post("/tasks", response_model=schemas.TaskResponse, tags=["Tasks"])
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    """Создать новую задачу"""
    return await crud.create_task(db=db, task=task)



@app.post("/register", response_model=schemas.UserResponse, tags=["Auth"])
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    return await crud.create_user(db=db, user=user)


@app.post("/token", tags=["Auth"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """Вход и получение токена"""
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or form_data.password != user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/", tags=["General"])
async def root():
    return {"status": "ok", "message": "Backend is running with Auth and Tasks"}


