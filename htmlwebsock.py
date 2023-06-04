import asyncio
import websockets

# Waiting websocket to accept HTML websocket kicks on localhost CRAB webpage
async def hello(websocket):
    name = await websocket.recv()
    print(f"await discord.Guild.kick(self= await client.fetch_guild(int(Preferences['GuildID'])),user={name})")

async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
