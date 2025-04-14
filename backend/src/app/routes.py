from aiohttp import web
from handler import handle_post, handle_history, handle_InstaManager

def setup_routes(app: web.Application):
    app.router.add_post("/api/process", handle_post)
    app.router.add_post("/api/history",handle_history)
    app.router.add_post("/api/manager",handle_InstaManager)
    