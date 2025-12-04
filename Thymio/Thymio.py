from tdmclient import ClientAsync

async def main():
    
    async with ClientAsync() as client:
        node = await client.wait_for_node()
        
        # Send event to robot
        await node.send_event("forwards")
        
        # Poll for 'performed'
        while True:
            events = node.events.get("performed")
            if events:
                print("Callback: move completed.")
                break

import asyncio

asyncio.run(main())
