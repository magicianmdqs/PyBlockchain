import asyncio
import websockets
from websockets.protocol import State

connected = set()

async def handler(ws, path=None):
    print(f"New client: {ws.remote_address}")
    connected.add(ws)
    try:
        async for msg in ws:
            print(f"Received: {msg} from {ws.remote_address}")
            for client in connected:
                if client != ws and client.state == State.OPEN:
                    await client.send(msg)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {ws.remote_address}")
    finally:
        connected.remove(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8080):
        print("Server running on wss://0.0.0.0:8080")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
