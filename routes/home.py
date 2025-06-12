from flask import Flask
from controllers import HomeController

def init_home_routes(app: Flask) -> None:
    """
    Initialize home-related routes.
    
    Args:
        app: Flask application instance
    """
    home_controller = HomeController()
    
    app.add_url_rule("/", view_func=home_controller.index)
    app.add_url_rule("/search", view_func=home_controller.search)
    app.add_url_rule("/results", methods=["POST"], view_func=home_controller.results) 