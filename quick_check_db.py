# quick_check_db.py
import asyncio
from sqlalchemy import select

from app.db.postgres import AsyncSessionLocal
from app.db.models import User, History, SmsPurchase, UserTask, UserXP


async def main():
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User.user_id))).all()
        print("Users count:", len(users))

        history = (await session.execute(select(History.id))).all()
        print("History count:", len(history))

        tasks = (await session.execute(select(UserTask.user_id, UserTask.task_code))).all()
        print("UserTasks count:", len(tasks))

        purchases = (await session.execute(select(SmsPurchase.id))).all()
        print("SmsPurchases count:", len(purchases))

        xp_rows = (await session.execute(select(UserXP.user_id, UserXP.xp))).all()
        print("UserXP rows:", len(xp_rows))


if __name__ == "__main__":
    asyncio.run(main())
