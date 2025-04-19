from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

class InstagramAccountManager:
    def __init__(self, mongo_uri="mongodb://localhost:27017", db_name="insta_ids"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db.instagram_accounts

    async def load_all_accounts(self):
       cursor = self.collection.find(
           {},
           {"_id": 0, "username": 1, "status": 1, "banstatus": 1, "scraper" : 1}
       )
       return await cursor.to_list(length=None)


    async def get_available_account(self, scraper_id: str):
        now = datetime.utcnow()
        account = await self.collection.find_one_and_update(
            {
                "status": {"$in": ["idle", "cooldown"]},
                "cooldown_until": {"$lte": now},
                "scraper": scraper_id,
                "banstatus": "perfect"
            },
            {
                "$set": {"status": "in_process"}
            },
            sort=[("cooldown_until", 1)]
        )
        return account

    async def set_cooldown(self, username: str, cooldown_secs: int = 30):
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
        try:
            await self.collection.insert_one({
                "username": username,
                "password": password,
                "status": "idle",
                "cooldown_until": datetime.utcnow(),
                "scraper": assigned,
                "sessionDir": session_path,
                "banstatus": "perfect"
            })
            return True
        except Exception as e:
            print(e)
            return False
    async def reset_expired_cooldowns(self):
        '''
        This will reset the cooldown status
        and should be called on ws request as it's essential for frontend to have accurate data and backend has the handler to buypass its use
        '''
        now = datetime.utcnow()
        await self.collection.update_many(
            {
                "status": "cooldown",
                "cooldown_until": {"$lte": now}
            },
            {
                "$set": {"status": "idle"}
            }
        )

import asyncio
async def main():
    manager = InstagramAccountManager()
    
    account = await manager.get_available_account(scraper_id = "scraper1")
    if not account:
        print("No available account.")
        return
    print(account)
    print(f"Using account: {account['username']}")

    # simulate scrape
    await asyncio.sleep(2)

    # Set cooldown
    await manager.set_cooldown(account['username'], cooldown_secs=300)
if __name__=="__main__":
    asyncio.run(main())