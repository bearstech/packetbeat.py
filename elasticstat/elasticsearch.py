from http import EventHttp, EventsHoseHttp


class EventElasticsearch(EventHttp):

    @property
    def bluk(self):
        if self.http.request.path == '/_bulk':
            pass
        return None

    @property
    def api(self):
        if len(self.http.request.slug) == 0:
            return 'root'
        first = self.http.request.slug[0]
        if first.startswith('_'):
            return first[1:]
        last = self.http.request.slug[-1]
        if last.startswith('_'):
            return last[1:]
        return 'index'


class EventsHoseElasticsearch(EventsHoseHttp):
    event = EventElasticsearch


if __name__ == '__main__':
    import sys
    import redis

    r = redis.StrictRedis(host=sys.argv[1], port=6379, db=0)
    hose = EventsHoseElasticsearch(r)
    for event in hose:
        print event.api, event.http.request.method, event.http.request.path
