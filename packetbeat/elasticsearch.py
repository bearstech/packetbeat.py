import json

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


def bulk_request(event):
    action = None
    for line in event.http.request.body.split('\n')[:-1]:
        if action is None:
            action = json.loads(line).items()[0]
            if action[0] not in {'index', 'create'}:
                yield action
                action = None
        else:
            yield action[0], action[1], line
            action = None

class EventsHoseElasticsearch(EventsHoseHttp):
    event = EventElasticsearch


if __name__ == '__main__':
    import sys
    import redis

    r = redis.StrictRedis(host=sys.argv[1], port=6379, db=0)
    hose = EventsHoseElasticsearch(r)
    for event in hose:
        print event.api, event.http.request.method, event.http.request.path
        if event.api == 'bulk':
            for action in bulk_request(event):
                print "\t", action

            print "\t", event.http.response.json
