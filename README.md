# wireshark4j
Import a pcap file into Neo4j and view the network graph

# Usage

```bash
python3 main.py -p ../path/to/your.pcap -c config.json -i 00:50:56:e5:33:52
```

Processes approx. 40-60 packets per second into Neo4j.

# Why

 - Visualize the network from a PCAP
 - Verify network segmentation
 - Identify CTF players attacking each other

# Example and how to resize

## Using the custom Neovis.js client

Found at `/web/index.html`, just open it in your browser

I made this

 - Config and Query UI can be hidden with a toggle
 - Query bar has a history. Use up/down arrow. Clears upon page reload
 - Pause button halts the graph movement physics

![Preview](/screenshots/Screen%20Shot%202022-01-19%20at%203.02.39%20PM.png "Neovis.js client")

## Using the Neo4j Browser

![Preview](/screenshots/Screen%20Shot%202022-01-18%20at%204.51.56%20PM.png "Preview")

This is after cranking up the node and relationship size. You can do so as shown below:

![Click here](/screenshots/Screen%20Shot%202022-01-18%20at%204.52.05%20PM.png "Node and Edge labels")

![then here](/screenshots/Screen%20Shot%202022-01-18%20at%204.52.45%20PM.png "Edit size, color")

MAC addresses and some IP addresses will still be...

# Helpful queries

Modify to suit your needs

Find all 80/tcp connections

```
MATCH (n)-[r:CONNECTED {port: 80, protocol: "tcp"}]->(m) RETURN n,r,m
```

Find all connections to/from an IP

```
MATCH (n {name: "192.168.119.151"})-[r:CONNECTED]->(m) RETURN n,r,m
```

Display all nodes and relationships

```
MATCH (n) RETURN (n)
```

Narrow down the results yourself `https://neo4j.com/docs/cypher-manual/current/clauses/match/`

Display all paths which do not involve a multicast address
```
MATCH path=(n)-[r]-(m) WHERE NONE(n IN nodes(path) WHERE exists(n.multicast)) RETURN path
```


Clear out all objects in database (start over)

```
MATCH (n) DETACH DELETE n
```
