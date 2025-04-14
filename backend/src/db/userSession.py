from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

class InstagramAccountManager:
    def __init__(self, mongo_uri="mongodb://localhost:27017", db_name="insta_ids"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db.instagram_accounts

    async def get_available_account(self, scraper_id: int):
        now = datetime.utcnow()
        account = await self.collection.find_one_and_update(
            {
                "status": "idle",
                "cooldown_until": {"$lte": now},
                "assigned": scraper_id,
                "banstatus": "perfect"
            },
            {
                "$set": {"status": "in_process"}
            },
            sort=[("cooldown_until", 1)]
        )
        return account

    async def set_cooldown(self, username: str, cooldown_secs: int = 300):
        await self.collection.update_one(
            {"username": username},
            {
                "$set": {
                    "status": "cooldown",
                    "cooldown_until": datetime.utcnow() + timedelta(seconds=cooldown_secs)
                }
            }
        )

    async def release_account(self, username: str):
        await self.collection.update_one(
            {"username": username},
            {
                "$set": {
                    "status": "idle",
                    "cooldown_until": None
                }
            }
        )

    async def update_banstatus(self, username: str, status: str):
        await self.collection.update_one(
            {"username": username},
            {
                "$set": {
                    "banstatus": status
                }
            }
        )

    async def insert_account(self, username, password ,session_path, assigned):
        await self.collection.insert_one({
            "username": username,
            "password": password,
            "status": "idle",
            "cooldown_until": datetime.utcnow(),
            "assigned": assigned,
            "sessionDir": session_path,
            "banstatus": "perfect"
        })

import asyncio
async def main():
    manager = InstagramAccountManager()
    
    account = await manager.get_available_account(scraper_id=1)
    if not account:
        print("No available account.")
        return

    print(f"Using account: {account['username']}")

    # simulate scrape
    await asyncio.sleep(2)

    # Set cooldown
    await manager.set_cooldown(account['username'], cooldown_secs=300)

asyncio.run(main())