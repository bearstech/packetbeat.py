PacketBeat client
=================

Packetbeat steal packets and rebuild protocol for later analysis.
The main target is Logstash-Elasticsearch-Kibana, but you can refine event and analyzing its.

Packetbeat
----------

Your packetbeat agents have to use redis channel output

    ```YAML
    protocols:
      http:
        ports: [9200]
        send_request: true
        send_response: true
        include_body_for: ["application/json", "text/plain"]

    output:
      redis:
        enabled: true
        # Set the host and port where to find Redis.
        host: my_redis_broker
        port: 6379
        save_topology: true
        db: 0
        # Choose a name to avoid mess
        index: "packetbeat/sponge-bob"
        # Use pubsub communication
        datatype: channel
    ```

Client
------

Python 2.7 and Pypy are supported.

This project is a library, with a CLI.

Just try :

    python packetbat/cli.py --help


Licence
-------

3 Terms BSD licence, ©2015 Mathieu Lecarme
