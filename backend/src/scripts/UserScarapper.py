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
import asyncio
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import ExtendedUser
from db import User
from db import InstagramAccountManager

from ensta import Guest

from aiograpi import Client
from aiograpi.exceptions import (
    LoginRequired, 
    AccountSuspended, 
    AboutUsError,
    ChallengeRequired,
    ChallengeError,
    CheckpointRequired,
    ConsentRequired,
    GeoBlockRequired
) 

logger =logging.getLogger()

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


class Driver:
    async def main(session_id):
        # session_id will help to keep the track of the given task id scans
        # client is for aiogrpi
        # get a usier list 
        '''
        we need to set the session management also in this script
        '''
        try:
            manager = InstagramAccountManager()
            account = await manager.get_available_account(scraper_id="scraper2")
            
            print("user Scanner is active")
            await asyncio.sleep(10)
            client = Client()
            client.delay_range = [1, 3]
            insta_session = client.load_settings(account['sessionDir'])
            # just some plags
            login_via_session = False
            login_via_pw = False

            if insta_session:
                try:
                    client.set_settings(insta_session)
                    await client.login(
                        username = account['username'],
                        password = account['password']
                        )
                    # now check if the session is valid or not
                    try:
                        await client.get_timeline_feed()
                    except LoginRequired:
                        logger.info("Session is invalid. need to login via credentials")
                        old_insta_session  = client.get_settings()
                        client.set_settings({})
                        client.set_uuids(old_insta_session["uuids"])
                        await client.login(
                            username = account['username'],
                            password = account['password']
                        )
                    except (ChallengeRequired, CheckpointRequired, ChallengeError):
                        await manager.update_banstatus(account['username'], "challenge")
                        logger.warning("Challenge flow triggered.")
                        raise
                    except (ConsentRequired, GeoBlockRequired):
                        await manager.update_banstatus(account['username'], "restricted")
                        logger.warning("Geo/Consent restriction triggered.")
                        raise
                    except AccountSuspended:
                        await manager.update_banstatus(account['username'], "suspended")
                        raise
                    except AboutUsError:
                        await manager.update_banstatus(account['username'], "blocked")
                        raise
                    finally:
                        login_via_session = True
                except Exception as e:
                    logger.info("Couldn't login user using the session info: %s"%account['username'])
                    print(e)
            if not login_via_session:
                try:
                    logger.info("Attempting to login via username and password.")
                    if await client.login(username = account['username'], password = account['password']):
                        login_via_pw = True
                except Exception as e : 
                    logger.info("Couldn't login user using username and password")
                except (ChallengeRequired, CheckpointRequired, ChallengeError):
                    await manager.update_banstatus(account['username'], "challenge")
                    logger.warning("Challenge flow triggered.")
                    raise
                except (ConsentRequired, GeoBlockRequired):
                    await manager.update_banstatus(account['username'], "restricted")
                    logger.warning("Geo/Consent restriction triggered.")
                    raise
                except AccountSuspended:
                    await manager.update_banstatus(account['username'], "suspended")
                    raise
                except AboutUsError:
                    await manager.update_banstatus(account['username'], "blocked")
                    raise
            if not login_via_pw and not login_via_session : 
                raise Exception("Couldn't login user with either password or session")
            
            while (True):
                users = await User.find_by_scanned_status(scanned=False,search_id = session_id)
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
        except Exception as e:
            print(e)
        finally:
            await manager.set_cooldown(account['username'])
            
if __name__ == "__main__":
    asyncio.run(Driver.main())