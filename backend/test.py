import asyncio
import json
import websockets


async def consumer_handler(websocket, path):
    async for message in websocket:
        print(path, message)


async def test(uri):
    async with websockets.connect(uri) as websocket1, websockets.connect(uri) as websocket2:
        asyncio.ensure_future(consumer_handler(websocket1, 1))
        asyncio.ensure_future(consumer_handler(websocket2, 2))

        await websocket1.send(json.dumps({'action': 'logon', 'room': 'test3', 'name': 'brick'}))
        await websocket2.send(json.dumps({'action': 'logon', 'room': 'test3', 'name': 'other_brick'}))
        await asyncio.sleep(1)
        await websocket1.send(json.dumps({'action': 'roll', 'request': '1d20'}))
        await websocket2.send(json.dumps({'action': 'roll', 'request': '1d20+3'}))
        await websocket2.send(json.dumps({'action': 'roll', 'request': '2d6+1'}))
        await asyncio.sleep(3)
        await websocket1.close()
        await asyncio.sleep(3)
        await websocket2.send(json.dumps({'action': 'logon', 'room': 'test3', 'name': 'change_name'}))
        await asyncio.sleep(3)
        await websocket2.close()


asyncio.get_event_loop().run_until_complete(test('ws://localhost:8765'))
