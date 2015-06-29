import json

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

from beat import Event, EventsHose

"""
Packetbeat events are HTTP.
"""


class EventHttp(Event):
    _transaction = None

    @property
    def transaction(self):
        if self.type != 'http':
            return None
        if self._transaction is None:
            self._transaction = Http(self)
        return self._transaction


class EventsHoseHttp(EventsHose):
    event = EventHttp

    def __iter__(self):
        for event in super(EventsHoseHttp, self).__iter__():
            if event.type == 'http':
                yield event


class Http(object):
    def __init__(self, raw):
        self.raw = raw
        self.request = HttpRequest(raw)
        self.response = HttpResponse(raw)

    def __repr__(self):
        return "<Http %s %s>" % (repr(self.request), repr(self.response))


class HttpRequest(object):
    def __init__(self, raw):
        self.raw = raw
        req = HttpParser()
        req.execute(raw.request, len(raw.request))
        self.headers = req.get_headers()
        self.body = "".join(req._body)
        self.url = req.get_url()
        self.path = req.get_path()
        self.method = req.get_method()
        self.arguments = req.get_query_string()
        self.slug = [a for a in self.path.split('/') if a != '']

    def __repr__(self):
        return u"<Request %s %s>" % (self.method, self.url)

    @property
    def json(self):
        if self.body == '':
            return None
        return json.loads(self.body)


class HttpResponse(object):
    def __init__(self, raw):
        resp = HttpParser()
        resp.execute(raw.response, len(raw.response))
        self.headers = resp.get_headers()
        self.body = "".join(resp._body)
        self.raw = raw
        self.code = resp.get_status_code()
        self._json = None

    def __repr__(self):
        return u"<Response %i>" % self.code

    @property
    def json(self):
        if self._json is None:
            self._json = json.loads(self.body)
        return self._json


if __name__ == '__main__':
    import sys
    import redis

    r = redis.StrictRedis(host=sys.argv[1], port=6379, db=0)
    hose = EventsHoseHttp(r)
    for event in hose:
        print event.transaction
