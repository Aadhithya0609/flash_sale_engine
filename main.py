import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Product, Order
import redis

app = FastAPI()

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/buy/naive/{product_id}")
async def buy_product_naive(product_id: int, db: AsyncSession = Depends(get_db)):
    # 1. READ the inventory from the database
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. CHECK if stock is available
    if product.inventory > 0:
        
        # ⚠️ SIMULATE LATENCY (The "Thinking Time" that causes bugs)
        # This represents payment gateway processing or network lag.
        await asyncio.sleep(0.1) 

        # 3. UPDATE the inventory
        product.inventory -= 1
        
        # 4. CREATE the order
        new_order = Order(product_id=product_id)
        db.add(new_order)
        
        # 5. COMMIT (Save to DB)
        await db.commit()
        return {"message": "Purchase successful", "remaining_stock": product.inventory}
    
    else:
        return {"message": "Sold Out!"}

@app.get("/inventory/{product_id}")
async def check_inventory(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    return {"id": product.id, "name": product.name, "inventory": product.inventory}


# ... existing imports ...
from services import redis_lock  # Import the lock we just wrote
# ... keep your imports ...
from services import redis_lock 

@app.post("/buy/smart/{product_id}")
async def buy_product_smart(product_id: int, db: AsyncSession = Depends(get_db)):
    
    try:
        # ⚠️ CHANGED: Added 'async' before 'with'
        async with redis_lock(f"lock:product:{product_id}"):
            
            # 1. READ
            result = await db.execute(select(Product).where(Product.id == product_id))
            product = result.scalars().first()

            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # 2. CHECK
            if product.inventory > 0:
                # 3. UPDATE
                product.inventory -= 1
                new_order = Order(product_id=product_id)
                db.add(new_order)
                
                # 4. COMMIT
                await db.commit()
                return {"message": "Purchase successful", "remaining_stock": product.inventory}
            
            else:
                return {"message": "Sold Out!"}
                
    except Exception as e:
        # If lock fails or other errors
        raise HTTPException(status_code=503, detail=str(e))