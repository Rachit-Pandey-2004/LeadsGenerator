from aiohttp import web
import aiohttp_cors
import json
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Allowed request types
ALLOWED_REQ_TYPES = {
    "Hashtags",
    "Followers",
    "Following",
    "Comments",
    "Location",
    "Post Likes",
}

@routes.post("/api/process")
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

        # Extract and validate fields
        req_type = data.get("req_type")
        query = data.get("query")
        limit = data.get("limit")

        # Basic field validation
        missing_fields = [key for key in ( "req_type", "query", "limit") if data.get(key) is None]
        if missing_fields:
            return web.json_response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        # Check for allowed request type
        if req_type not in ALLOWED_REQ_TYPES:
            return web.json_response({
                "error": f"Invalid req_type '{req_type}'. Allowed types are: {', '.join(ALLOWED_REQ_TYPES)}"
            }, status=400)

        # Optionally validate limit as integer
        try:
            limit = int(limit)
            if limit < -1 and limit != 0:
                raise ValueError
        except (ValueError, TypeError):
            return web.json_response({"error": "limit is not set properly"}, status=400)

        # processing logic here (possibly async scraping, queueing, etc.)
        # For now, just return a success response
        #  we will get unique id from history mongo
        result = {
            "message": f"Search request of type '{req_type}' initiated.",
            "status": "success"
        }

        return web.json_response(result, status=200)

    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.exception("Unhandled exception occurred:")
        return web.json_response({"error": str(e)}, status=500)

def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)

    # Setup default CORS settings
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # Apply CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)

    return app

if __name__ == "__main__":
    web.run_app(create_app(), port=8080)