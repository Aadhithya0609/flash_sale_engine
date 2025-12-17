import asyncio
from database import engine, Base, AsyncSessionLocal
from models import Product

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.drop_all) # Reset DB each time we run this
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables Created")

    async with AsyncSessionLocal() as session:
        # Add a product with 100 inventory
        iphone = Product(name="iPhone 15", inventory=100)
        session.add(iphone)
        await session.commit()
        print("✅ Added 'iPhone 15' with 100 stock")

if __name__ == "__main__":
    asyncio.run(init_db())