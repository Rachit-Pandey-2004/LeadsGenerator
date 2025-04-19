import json
from aiohttp import web, WSMsgType
from typing import Dict, Any
from interface import InstaDriver
from db import InstagramAccountManager
# first verify if user exist if not then go further
async def handle_InstaManager_ws(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket connection for InstaManager established")
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data: Dict[str, Any] = json.loads(msg.data)
                    query = data.get("query")
    
                    if query == 'save':
                        data = data.get("data")
                        username = data.get("username")
                        password = data.get("password")
                        scraper = data.get("scraper")
                        print(username, password, scraper)
                        if not all([username, password, scraper]):
                            await ws.send_json({"query": "save",
                                    "status": "error",
                                    "msg": "Missing fields"})
                            continue
    
                        await ws.send_json({"query": "save",
                                    "status": "process","msg": "Trying to log in..."})
                        # check if id is alredy logged into some session
    
                        if scraper == "scraper1":
                            try:
                                async with InstaDriver(username=username, password=password, headless=True) as driver:
                                    status = await driver.begin(f"src/sessions/session_{username}_{scraper}.json")
                                    if not status:
                                        await ws.send_json({"query": "save",
                                    "status": "error","msg": "Failed to login with scraper1"})
                                        continue
                            except Exception as e:
                                await ws.send_json({"query": "save",
                                    "status": "error","msg": f"scraper1 login failed: {str(e)}"})
                                continue
    
                        elif scraper == "scraper2":
                            try:
                                from aiograpi import Client
                                client = Client()
                                status = await client.login(username, password)
                                await client.dump_settings(f"src/sessions/session_{username}_{scraper}.json")
                                if not status:
                                    await ws.send_json({"query": "save",
                                    "status": "error","msg": "Failed to login with scraper2"})
                                    continue
                            except Exception as e:
                                await ws.send_json({"query": "save",
                                    "status": "error","msg": f"scraper2 login failed: {str(e)}"})
                                continue
                        else:
                            await ws.send_json({"query": "save",
                                    "status": "error","msg": "Unknown assign type"})
                            continue
    
                        await ws.send_json({"query": "save",
                                    "status": "process","msg": "Saving account to DB..."})
    
                        result = await InstagramAccountManager().insert_account(
                            username=username,
                            password=password,
                            assigned=scraper,
                            session_path=f"src/sessions/session_{username}_{scraper}.json"
                        )
    
                        if not result:
                            await ws.send_json({"query": "save",
                                    "status": "error","msg": "Failed to insert into DB"})
                            continue
    
                        await ws.send_json({"query": "save",
                                    "status": "success","msg": "Account saved successfully"})
    
                    elif query == 'load':
                        # You can implement your own loader logic here
                        try : 
                            await InstagramAccountManager().reset_expired_cooldowns()
                            accounts = await InstagramAccountManager().load_all_accounts()
                            await ws.send_json(
                                {
                                    "query": "load",
                                    "status": "success",
                                    "response": {
                                        "accounts": accounts
                                    }
                                }
                                    )
                        except Exception as e:
                            await ws.send_json({
                                "query" : "loads",
                                "status" : "internal_error",
                                "msg" : "internal server error"
                            })
    
                    elif query == 'delete':
                        username = data.get("username")
                        if not username:
                            await ws.send_json({"error": "Missing username to delete"})
                            continue
                        result = await InstagramAccountManager().delete_account(username)
                        if result:
                            await ws.send_json({"msg": f"Deleted {username} successfully"})
                        else:
                            await ws.send_json({"error": f"Could not delete {username}"})
                    else:
                        await ws.send_json({"error": "Unknown query type"})
    
                except Exception as e:
                    await ws.send_json({"error": f"Exception occurred: {str(e)}"})
    
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
    
    except Exception as e:
        print(f"[ERROR] WebSocket exception: {str(e)}")

    finally:
        print("Cleaning up WebSocket connection")
        await ws.close()

    print("WebSocket closed for InstaManager")
    return ws