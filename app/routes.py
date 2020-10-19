from app import app, db

@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
