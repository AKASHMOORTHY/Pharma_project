from app.database import SessionLocal
from app import models

db = SessionLocal()

user3 = models.User(email="admin@mail.com", full_name="admin", phone="+919841992192")
# user2 = models.User(email="manager@mail.com", full_name="Manager")


db.add_all([user3])
db.commit()

print("Users added successfully.")
db.close()
