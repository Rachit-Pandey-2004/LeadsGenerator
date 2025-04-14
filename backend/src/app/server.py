from aiohttp import web
from routes import setup_routes
from cors import setup_cors

def create_app():
    app = web.Application()
    setup_routes(app)
    setup_cors(app)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), port=8080)