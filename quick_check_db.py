# quick_check_db.py
import asyncio
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.db.models import User, History, SmsPurchase, UserTask

async def main():
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User.user_id, User.username))).all()
        print("Users count:", len(users))

        history = (await session.execute(select(History.id, History.user_id))).all()
        print("History count:", len(history))

        purchases = (await session.execute(select(SmsPurchase.id, SmsPurchase.user_id))).all()
        print("Purchases count:", len(purchases))

        tasks = (await session.execute(select(UserTask.user_id, UserTask.task_code))).all()
        print("UserTasks count:", len(tasks))

if __name__ == "__main__":
    asyncio.run(main())
