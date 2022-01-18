# wireshark4j
Import a pcap file into Neo4j and view the network graph

```bash
python3 main.py ../path/to/your.pcap config.json
```

View in Neo4j browser console `http://localhost:7474/browser/`

Display all nodes and relationships

```
MATCH (n) RETURN (n)
```

Narrow down the results yourself `https://neo4j.com/docs/cypher-manual/current/clauses/match/`

Clear out all objects in database (start over)
```
MATCH (n) DETACH DELETE n
```
