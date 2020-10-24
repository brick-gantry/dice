import hashlib
import json
import redis
import time
from backend.dice_exception import DiceException

# cache_keep_duration = 60 * 60 * 3  # keep history for three hours
cache_keep_duration = 30


def _get_hash(x: str) -> bytes:
    return hashlib.sha256(x.encode()).hexdigest()


class RoomData:
    cache = redis.Redis(host='localhost', port=6379, db=0)

    def __init__(self, room: str, name: str, password: str):
        self.room = room
        self.name = name
        self.pubsub = self.cache.pubsub(ignore_subscribe_messages=True)
        self.room_member_password = f"r{self.room}-n{self.name}-password"
        self.room_connected_set_key = f"r{self.room}-connected"
        self.room_member_macros_key = f"r{self.room}-n{self.name}-macros"
        self.room_announce_channel_key = f"r{self.room}-announce"

        password_hash = _get_hash(password)
        if self.cache.exists(self.room_member_password):
            if password_hash != self.cache.get(self.room_member_password).decode('utf-8'):
                raise DiceException("Incorrect password")
        else:
            self.cache.set(self.room_member_password, password_hash)

        self.cache.sadd(self.room_connected_set_key, self.name)
        self.write_room_log(f"{self.name} enters {self.room}")
        self.pubsub.subscribe(self.room_announce_channel_key)

    def get_current(self):
        return {'current_members': self.read_room_members(),
                'history': self.read_room_log(),
                'macros': self.read_macros()}

    def member_leave_room(self):
        if self.room and self.name:
            self.cache.srem(self.room_connected_set_key, self.name)
            self.write_room_log(f"{self.name} leaves {self.room}")
        if self.pubsub:
            self.pubsub.close()
            self.pubsub = None

    def write_room_log(self, text: str):
        cache_key = f"{time.time()}:{self.room}"
        self.cache.publish(self.room_announce_channel_key, text)
        self.cache.set(cache_key, text, cache_keep_duration)

    def read_room_log(self):
        keys = sorted(self.cache.keys(f"*:{self.room}"))
        return [{'timestamp': k.decode('utf-8')[:k.index(b':')],
                 'text': v.decode('utf-8')} for k, v in zip(keys, self.cache.mget(keys))]

    def read_room_members(self):
        return [m.decode('utf-8') for m in self.cache.smembers(self.room_connected_set_key)]

    def write_macro(self, macro: dict):
        macro = json.dumps(macro)
        self.cache.sadd(self.room_member_macros_key, macro)

    def read_macros(self):
        return [json.loads(m.decode('utf-8')) for m in self.cache.smembers(self.room_member_macros_key)]

    def delete_macro(self, macro: dict):
        macro = json.dumps(macro)
        self.cache.srem(self.room_member_macros_key, macro)
