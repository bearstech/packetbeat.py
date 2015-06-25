#!/usr/bin/env python
import time

import click
import redis

from elasticsearch import EventsHoseElasticsearch


@click.group()
@click.option('--host', default='localhost')
@click.option('--port', default=6379)
@click.option('--db', default=0)
@click.pass_context
def packetbeat(ctx, host, port, db):
    ctx.obj['HOST'] = host
    ctx.obj['PORT'] = port
    ctx.obj['DB'] = db

@packetbeat.command()
@click.pass_context
def channels(ctx):
    r = redis.StrictRedis(host=ctx.obj['HOST'], port=ctx.obj['PORT'],
                          db=ctx.obj['DB'])
    pubsub = r.pubsub()
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



@packetbeat.command()
@click.option('--channel', default='packetbeat/*')
@click.pass_context
def watch(ctx, channel):
    r = redis.StrictRedis(host=ctx.obj['HOST'],
                          port=ctx.obj['PORT'],
                          db=ctx.obj['DB'])
    hose = EventsHoseElasticsearch(r, channel)
    for event in hose:
        print(event.api, event.http.request.method, event.http.request.path)

if __name__ == '__main__':
    packetbeat(obj={})
