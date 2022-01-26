# wireshark4j
Import a pcap file into Neo4j and view the network graph

# Contributing

Please submit a pull request rather than committing directly to the repository.

# Usage

```bash
python3 main.py -p ../path/to/your.pcap -c ws4j.json -nc
```

Processes approx. 30-60 packets per second into Neo4j.

If you have multiple PCAPs, you can run this injestor in parallel to get speed benefits up to the number of CPUs assigned to your VM.

# Why

 - Visualize the network from a PCAP
 - Verify network segmentation
 - Identify CTF players attacking each other

# Demo

## Using the custom Neovis.js client

Found at `/web/index.html`, just open it in your browser

I made this

 - Config and Query UI can be hidden with a toggle
 - Query bar has a history. Use up/down arrow. Clears upon page reload
 - Pause button halts the graph movement physics
 - i button toggles a list of helpful queries you can click on, modify, and run
 - h button toggles your history, also clickable

![Preview](/screenshots/neovis-demo.png "Neovis.js client")

# Using community and pagerank

This will color nodes based on the clusters they form within the graph. This is most useful when you have a capture from a core network point rather than your local machine. Nodes will also appear larger based on the number of incoming/outgoing connections compared to other nodes.

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
