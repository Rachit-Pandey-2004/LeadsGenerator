# need to find work around scroll
#  the scroll still not have any fix and works on fixed 10 scrolls
# need to implement swap insta id's dynamically to save the state of scroll or improving hooking and do mitm attack
'''
with the trigger for hash search after a waiting period or a variable switch we will initiate forget and fire for user scrapping
'''
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
import math
from playwright.async_api import Page, Response
from extensions import watchList
import traceback
from .UserScarapper import Driver
class Hash:
    def __init__(self, page: Page, session_id,tag: str, limit:int):
        self.limit = math.ceil(limit/18) # 18 is items per scroll ~ removing infinite scroll support for safety ( temporary )
        self.page = page
        self.session_id=session_id
        self.tag = tag
        self.next_max_id = None
        self.last_max_id= None
        # getting a race condition I don't know but page is closing ~ fixed
    async def hook(self, res: Response):
        try:
            if res.request.frame.page.is_closed():
                return
            if res.url.startswith("https://www.instagram.com/api/v1/fbsearch/web/top_serp/?enable_metadata=true&query=%23"):
                data = await res.json()
                # this should be done first for 
                self.next_max_id = data["media_grid"]["next_max_id"]
                print(f"Hook received next_max_id: {self.next_max_id}")
                asyncio.create_task(watchList.search_entries(data,self.session_id))
                
                # for rest do forget and fire operations
                
        except Exception as e:
            print(f"Error in hook: {e}")
            traceback.print_exc()
    
    async def __scrollTags(self):
        try:
            while((self.next_max_id is not None and self.next_max_id!=self.last_max_id and self.limit > 1)):
                await asyncio.sleep(500)
                self.last_max_id= self.next_max_id
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print("Scrolling page...")
                # wait for target API RESPONSE TO LOAD
                # await self.page.expect_response(lambda response : response.url.startswith("https://www.instagram.com/api/v1/fbsearch/web/top_serp/") )
                await self.page.wait_for_function(
                    """() => {
                        return window.performance.getEntries().some(entry =>
                            entry.name.includes("https://www.instagram.com/api/v1/fbsearch/web/top_serp/?enable_metadata=true&query=%23")
                        );
                    }"""
                )
                print(f"last maxid >>{self.last_max_id}\nnext maxid {self.next_max_id}")
                await asyncio.sleep(4)
                await asyncio.sleep(random.gammavariate(2.05678,2.032))
                self.limit = self.limit - 1 # decrasing by scrolls
                
        except Exception as e:
            print(f"Error during scrolling: {e}")
            traceback.print_exc()

    async def search(self):
        try:
            # here implement the user searching task
            task = asyncio.create_task(Driver.main())
            # this is only for hooking the data
            self.page.on("response", self.hook)
            # Navigate to the hashtag search page
            await self.page.goto(f"https://www.instagram.com/explore/search/keyword/?q=%23{self.tag}")
            print(f"🔍 Searching posts by hashtag: {self.tag}")
            # await self.page.expect_response(lambda response : response.url.startswith("https://www.instagram.com/api/v1/fbsearch/web/top_serp/") )
            await self.page.wait_for_function(
                """() => {
                    return window.performance.getEntries().some(entry =>
                        entry.name.includes("https://www.instagram.com/api/v1/fbsearch/web/top_serp/?enable_metadata=true&query=%23")
                    );
                }"""
            )
            await asyncio.sleep(random.gammavariate(2.05678,2.032))
            await self.__scrollTags()    
        except Exception as e:
            print(f"Error in search: {e}")
            traceback.print_exc()
        finally:
            self.page.remove_listener("response", self.hook)
            await task