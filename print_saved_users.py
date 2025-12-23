from app.database import SessionLocal
from app import models

db = SessionLocal()
users = db.query(models.User).all()
for u in users:
    print(u.id, u.username, u.hashed_password, u.salt)
db.close()