import json
import time

"""
Raw packetbeat client.
"""


class Event(object):
    """
{u'client_ip': u'10.20.125.63',
 u'client_port': 47685,
 u'client_proc': u'',
 u'client_server': u'bnp-logstash',
 u'count': 1,
 u'http': {u'code': 200, u'content_length': 158, u'phrase': u'OK'},
 u'ip': u'10.20.125.63',
 u'method': u'POST',
 u'params': u'',
 u'path': u'/_bulk',
 u'port': 9200,
 u'proc': u'',
 u'query': u'POST /_bulk',
 u'request': u'POST /_bulk HTTP/1.1\r\nContent-Length: 1143\r\nContent-Type: text/plain; charset=ISO-8859-1\r\nHost: 10.20.125.63:9200\r\nConnection: Keep-Alive\r\nUser-Agent: Manticore 0.4.1\r\nAccept-Encoding: gzip,deflate\r\n\r\n',
 u'response': u'HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=UTF-8\r\nContent-Length: 158\r\n\r\n{"took":1,"errors":false,"items":[{"create":{"_index":"logstash-avalon-2015.06.28","_type":"local7","_id":"AU47_9Kg2-jBDI-Jr-eB","_version":1,"status":201}}]}',
 u'responsetime': 2,
 u'server': u'bnp-logstash',
 u'shipper': u'bnp-logstash',
 u'status': u'OK',
 u'timestamp': u'2015-06-28T21:08:18.207Z',
 u'type': u'http'}
"""
    def __init__(self, raw):
        self.raw = raw
        self.client_ip = raw['client_ip']
        self.client_port = raw['client_port']
        self.client_proc = raw['client_proc']
        self.client_server = raw['client_server']
        self.count = raw['count']
        self.http = raw['http']
        self.ip = raw['ip']
        self.method = raw['method']
        self.params = raw['params']
        self.path = raw['path']
        self.port = raw['port']
        self.proc = raw['proc']
        self.query = raw['query']
        self.request = raw['request']
        self.response = raw['response']
        self.responsetime = raw['responsetime']
        self.server = raw['server']
        self.shipper = raw['shipper']
        self.status = raw['status']
        self.timestamp = raw['timestamp']
        self.type = raw['type']
        self.notes = raw.get('notes', None)

    def __repr__(self):
        return "<Event %s %s %ims>" % (self.client_server, self.type,
                                       self.responsetime)


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


if __name__ == '__main__':
    import sys
    import redis

    r = redis.StrictRedis(host=sys.argv[1], port=6379, db=0)
    hose = EventsHose(r)
    for event in hose:
        print event
