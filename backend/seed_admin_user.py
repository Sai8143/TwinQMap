import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import MongoDBManager
from backend.repositories.user import UserRepository
from backend.services.user import UserService
from backend.schemas.user import UserCreate

async def seed_admin():
    print("Connecting to MongoDB Atlas...")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()
    
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    admin_user = await user_repo.get_by_username("admin")
    if admin_user:
        print("[SUCCESS] Admin user already exists in MongoDB Atlas database!")
    else:
        print("Creating admin user (admin / admin123)...")
        new_admin = UserCreate(
            username="admin",
            email="admin@twinq.io",
            password="admin123",
            full_name="System Administrator",
            role="admin"
        )
        created = await user_service.register_user(new_admin)
        print("[SUCCESS] Admin user created successfully:", created.username)
        
    await MongoDBManager.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_admin())
