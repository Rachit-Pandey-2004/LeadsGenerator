# clone of interface for proper setup
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import asyncio
from scripts import auth
from scripts import hashSearch
from scripts import Driver

USERNAME = "thecreators782"
PASSWORD = "TheCreators12345"
class InstaDriver:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
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
        await stealth_async(self.page)
        return self  # Returning the instance for context management

    async def __aexit__(self, exc_type, exc_value, traceback):
        
        await self.browser.close()
        await self.playwright.stop()

    async def begin(self):
        print("Initiating the client...")
        AuthClass = auth.Authenticate 
        AuthInstance = auth.Authenticate(USERNAME, PASSWORD, self.page,self.context)
        await AuthInstance.get_session() 
        print("scrapping session")
        await Driver.main(self.page)

    async def search_by_hashtag(self, hashtag):
        """
        Search posts by hashtag
        https://www.instagram.com/explore/search/keyword/?q=%23fashion
        # = %23 encoding
        scroll and hook endpoint
        https://www.instagram.com/api/v1/fbsearch/web/top_serp/?enable_metadata=true&query=%23fashion
        """
        HashClass = hashSearch.Hash
        HashInstance = hashSearch.Hash(self.page, hashtag)
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