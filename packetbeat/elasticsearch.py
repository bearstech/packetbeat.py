import json

from http import EventHttp, EventsHoseHttp

"""
Packetbeat events are Elasticsearch actions.
"""

class EventElasticsearch(EventHttp):

    @property
    def bulk(self):
        if self.api not in ['bulk', 'msearch']:
            return None
        return bulk_request(self.transaction)

    @property
    def api(self):
        if len(self.transaction.request.slug) == 0:
            return 'root'
        first = self.transaction.request.slug[0]
        if first.startswith('_'):
            return first[1:]
        last = self.transaction.request.slug[-1]
        if last.startswith('_'):
            return last[1:]
        return 'index'


def bulk_request(transaction):
    action = None
    for line in transaction.request.body.split('\n')[:-1]:
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
        print "\n", event.api, event.transaction.request.method, event.transaction.request.path
        if event.api == 'bulk':
            for action in event.bulk:
                print "\t>", action
        else:
            print "\t>", event.transaction.request.json
        print "\t<", event.transaction.response.json
