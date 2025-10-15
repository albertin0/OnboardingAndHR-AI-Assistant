from app.db import init_db, get_session
from app.models import User
from app.auth import hash_password

init_db()
session = get_session()
admin = User(
    full_name="Admin User",
    phone="0000000000",
    email="admin@example.com",
    hashed_password=hash_password("AdPass123"),
    is_admin=True,
    is_validated=True
)
session.add(admin)
session.commit()
session.close()
print("Admin created: admin@example.com / AdminPass123!")
