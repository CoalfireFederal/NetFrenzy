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

![Preview](/screenshots/Screen Shot 2022-01-18 at 4.51.56 PM.png "Preview")

This is after cranking up the node and relationship size. You can do so as shown below:

![Click here](/screenshots/Screen Shot 2022-01-18 at 4.52.05 PM.png "Node and Edge labels")

![then here](/screenshots/Screen Shot 2022-01-18 at 4.52.45 PM.png "Edit size, color")

MAC addresses and some IP addresses will still be...
