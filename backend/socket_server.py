import asyncio
import json
import websockets

from backend.dice_exception import DiceException
from backend.dice_parser import GenericDiceParser as DiceParser
from backend.room_data import RoomData

server_port = 8765
message_dispatch_interval = .01

parser = DiceParser()


class DiceServer:
    def __init__(self):
        self.connections = set()

    def serve(self):
        start_server = websockets.serve(self._socket_connect, "0.0.0.0", server_port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def _socket_connect(self, websocket: websockets.WebSocketServerProtocol, path: str):
        ds = DiceSocket(websocket, path)
        self.connections.add(ds)
        await ds.serve()
        self.connections.remove(ds)
        ds.cleanup()


class DiceSocket:
    def __init__(self, websocket, path):
        self.websocket = websocket
        self.data = RoomData()

    def cleanup(self):
        self.data.member_leave_room()

    async def serve(self):
        try:
            async for req in self.websocket:
                resp = None
                try:
                    jreq = json.loads(req)
                    action = jreq['action']
                    resp = getattr(self, f"_do_{action}")(jreq)
                except DiceException as de:
                    resp = {'action': 'error', 'error': de.message}
                except:
                    resp = {'action': 'error', 'error': f"Failed to handle request: \"{req}\""}
                    raise
                finally:
                    if resp:
                        jresp = json.dumps(resp)
                        await self.websocket.send(jresp)
        except Exception as e:
            print(e)

    async def heartbeat(self):
        # todo self checks as called by server
        return True

    def _do_logon(self, req):
        result = self.data.member_enter_room(req['room'], req['name'])

        async def get_messages():
            while self.data.pubsub:
                message = self.data.pubsub.get_message()
                if message:
                    output = json.dumps({'action': 'append', 'message': message['data'].decode('utf-8')})
                    await self.websocket.send(output)
                await asyncio.sleep(message_dispatch_interval)
        asyncio.create_task(get_messages())

        return {'action': 'logon', **result}

    def _do_logoff(self, req):
        self.data.member_leave_room()

    def _do_roll(self, req):
        result = f"[{self.data.name}] {DiceParser.parse(req['dice'], req['purpose'])}"
        self.data.write_room_log(result)

    def _do_create_macro(self, req):
        self.data.write_macro({'dice': req['dice'], 'purpose': req['purpose']})

    def _do_delete_macro(self, req):
        self.data.delete_macro({'dice': req['dice'], 'purpose': req['purpose']})
