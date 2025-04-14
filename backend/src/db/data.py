import traceback
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

# --------- Mongo Setup ---------
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["Scrapper"]
users_collection = db["users_complete"]

#---------- Async User Complete Data Model --------------
class ExtendedUser:
    def __init__(
        self,
        username: str,
        fullname: str,
        isprivate: bool,
        profile_pic_url: str,
        is_business_account: bool,
        is_professional_account: bool,
        account_type: int,
        bio: str,
        bio_links: list,
        action_button: list,
        email: list,
        search_id,
        api_used: str,
        _id=None, created_at=None, **kwargs
    ):
        if not isinstance(username, str):
            raise ValueError("username must be a string")
        if not isinstance(fullname, str):
            raise ValueError("fullname must be a string")
        if not isinstance(isprivate, bool):
            raise ValueError("isprivate should be a boolean")
        if not isinstance(is_business_account, bool):
            raise ValueError("is_business_account should be a boolean")
        if not isinstance(is_professional_account, bool):
            raise ValueError("is_professional_account should be a boolean")
        if not isinstance(profile_pic_url, str):
            raise ValueError("profile_pic_url must be a string")
        if not isinstance(bio, str):
            raise ValueError("bio must be a string")
        if not isinstance(bio_links, list):
            raise ValueError("bio_links must be a list")
        if not isinstance(action_button, list):
            raise ValueError("action_button must be a list")
        if not isinstance(email, list):
            raise ValueError("email must be a list")
        if not isinstance(search_id, (str, ObjectId, list)):
            raise ValueError("search_id must be a string, ObjectId, or list of them")
        if isinstance(search_id, list):
            if not all(isinstance(sid, (str, ObjectId)) for sid in search_id):
                raise ValueError("All items in search_id must be strings or ObjectIds")

        self.username = username
        self.fullname = fullname
        self.isprivate = isprivate
        self.is_professional_account = is_professional_account
        self.is_business_account = is_business_account
        self.account_type = account_type
        self.profile_pic_url = profile_pic_url
        self.bio = bio
        self.bio_links = bio_links
        self.action_button = action_button
        self.email = email
        self.api_used = api_used
        UTC = timezone.utc
        self.created_at = created_at or datetime.now(UTC)
        self._id = ObjectId(_id) if _id else None

        if isinstance(search_id, list):
            self._search_ids = [ObjectId(sid) if isinstance(sid, str) else sid for sid in search_id]
        else:
            self._search_ids = [ObjectId(search_id) if isinstance(search_id, str) else search_id]

        for key, value in kwargs.items():
            setattr(self, key, value)

    async def __aenter__(self):
        try:
            indexes = await users_collection.index_information()
            if not any(i.get("key") == [('username', 1)] for i in indexes.values()):
                await users_collection.create_index("username", unique=True)
        except Exception as e:
            print(f"Error setting up index: {e}")
        finally:
            return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def to_dict(self):
        doc = {
            "username": self.username,
            "fullname": self.fullname,
            "isprivate": self.isprivate,
            "is_professional_account": self.is_professional_account,
            "is_business_account": self.is_business_account,
            "account_type": self.account_type,
            "profile_pic_url": self.profile_pic_url,
            "bio": self.bio,
            "bio_links": self.bio_links,
            "action_button": self.action_button,
            "email": self.email,
            "api_used": self.api_used,
            "search_ids": self._search_ids,
            "created_at": self.created_at
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
                try:
                    result = await users_collection.insert_one(self.to_dict())
                    self._id = result.inserted_id
                    return result.inserted_id
                except DuplicateKeyError:
                    print(f"Duplicate username: {self.username}")
                    existing = await self.find_by_username(self.username)
                    if existing:
                        self._id = existing._id
                        await users_collection.update_one(
                            {"_id": self._id},
                            {
                                "$addToSet": {"search_ids": {"$each": self._search_ids}},
                                "$set": {
                                    "fullname": self.fullname,
                                    "isprivate": self.isprivate,
                                    "is_professional_account": self.is_professional_account,
                                    "is_business_account": self.is_business_account,
                                    "account_type": self.account_type,
                                    "profile_pic_url": self.profile_pic_url,
                                    "bio": self.bio,
                                    "bio_links": self.bio_links,
                                    "action_button": self.action_button,
                                    "email": self.email,
                                }
                            }
                        )
                        return self._id
                    return None
        except Exception as e:
            print(f"Error in saving user: {e}")
            traceback.print_exc()
            return None

    async def update(self, **kwargs):
        if not self._id:
            raise ValueError("Cannot update unsaved document")
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return await self.save()

    @staticmethod
    async def find_by_id(user_id):
        try:
            doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if doc:
                return ExtendedUser(
                    username=doc["username"],
                    fullname=doc["fullname"],
                    isprivate=doc["isprivate"],
                    is_professional_account=doc["is_professional_account"],
                    is_business_account=doc["is_business_account"],
                    account_type=doc["account_type"],
                    profile_pic_url=doc["profile_pic_url"],
                    bio=doc["bio"],
                    bio_links=doc["bio_links"],
                    action_button=doc["action_button"],
                    email=doc["email"],
                    api_used=doc["api_used"],
                    search_id=doc.get("search_ids", []),
                    _id=str(doc["_id"]),
                    created_at=doc.get("created_at")
                )
            return None
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None

    @staticmethod
    async def find_by_username(username):
        try:
            doc = await users_collection.find_one({"username": username})
            if doc:
                return ExtendedUser(
                    username=doc["username"],
                    fullname=doc["fullname"],
                    isprivate=doc["isprivate"],
                    is_professional_account=doc["is_professional_account"],
                    is_business_account=doc["is_business_account"],
                    account_type=doc["account_type"],
                    profile_pic_url=doc["profile_pic_url"],
                    bio=doc["bio"],
                    bio_links=doc["bio_links"],
                    action_button=doc["action_button"],
                    email=doc["email"],
                    api_used=doc["api_used"],
                    search_id=doc.get("search_ids", []),
                    _id=str(doc["_id"]),
                    created_at=doc.get("created_at")
                )
            return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None

    @staticmethod
    async def find_by_search_id(search_id):
        try:
            sid = ObjectId(search_id) if isinstance(search_id, str) else search_id
            cursor = users_collection.find({"search_ids": sid})
            results = []
            async for doc in cursor:
                results.append(ExtendedUser(
                    username=doc["username"],
                    fullname=doc["fullname"],
                    isprivate=doc["isprivate"],
                    is_professional_account=doc["is_professional_account"],
                    is_business_account=doc["is_business_account"],
                    account_type=doc["account_type"],
                    profile_pic_url=doc["profile_pic_url"],
                    bio=doc["bio"],
                    bio_links=doc["bio_links"],
                    action_button=doc["action_button"],
                    email=doc["email"],
                    api_used=doc["api_used"],
                    search_id=doc.get("search_ids", []),
                    _id=str(doc["_id"]),
                    created_at=doc.get("created_at")
                ))
            return results
        except Exception as e:
            print(f"Error finding users by search_id: {e}")
            return []
    @staticmethod
    async def preview_by_search_id(search_id):
        try:
            sid = ObjectId(search_id) if isinstance(search_id, str) else search_id
            cursor = users_collection.find({"search_ids": sid})
            results = []
            async for doc in cursor:
                results.append({
                    "username": doc["username"],
                    "account_type": doc["account_type"],
                    "profile_pic_url": doc["profile_pic_url"],
                    "bio": doc["bio"],
                    "email": doc["email"]
                })
            return results
        except Exception as e:
            print(f"Error finding users by search_id: {e}")
            return []
    
async def scan():
    data = ExtendedUser
    content = await data.preview_by_search_id("67f7f1972a94201d7db8f3e8")
    print(content)
if __name__=="__main__":
    asyncio.run(scan())