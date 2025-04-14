'''
Email can be found in :
private and public account : can use dorking (google and ducduckgo ) and non login web api
- bio
- links
public account : mobile api
- action button

need to implement id rotation . . . and pickling or session save and reuse is need to set

'''
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from db import ExtendedUser
from db import User
from ensta import Guest
import  random
def extract_emails(text):
    # Regex pattern for extracting email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


class Insta_user_profile:
    def __init__(self,content:dict[str,any],client):
        self.cl = client
        
        self.id =content['_id']
        self.username = content['username']
        self.fullname = content['fullname']
        self.isprivate = content['isprivate']
        self.is_professional_account = content['is_professional_account']
        self.is_business_account = content['is_business_account']
        self.account_type = content['account_type']
        self.profile_pic_url = content['profile_pic_url']
        self.search_ids = content['search_ids']
        # for later use
    

    async def insta_guest_api(self):
        try:
            guest = Guest()
            self.api_used = "guest"
            print(self.username)
            self.profile = guest.profile(self.username)
            if self.profile is None:
                raise ConnectionError("Got temporary block")
    
            del guest
            self.bio = await self.profile.biography
            self.bio_links = await self.profile.biography_links
            self.email = extract_emails(self.profile.biography)
            if self.email== []:
                if self.profile.biography_links != []:
                    for link in self.profile.biography_links:
                        self.email = extract_emails(link['url'])
                        if self.email!=[]:
                            # out of the loop
                            break
            return True
        except Exception as e:
            print(f"skipping userid {self.username}")
            return False
    async def insta_aiograpi(self):
        try:
            self.api_used = "mobile"
            self.profile = (await self.cl.user_info_by_username(self.username)).model_dump()
            print("here1")
            print( self.profile['biography'])
            print( self.profile['bio_links'])
            print(self.profile)
            if self.profile['public_email'] is None:
                self.bio = self.profile['biography']
                self.bio_links = self.profile['bio_links']
                self.email = extract_emails(self.bio)
            
                if not self.email:
                    for link in self.bio_links:
                        self.email = extract_emails(link['url'])
                        if self.email:
                            break
            else:
                self.bio = self.profile['biography']  # ✅ always set this
                self.bio_links = self.profile['bio_links']
                self.email = extract_emails(self.profile['public_email'])
        except Exception as e:
            print(f"skipping userid {self.username}")
            return False

    async def db_handler(self):
        try:
            assert hasattr(self, "bio"), f"{self.username} is missing 'bio'"
            assert hasattr(self, "bio_links"), f"{self.username} is missing 'bio_links'"
            assert hasattr(self, "email"), f"{self.username} is missing 'email'"
    
            async with ExtendedUser(
                username = self.username,
                fullname = self.fullname,
                isprivate = self.isprivate,
                profile_pic_url = self.profile_pic_url,
                is_business_account = self.is_business_account, 
                is_professional_account = self.is_professional_account,
                account_type = self.account_type,
                bio = self.bio,
                bio_links = self.bio_links,
                email = self.email,
                search_id = self.search_ids,
                action_button = [],
                api_used = self.api_used
            ) as eu:
                print(f"Saving user: {self.username}")
                await eu.save()
                print('done')
                return True
        except Exception as e:
            print(f"[db_handler error] {e}")
            print(e)
            return False
    
    async def random_webdriver(self):
        '''
        No idea how to divide the task at present keeping random
        but for best result these can't have email action button
        is_private: false
        is_professional_account: false
        is_business_account: false
        account_type: 1
        or 
        is_private: true
        is_professional_account: true
        is_business_account: true or false
        account_type: 2 or 3
        or 
        is_private: false
        is_professional_account: true
        is_business_account: true or false
        account_type: 2 or 3
        public_email: ""
        '''
        try:
            # at present guest api is not working
            selection = 2#random.randrange(1,3)
            if selection == 1:
                await self.insta_guest_api()
                pass
            elif selection == 2:
                await self.insta_aiograpi()
                pass
            print(f"user: {self.username}")
            print(f"{self.bio}")
            print(f"{self.bio_links}")
            print("success")
        except Exception as e:
            print(e)

import aiograpi   
class Driver:
    async def main():
        # client is for aiogrpi
        # get a usier list 
        try:
            print("user Scanner is active")
            await asyncio.sleep(10)
            client = aiograpi.Client()
            await client.login(username="thecreators782", password="TheCreators12345")
            while (True):
                users = await User.find_by_scanned_status(scanned=False)
                if users == []:
                    print("user scanner going to sleep for 30 sec")
                    await asyncio.sleep(30)
                
                
                for usr in users:
                    content = usr.to_dict()
                    classObj = Insta_user_profile(content,client)
                    await classObj.random_webdriver()
                    completed = await classObj.db_handler()
                    if completed:
                        await usr.update(scanned=True)
                    await asyncio.sleep(random.randrange(30,60))
        except Exception as e:
            print(e)
            
if __name__ == "__main__":
    asyncio.run(Driver.main())