import asyncio
import json
import websockets


async def hello(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'action': 'logon', 'room': 'test2', 'name': 'brick'}))
        print(await websocket.recv())
        await websocket.send(json.dumps({'action': 'roll', 'request': '1d20'}))
        print(await websocket.recv())

asyncio.get_event_loop().run_until_complete(hello('ws://localhost:8765'))