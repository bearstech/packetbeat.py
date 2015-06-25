import json

from beat import Event, EventsHose


class EventHttp(Event):
    @property
    def http(self):
        if self.raw['http'] is None:
            return None
        return Http(self.raw)


class EventsHoseHttp(EventsHose):
    event = EventHttp

    def __iter__(self):
        for event in super(EventsHoseHttp, self).__iter__():
            if event.raw['http'] is not None:
                yield event


def parse_headers(raw):
    d = {}
    for line in raw.split('\r\n')[1:]:
        k, v = line.split(': ', 1)
        d[k.lower()] = v
    return d


class Http(object):
    def __init__(self, raw):
        self.raw = raw
        self.request = HttpRequest(self.raw['http'], self.raw['request_raw'])
        self.response = HttpResponse(self.raw['http'], self.raw['response_raw'])


class HttpRequest(object):
    def __init__(self, http, raw):
        self.raw = raw
        self.host = http['host']
        self.uri = http['request']['uri']
        self.method = http['request']['method']
        s = self.uri.split('?')
        self.path = s[0]
        if len(s) > 1:
            self.arguments = s[1]
        else:
            self.arguments = None
        self.path = s[0]
        self.slug = [a for a in self.path.split('/') if a != '']
        self.header, self.body = self.raw.split('\r\n\r\n', 1)
        self.header = parse_headers(self.header)

    @property
    def json(self):
        return json.loads(self.body)

    def __len__(self):
        return len(self.raw)


class HttpResponse(object):
    def __init__(self, http, raw):
        self.raw = raw
        self.code = http['response']['code']
        self._header = None
        self._body = None
        self._json = None

    def _parse(self):
        self._header, self._body = self.raw.split('\r\n\r\n', 1)

    def __len__(self):
        return len(self.raw)

    @property
    def body(self):
        if self._body is None:
            self._parse()
        return self._body

    @property
    def header(self):
        if self._header is None:
            self._parse()
        return self._header

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
        print event
