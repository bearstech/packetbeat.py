PacketBeat client
=================

Packetbeat steal packets and rebuild protocol for later analysis.
The main target is Logstash-Elasticsearch-Kibana, but you can refine event and analyzing its.

Packetbeat
----------

Your packetbeat agents have to use redis channel output

    [output]
      [output.redis]
      # Uncomment out this option if you want to output to Redis.
      enabled = true
      # Choose a name to avoid mess
      index = "packetbeat/sponge-bob"

      # Use pubsub communication
      dataType = "channel"
      db = 0

      # Set the host and port where to find Redis.
      host = "my-redis-broker"
      port = 6379

    [protocols]
      [protocols.http]
        # I want to watch Elasticsearch usage
        ports = [9200]


Client
------

This project provides an API, not a CLI. Python 2.7 and Pypy are supported.

Just try :

    python packetbat/elasticsearch.py my-redis-broker


Licence
-------

3 Terms BSD licence, ©2015 Mathieu Lecarme
