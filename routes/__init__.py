from flask import Flask
from .home import init_home_routes

def init_routes(app: Flask) -> None:
    """
    Initialize all application routes.
    
    Args:
        app: Flask application instance
    """
    init_home_routes(app) 