import json
import time


class Event(object):
    def __init__(self, raw):
        self.raw = raw
        self.timestamp = raw['@timestamp']
        self.responsetime = raw['responsetime']
        self.src_ip = raw['src_ip']
        self.agent = raw['agent']


class EventsHose(object):
    event = Event
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
                yield self.event(packet)
