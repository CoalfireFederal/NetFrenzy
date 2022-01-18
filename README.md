# wireshark4j
Import a pcap file into Neo4j and view the network graph

# Usage

```bash
python3 main.py -p ../path/to/your.pcap -c config.json -i 00:50:56:e5:33:52
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

# Example and how to resize

![Preview](/screenshots/Screen%20Shot%202022-01-18%20at%204.51.56%20PM.png "Preview")

This is after cranking up the node and relationship size. You can do so as shown below:

![Click here](/screenshots/Screen%20Shot%202022-01-18%20at%204.52.05%20PM.png "Node and Edge labels")

![then here](/screenshots/Screen%20Shot%202022-01-18%20at%204.52.45%20PM.png "Edit size, color")

MAC addresses and some IP addresses will still be...
