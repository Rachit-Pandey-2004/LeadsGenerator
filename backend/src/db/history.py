'''
This is non-context manager implementation of user.py
'''

import traceback
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

# --------- Mongo Setup ---------
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["Scrapper"]
users_collection = db["history"]

# --------- Async User Model ---------
'''Status : "pending," "in_progress," "completed" '''
class History:
    def __init__(
        self, 
        status: str, 
        query_type: str,
        query: list,
        limit: int,
        _id=None, 
        created_at=None
    ):
        if not isinstance(status, str):
            raise ValueError("Status must be a string")
        if not isinstance(query_type, str):
            raise ValueError("query_type must be a string")
        if not isinstance(query, list):
            raise ValueError("query must be a list")
        if not isinstance(limit, int):
            raise ValueError("limit must be an integer")

        self.status = status
        self.query_type = query_type
        self.query = query
        self.limit = limit
        UTC = timezone.utc
        self.created_at = created_at or datetime.now(UTC)
        self._id = ObjectId(_id) if _id else None

    def to_dict(self):
        doc = {
            "status": self.status,
            "query_type": self.query_type,
            "query": self.query,
            "limit": self.limit,
            "created_at": self.created_at,
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    async def save(self):
        try:
            if self._id:
                result = await users_collection.update_one(
                    {"_id": self._id},
                    {"$set": self.to_dict()}
                )
                return result.modified_count
            else:
                result = await users_collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return result.inserted_id

        except Exception as e:
            print(f"[MongoDB] Error saving user: {e}")
            traceback.print_exc()
            return None

    async def update(self, **fields):
        try:
            if not self._id:
                raise ValueError("Cannot update unsaved document")
            for key, value in fields.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            return await self.save()
        except Exception as e:
            print(e)
            return False

    @staticmethod
    async def find_by_id(search_id):
        try:
            doc = await users_collection.find_one({"_id": ObjectId(search_id)})
            if doc:
                return History(**doc)
            return None
        except Exception as e:
            print(f"[MongoDB] Error finding by ID: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    async def find_by_status(status):
        try:
            cursor = users_collection.find({"status": status})
            results = []
            async for doc in cursor:
                results.append(History(**doc))
            return results
        except Exception as e:
            print(f"[MongoDB] Error finding by status: {e}")
            traceback.print_exc()
            return []
    @staticmethod
    async def find_all():
        try:
            cursor = users_collection.find()
            results = []
            async for doc in cursor:
                results.append(History(**doc))
            return results
        except Exception as e:
            print(f"[MongoDB] Error fetching all users: {e}")
            traceback.print_exc()
            return []
    @staticmethod
    async def find_all_as_dicts():
        cursor = users_collection.find({})
        results = []
        async for doc in cursor:
            doc['_id'] = str(doc['_id'])
            doc['created_at'] = doc['created_at'].isoformat()
            results.append(doc)
        return results