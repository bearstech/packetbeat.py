#!/usr/bin/env python
import time
import re

import click
import redis

from elasticsearch import EventsHoseElasticsearch


UA_SPLIT = re.compile('[/ ]')

def redis_factory(ctx):
    return redis.StrictRedis(host=ctx.obj['HOST'],
                             port=ctx.obj['PORT'],
                             db=ctx.obj['DB'])


@click.group()
@click.option('-h', '--host', default='localhost', help='Redis host.')
@click.option('-p', '--port', default=6379, help='Redis port.')
@click.option('-d', '--db', default=0, help='Redis db.')
@click.pass_context
def packetbeat(ctx, host, port, db):
    ctx.obj['HOST'] = host
    ctx.obj['PORT'] = port
    ctx.obj['DB'] = db


@packetbeat.command(help="Guess used channels.")
@click.pass_context
def channels(ctx):
    pubsub = redis_factory(ctx).pubsub()
    pubsub.psubscribe('packetbeat/*')
    channels = set()
    print("Guessing used channels, hit ctrl-C to stop.")
    try:
        while True:
            msg = pubsub.get_message()
            if msg is None:
                time.sleep(0.1)
                continue
            if msg['type'] in {'message', 'pmessage'}:
                channel = msg['channel']
                if channel not in channels:
                    print(channel)
                    channels.add(channel)
    except KeyboardInterrupt:
        pass


@packetbeat.command(help="Watch events on a channel.")
@click.option('-c', '--channel', default='packetbeat/*',
              help="Pick a channel, or a pattern.")
@click.pass_context
def watch(ctx, channel):
    hose = EventsHoseElasticsearch(redis_factory(ctx), channel)
    for event in hose:
        print(u"{clientserver} {api} {method} \
{took}ms {path} [{ua}]".format(clientserver=event.client_server,
                      api=event.api,
                      method= event.transaction.request.method,
                      took=event.responsetime,
                      path=event.transaction.request.path,
                      ua=UA_SPLIT.split(event.transaction.\
                                        request.headers.get('user-agent',
                                                            'Unknown'))[0]))


@packetbeat.command(help="Watch search speed on a channel.")
@click.option('-c', '--channel', default='packetbeat/*',
              help="Pick a channel, or a pattern.")
@click.pass_context
def search_stats(ctx, channel):
    hose = EventsHoseElasticsearch(redis_factory(ctx), channel)
    for event in hose:
        if event.api == 'search':
            r = event.transaction.response.json
            print(u"%s %i ms took: %i shards.total: %i shards.failed: %i \
hits.total: %i" % (event.transaction.request.path,
                   event.responsetime, r['took'],
                   r['_shards']['total'],
                   r['_shards']['failed'],
                   r['hits']['total']))


@packetbeat.command(help="Watch search speed on a channel.")
@click.option('-c', '--channel', default='packetbeat/*',
              help="Pick a channel, or a pattern.")
@click.pass_context
def bulk_stats(ctx, channel):
    hose = EventsHoseElasticsearch(redis_factory(ctx), channel)
    for event in hose:
        if event.api == 'bulk':
            r = event.transaction.response.json
            size = len(r['items'])
            print("{clientserver} {took} ms size:{size} \
errors:{errors}".format(clientserver=event.client_server,
                        took=r['took'],
                        size=size,
                        errors=r['errors']))

if __name__ == '__main__':
    packetbeat(obj={})
