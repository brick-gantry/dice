import asyncio
import json
import time
import redis
import websockets

from backend.dice_parser import GenericDiceParser as DiceParser

cache = redis.Redis(host='localhost', port=6379, db=0)

parser = DiceParser()


class DiceServer:
    def __init__(self):
        self.connections = set()

    def serve(self):
        start_server = websockets.serve(self._socket_connect, "localhost", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def _socket_connect(self, websocket: websockets.WebSocketServerProtocol, path: str):
        ds = DiceSocket(websocket)
        self.connections.add(ds)
        await ds.serve()
        self.connections.remove(ds)
        ds.cleanup()


class DiceSocket:
    def __init__(self, websocket):
        self.websocket = websocket
        self.room = None
        self.name = None
        self.pubsub = None

    def cleanup(self):
        if self.room and self.name:
            cache.srem(f"{self.room}-members", self.name)
            cache.publish(f"{self.room}-announce", f"{self.name} leaves {self.room}")

    async def serve(self):
        try:
            async for req in self.websocket:
                try:
                    jreq = json.loads(req)
                    action = jreq['action']
                    action_map = {'logon': self._do_logon,
                                  'logoff': self._do_logoff,
                                  'roll': self._do_roll}
                    resp = action_map[action](jreq)
                    jresp = json.dumps(resp)
                    await self.websocket.send(jresp)
                except:
                    await self.websocket.send(f"Failed to handle request: {req}")
        except Exception as e:
            print(e)

    def heartbeat(self):
        # todo self checks as called by server
        return True

    def _do_logon(self, req):
        self.room = req['room']
        self.name = req['name']
        self.pubsub = cache.pubsub()

        async def handler(message):
            await self.websocket.send(message['data'])
        self.pubsub.subscribe(**{f"{self.room}-*": handler})

        cache.publish(f"{self.room}-announce", f"{self.name} enters {self.room}")
        cache.sadd(f"{self.room}-members", self.name)
        current_members = [m.decode('utf-8') for m in cache.smembers(f"{self.room}-members")]
        history = [h.decode('utf-8') for h in self._get_room_history()]

        return {'action': 'logon', 'current_members': current_members, 'history': history}

    def _get_room_history(self):
        keys = cache.keys(f"*:{self.room}")
        keys.sort()
        return cache.mget(keys)

    def _do_logoff(self, req):
        self.room = None
        self.name = None
        cache.srem(f"{self.room}-members", self.name)
        cache.publish(f"{self.room}-announce", f"{self.name} leaves {self.room}")
        self.pubsub.close()
        self.pubsub = None
        pass

    def _do_roll(self, req):
        cache_key = f"{time.time()}:{self.room}"
        result = f"[{self.name}] {parser.parse(req['request'])}"
        cache.set(cache_key, result, 60*60)  # keep history for one hour
        return result