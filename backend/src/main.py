'''
Let's make the implementation simple and cyclic
'''
import sys
import os
import asyncio
from app import create_app
from aiohttp import web
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface import InstaDriver
from db import History

class Cyclic:
    def __init__(self) -> None:
        pass

    async def find_task(self):
        try: 
            task_list = await History.find_by_status("pending")
            if not task_list:
                print("No pending tasks.")
                return

            for task in task_list:
                await task.update(status="in_progress")
                
                try:
                    async with InstaDriver(session_id=task._id) as driver:
                        status = await driver.begin()
                        limit = task.limit
                        if task.query_type.lower() == 'hashtags':
                            for query in task.query:
                                # 
                                await driver.search_by_hashtag(query.replace('#', ''), limit)

                    # await task.update(status="completed")

                except Exception as task_error:
                    print(f"Task failed: {task._id} -> {task_error}")
                    await task.update(status="failed")

        except Exception as e:
            print(f"General error in find_task(): {e}")
async def server():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    print("Server started at http://localhost:8080")
async def main():
    asyncio.create_task(server())
    while(True):
       await Cyclic().find_task()
       await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(main())