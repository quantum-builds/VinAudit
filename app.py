import os
from flask import Flask, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
from urllib.parse import quote_plus  # <-- added

from models import db
from routes import init_routes

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Escape password and optional user if needed
    db_user = quote_plus(os.getenv("DB_USER"))
    db_password = quote_plus(os.getenv("DB_PASSWORD"))
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3307")
    db_name = os.getenv("DB_NAME")

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize routes
    init_routes(app)

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', error=error), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

