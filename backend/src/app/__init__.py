from .config import ALLOWED_REQ_TYPES
from .cors import setup_cors
from .handler import handle_post
from .handler import handle_history
from .handler import handle_InstaManager
from .routes import setup_routes
from .handler_ws import handle_InstaManager_ws
from .server import create_app