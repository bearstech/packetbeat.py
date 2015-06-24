import json
import time

from http import Http

class Event(object):
    def __init__(self, raw):
        self.raw = raw
        self.timestamp = raw['@timestamp']
        self.responsetime = raw['responsetime']
        self.src_ip = raw['src_ip']
        self.agent = raw['agent']

    @property
    def http(self):
        if self.raw['http'] is None:
            return None
        return Http(self.raw)


class EventsHose(object):
    "Source of events"
    def __init__(self, redis_connection, chan='packetbeat/*'):
        self.r = redis_connection
        self.chan = chan
        assert self.r.ping()

    def __iter__(self):
        pubsub = self.r.pubsub()
        pubsub.psubscribe(self.chan)
        while True:
            msg = pubsub.get_message()
            if msg is None:
                time.sleep(0.1)
                continue
            if msg['type'] in {'message', 'pmessage'}:
                packet = json.loads(msg['data'])
                yield Event(packet)


if __name__ == '__main__':
    import sys
    import redis

    r = redis.StrictRedis(host=sys.argv[1], port=6379, db=0)
    hose = EventsHose(r)
    for event in hose:
        print event

