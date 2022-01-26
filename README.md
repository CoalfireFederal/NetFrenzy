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

# Using community and pagerank

Requires the Neo4j [Graph Data Science Library](https://neo4j.com/download-center/#algorithms) downloaded and moved to `/var/lib/neo4j/plugins/` with the proper `neo4j:adm` ownership.

## Setup

1\. Create the simple connection we will build our community and pagerank around

```
MATCH (r1)-[:CONNECTED]->(r2)
WITH r1, r2, COUNT(*) AS count
MERGE (r2)<-[r:COMMUNICATES]-(r1)
SET r.count = count
```

2\. Create the graph

```
CALL gds.graph.create('networkgraph', ['IP', 'MAC'], 'COMMUNICATES',
    { relationshipProperties: 'count' }
);
```

## Creating a community

3\. Create the `community` property using the [labelPropagation algorithm](https://data-xtractor.com/blog/graphs/neo4j-graph-algorithms-community-detection/#6_Label_Propagation_Algorithm_LPA)

```
CALL gds.labelPropagation.write('networkgraph', { writeProperty: 'community' })
YIELD communityCount, ranIterations, didConverge
```

## Creating pagerank

4\. Create the `pagerank` property using the [pageRank algorithm](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/#algorithms-page-rank-examples-write)

```
CALL gds.pageRank.write(
  'networkgraph',
  {
    writeProperty: 'pagerank'
  }
)
YIELD
  nodePropertiesWritten,
  createMillis,
  ranIterations,
  configuration AS conf
RETURN
  nodePropertiesWritten,
  createMillis,
  ranIterations,
  conf.writeProperty AS writeProperty
```

# Helpful queries

Clear out all objects in database (start over)

```
MATCH (n) DETACH DELETE n
```
