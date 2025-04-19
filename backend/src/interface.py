from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import asyncio
from scripts import auth
from scripts import hashSearch
from scripts import Driver
from aiograpi import Client
from db import InstagramAccountManager


class InstaDriver:
    
    def __init__(self, session_id=None, username:str = None, password:str = None,headless = False ):
        self.session_id = session_id
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless=headless
        self.USERNAME = username
        self.PASSWORD = password
        self.cl = Client()
    async def __aenter__(self):
        '''
        make the selection of the id and mark it as in use
        '''
        self.manager = InstagramAccountManager()
        self.account = await self.manager.get_available_account(scraper_id="scraper1")
        # and release the lock i exit 
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless = self.headless)
        self.context = await self.browser.new_context(
            timezone_id="Asia/Kolkata",
            locale="en-US",
            viewport={"width": 1280, "height": 800},
            geolocation={"longitude": 45.070950, "latitude": 7.711453},
            permissions=["geolocation"],
            extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9"
        }
        )
        self.page = await self.context.new_page()
        # await self.cl.login(InstaDriver.USERNAME, InstaDriver.PASSWORD)
        await stealth_async(self.page)
        return self  # Returning the instance for context management

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.manager.set_cooldown(self.account['username'])
        await self.browser.close()
        await self.playwright.stop()

    async def begin(self):
        print("Initiating the client...")
        AuthClass = auth.Authenticate 
        AuthInstance = auth.Authenticate(self.account['username'], self.account['password'], self.page,self.context)
        AuthInstance.STATE_FILE = self.account['sessionDir']
        status = await AuthInstance.get_session() 
        print("auth completed")
        return status

    async def search_by_hashtag(self, hashtag,limit):
        """
        Search posts by hashtag
        https://www.instagram.com/explore/search/keyword/?q=%23fashion
        # = %23 encoding
        scroll and hook endpoint
        https://www.instagram.com/api/v1/fbsearch/web/top_serp/?enable_metadata=true&query=%23fashion
        """
        HashClass = hashSearch.Hash
        HashInstance = hashSearch.Hash(self.page, self.session_id,hashtag,limit=limit)
        await HashInstance.search()

    async def search_by_suggested(self):
        """Search by suggested users"""
        pass

    async def search_by_following(self):
        """Search by people you follow"""
        pass

    async def search_by_followers(self):
        """Search by followers"""
        pass

    async def search_by_location(self, location):
        """Search posts by location"""
        print(f"📍 Searching posts by location: {location}")
        await self.page.goto(f"https://www.instagram.com/explore/locations/{location}/")
        await asyncio.sleep(2)  # Wait for page to load

    async def search_by_music_of_post(self):
        """Search posts by music"""
        pass

async def main():
    async with InstaDriver() as insta:
        await insta.begin()
        # await insta.search_by_hashtag("influencerlife")
        # await insta.search_by_location("chicago")

if __name__ == "__main__":
    asyncio.run(main())