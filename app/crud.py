from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_tasks(db: AsyncSession, completed: bool = None):
    query = select(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    result = await db.execute(query)
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(models.Task).filter(models.Task.id == task_id))
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update_task(db: AsyncSession, task_id: int, task_update: schemas.TaskUpdate):
    db_task = await get_task(db, task_id)
    if db_task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        await db.commit()
        await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int):
    db_task = await get_task(db, task_id)
    if db_task:
        await db.delete(db_task)
        await db.commit()
        return True
    return False