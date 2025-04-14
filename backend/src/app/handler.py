import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from aiohttp import web
from db import History
from db import ExtendedUser
import json
import logging
from typing import Any, Dict
from config import ALLOWED_REQ_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_InstaManager(request : web.Request) -> web.Response:
    '''
    query supported :
    save ~ save the account after verifing that account credentials are correct
    load ~ load all acoount status from db 
    delete ~ remove the account from the db
    '''
    try:
        if request.content_type != "application/json":
            return web.json_response({"error": "Content-Type must be application/json"}, status=415)

        data: Dict[str, Any] = await request.json()
        query = data.get("query")
        if query == 'save':
            user_name = data.get("username")
            password = data.get("password")
            assign = data.get("assign")
            # assign 1 means webdriver scrapper and assign 2 is aiograpi
            if ((not user_name or not isinstance(user_name, str)) or (not password or not isinstance(password, str)) or (not assign or not isinstance(assign, int))):
                return web.json_response({"error": "None data received !!"}, status= 404)
            # first login and save the user and then transfer the data to db with session location
            if(assign == 1):
                
            #  now implement db from here 
            
    except Exception as e:
        print(e)


# there three type of request possible if query have
# listing ~ the give history table with their status code
# preview ~ it give live data 
# file ~ it will open a stream to give the file 
async def handle_history(request: web.Request)->web.Response:
    try:
        if request.content_type != "application/json":
            return web.json_response({"error": "Content-Type must be application/json"}, status=415)

        data: Dict[str, Any] = await request.json()
        query = data.get("query")

        if query == "listing":
            records = await History.find_all_as_dicts()
            return web.json_response({"data": records}, status=200)
        elif query == "reset":
            '''This is for resetting the failed task to queue'''
            id = data.get("id")
            if not data or not isinstance(id, str):
               return web.json_response({"error": "no id received"}, status=415)
            # find and update
            found_content = await History.find_by_id(search_id = id)
            if found_content:
                status = await found_content.update(status="pending")
                if not status:
                    return web.json_response({"error": "failed"}, status=402)
                return web.json_response({"msg": "done"}, status=200)
            return web.json_response({"error": "can't process"}, status=422)

        elif query == "preview":
            id = data.get("id")
            if not data or not isinstance(id, str):
                return web.json_response({"error": "no id received"}, status=415)
            records = await ExtendedUser.preview_by_search_id(id)
            return web.json_response({"data": records}, status=200)
        else:
            # at present no plans for file download streaming
            return web.json_response({"error": "U r not allowed"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_post(request: web.Request) -> web.Response:
    try:
        '''
        here we will make a queue in mongodb on three status code ( queued, in process, completed)
        '''
        # Ensure content type is application/json
        if request.content_type != "application/json":
            return web.json_response({"error": "Content-Type must be application/json"}, status=415)

        # Parse JSON data
        data: Dict[str, Any] = await request.json()
        logger.info("Received data: %s", json.dumps(data, indent=2))

        # # Basic field validation
        # missing_fields = [key for key in ( "req_type", "query", "limit") if data.get(key) is None]
        missing_fields = [key for key in ( "req_type", "query", "limit") if key not in data]
        if missing_fields:
            return web.json_response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)
        null_data = [key for key in ("req_type", "query", "limit") if data.get(key) is None]
        if null_data:
            return web.json_response({"error": f"Null fields: {', '.join(null_data)}"}, status=400)
        
        req_type = data.get("req_type")
        query = data.get("query")
        limit = data.get("limit")
        
        # Check if `query` is a list with only empty or whitespace strings
        query = data["query"]
        if not isinstance(query, list) or all(str(q).strip() == "" for q in query):
            return web.json_response({"error": "Query list is empty or contains only empty strings"}, status=400)


        # Check for allowed request type
        if req_type not in ALLOWED_REQ_TYPES:
            return web.json_response({
                "error": f"Invalid req_type '{req_type}'. Allowed types are: {', '.join(ALLOWED_REQ_TYPES)}"
            }, status=400)

        # Optionally validate limit as integer
        try:
            limit = int(limit)
            if limit > -1 and limit == 0:
                raise ValueError
        except (ValueError, TypeError):
            return web.json_response({"error": "limit is not set properly"}, status=400)
        # processing logic here (possibly async scraping, queueing, etc.)
        # For now, just return a success response
        #  we will get unique id from history mongo
        mongoDb = History(
            status="pending",
            query= query,
            query_type= req_type,
            limit = limit
        )
        id = await mongoDb.save()
        result = {
            "message": f"Search request of type '{req_type}' initiated.",
            "status": "success",
            "id" : str(id)
        }
        
        return web.json_response(result, status=200)

    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.exception("Unhandled exception occurred:")
        return web.json_response({"error": str(e)}, status=500)