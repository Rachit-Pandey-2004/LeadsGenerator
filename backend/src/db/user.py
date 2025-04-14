import traceback
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from datetime import datetime, timezone  # Import UTC timezone
from pymongo.errors import DuplicateKeyError

# --------- Mongo Setup ---------
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["Scrapper"]
users_collection = db["users_waitlist"]

# --------- Async User Model ---------
class User:
    def __init__(
            self, username: str, 
            fullname: str, 
            isprivate: bool, 
            is_business_account: bool, 
            is_professional_account:bool,
            account_type : int,
            profile_pic_url: str, 
            search_id: str,
            scanned: bool=False, 
            _id=None, 
            created_at=None
            ):
        if not isinstance(username, str):
            raise ValueError("Name must be a string")
        if not isinstance(fullname, str):
            raise ValueError("fullname must be a string")
        if not isinstance(isprivate, bool):
            raise ValueError("isPrivate should have boolean values")
        if not isinstance(scanned, bool):
            raise ValueError("scanned should have boolean values")
        if not isinstance(profile_pic_url, str):
            raise ValueError("img url must be a string")
        if not isinstance(is_business_account, bool):
            raise ValueError("is_business_account should have boolean values")
        if not isinstance(is_professional_account, bool):
            raise ValueError("is_professional_account should have boolean values")
        if not isinstance(account_type, int):
            raise ValueError("account_type should have integer values")
        if not isinstance(search_id , (str, ObjectId)):
            raise ValueError("must be a string")
        self.username = username
        self.fullname = fullname
        self.isprivate = isprivate
        self.is_professional_account= is_professional_account
        self.is_business_account =is_business_account
        self.account_type = account_type
        self.scanned = scanned
        self.profile_pic_url = profile_pic_url 
        self._search_ids = [ObjectId(search_id)]
        UTC = timezone.utc
        self.created_at = created_at or datetime.now(UTC)
        self._id = ObjectId(_id) if _id else None

    async def __aenter__(self):
        try:
            # Check if index exists and create if not
            indexes = await users_collection.index_information()
            if not any(i.get("key")==[('username',1)]for i in indexes.values()):
                await users_collection.create_index("username", unique=True)
        except Exception as e:
            print(f"Error setting up index: {e}")
        # Return self for context manager
        return self
        
    async def __aexit__(self, exc_type, exc_value, traceback):
        print("⛔ Exiting User context manager")
        # Nothing to clean up
        pass
    
    def to_dict(self):
        doc = {
            "username": self.username,
            "fullname": self.fullname,
            "isprivate": self.isprivate,
            "is_professional_account": self.is_professional_account,
            "is_business_account": self.is_business_account ,
            "account_type":self.account_type,
            "scanned": self.scanned,
            "profile_pic_url": self.profile_pic_url,
            "search_ids": self._search_ids,
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
                try:
                    result = await users_collection.insert_one(self.to_dict())
                    self._id = result.inserted_id
                    return result.inserted_id
                except DuplicateKeyError:
                    print(f"Duplicate username: {self.username}")
                    # Handle duplicate by finding existing record
                    existing = await self.find_by_username(self.username)
                    if existing:
                        self._id = existing._id
                        
                        await users_collection.update_one(
                            {"_id": self._id},
                            {
                                "$addToSet": {"search_ids": {"$each": self._search_ids}},  # avoids duplicates
                                "$set": {
                                    "fullname": self.fullname,
                                    "isprivate": self.isprivate,
                                    "is_professional_account": self.is_professional_account,
                                    "is_business_account": self.is_business_account,
                                    "account_type": self.account_type,
                                    "scanned": self.scanned,
                                    "profile_pic_url": self.profile_pic_url,
                                }
                            }
                        )
                        return self._id
                    return None
        except Exception as e:
            print(f"Error saving user: {e}")
            traceback.print_exc()
            return None

    async def update(self, **fields):
        if not self._id:
            raise ValueError("Cannot update unsaved document")

        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return await self.save()

    @staticmethod
    async def find_by_id(user_id):
        try:
            doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if doc:
                return User(**doc)
            return None
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None
            
    @staticmethod
    async def find_by_username(username):
        try:
            doc = await users_collection.find_one({"username": username})
            if doc:
                return User(**doc)
            return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None
    @staticmethod
    async def find_by_scanned_status(scanned: bool):
        '''
        Returns all items matching the scanned status
        '''
        try:
            result = []
            cursor = users_collection.find({"scanned": scanned})
            async for doc in cursor:
                try:
                    user = User(
                        username=doc["username"],
                        fullname=doc["fullname"],
                        isprivate=doc["isprivate"],
                        is_professional_account=doc["is_professional_account"],
                        is_business_account=doc["is_business_account"],
                        account_type=doc["account_type"],
                        scanned=doc.get("scanned", False),
                        profile_pic_url=doc["profile_pic_url"],
                        search_id=str(doc["search_ids"][0]) if doc.get("search_ids") else "",
                        _id=doc["_id"],
                        created_at=doc.get("created_at")
                    )
                    result.append(user)
                except Exception as e:
                    print(f"Error processing document: {e}")
                    continue
            return result
        except Exception as e:
            print(f"Error in find_by_scanned_status: {e}")
            traceback.print_exc()
            return []
async def main():
    # Create and save a user
    url="https://instagram.fagr1-4.fna.fbcdn.net/v/t51.2885-19/468902712_1094963502279575_5702933051297399466_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_ht=instagram.fagr1-4.fna.fbcdn.net&_nc_cat=111&_nc_oc=Q6cZ2QHG7Kl_aQu-DFtMYCePZ7lqrq0aEF5eA5bwgdzaxb5SQwTNrKPE-ZpRWrsq9AA4q9zCnuSQlFhXYrf2JhTGvBCy&_nc_ohc=9V2IDH8madIQ7kNvwHu2I_o&_nc_gid=OnUenx0jbODkJWAxcMvtaA&edm=AFlAz-oBAAAA&ccb=7-5&oh=00_AYEQ7AD5E6GRRVSSXuGhRMZtoxMV7RzVTPIncucL85MLUg&oe=67F6EADE&_nc_sid=76c0fc"
    async with User(username="antomassoni", fullname="ANTO MASSONI", profile_pic_url=url, isprivate=False,is_business_account=False, is_professional_account=False,account_type=1) as user:
        inserted_id = await user.save()
        # print("Inserted ID:", inserted_id)
    
        # # Update the user
        # await user.update(isprivate=True)
        # print("Updated Age:", user.isprivate)
    
        # # Fetch user by ID
        # # fetched_user = await User.find_by_id(inserted_id)
        # fetched_user = await User.find_by_username("antomassoni")
        # if fetched_user:
        #     print("Fetched User:", fetched_user.to_dict())

# Run the async main
if __name__ == "__main__":
    asyncio.create_task(main())

