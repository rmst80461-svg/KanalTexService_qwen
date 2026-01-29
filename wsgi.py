"""WSGI entry point for production deployment"""
from app.models.database import Database
from app.web.routes import create_app

db = Database()
db.init_db()

app = create_app(db, None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
