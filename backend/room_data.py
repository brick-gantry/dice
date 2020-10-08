import json
import redis
import time

# cache_keep_duration = 60 * 60 * 3  # keep history for three hours
cache_keep_duration = 30


class RoomData:
    cache = redis.Redis(host='localhost', port=6379, db=0)

    def __init__(self):
        self.room = None
        self.name = None
        self.pubsub = None
        self.members_set = ""
        self.member_macros = ""
        self.announce_channel = ""

    def member_enter_room(self, room: str, name: str):
        self.room = room
        self.name = name
        self.pubsub = self.cache.pubsub(ignore_subscribe_messages=True)
        self.members_set = f"{self.room}-members"
        self.member_macros = f"{self.room}-{self.name}-macros"
        self.announce_channel = f"{self.room}-announce"

        self.cache.sadd(self.members_set, self.name)
        self.write_room_log(f"{self.name} enters {self.room}")
        self.pubsub.subscribe(self.announce_channel)

        current_members = self.read_room_members()
        history = self.read_room_log()
        macros = self.read_macros()

        return {'current_members': current_members,
                'history': history,
                'macros': macros}

    def member_leave_room(self):
        if self.room and self.name:
            self.cache.srem(self.members_set, self.name)
            self.write_room_log(f"{self.name} leaves {self.room}")
        if self.pubsub:
            self.pubsub.close()
            self.pubsub = None

    def write_room_log(self, text: str):
        cache_key = f"{time.time()}:{self.room}"
        self.cache.publish(self.announce_channel, text)
        self.cache.set(cache_key, text, cache_keep_duration)

    def read_room_log(self):
        keys = sorted(self.cache.keys(f"*:{self.room}"))
        return [{'timestamp': k.decode('utf-8')[:k.index(b':')],
                 'text': v.decode('utf-8')} for k, v in zip(keys, self.cache.mget(keys))]

    def read_room_members(self):
        return [m.decode('utf-8') for m in self.cache.smembers(self.members_set)]

    def write_macro(self, macro: dict):
        macro = json.dumps(macro)
        self.cache.sadd(self.member_macros, macro)

    def read_macros(self):
        return [json.loads(m.decode('utf-8')) for m in self.cache.smembers(self.member_macros)]

    def delete_macro(self, macro: dict):
        macro = json.dumps(macro)
        self.cache.srem(self.member_macros, macro)
