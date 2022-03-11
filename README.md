# NetFrenzy
Import a pcap file into Neo4j and view the network graph

# Usage

## Setup

Install Neo4j with the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-neo4j-on-ubuntu-20-04)

`./setup.sh` will install the Python dependencies and install Neo4j's Graph Data Science Library

## Run

**Importing a pcap file**
```bash
python3 NetFrenzy.py -p ../path/to/your.pcap -nc
```

Processes approx. 45-55 packets per second into Neo4j. Enable `--reduce` to increase speeds to 160-180 packets per second at the cost of less information stored about the connections.

**Running a live capture**
```bash
python3 NetFrenzy.py --live eth0
```

Live captures enable `--reduce` automatically which increases performance to keep up with the live capture.

**Recommended system specs**

Neo4j can be run in the same VM as the ingestor or in a separate VM.

Recommended minimum VM specs:

 - 6GB RAM, no swap
 - 3 CPU assigned

# Why

The human eye is the ultimate sensor.

 - Visualize the network from a PCAP
 - Verify network segmentation
 - Easily identify anomalies

# Demo

## Using the custom Neovis.js client

Found at `/web/NetFrenzy.html`, just open it in your browser

 - UI elements can be toggled by clicking on their label
 - Use up/down arrow or history button to access and replay queries
 - Pause button halts the graph physics
 - Built-in list of queries you may find helpful

![Preview](/screenshots/neovis-demo.png "Neovis.js client")

# Using community and pagerank

This will color nodes based on the clusters they form within the graph. This is most useful when you have a capture from a core network point rather than your local machine. Nodes will also appear larger based on the number of incoming/outgoing connections compared to other nodes.

![Preview](/screenshots/community.png "Community and PageRank")

## Setup

Requires the Neo4j [Graph Data Science Library](https://neo4j.com/download-center/#algorithms) downloaded and moved to `/var/lib/neo4j/plugins/` with the proper user and group permissions. If you have run `setup.sh`, this has already been done.

## How to generate

Open the Info pane by clicking the `i` button. Click the `Create COMMUNICATES relationship, Community, and PageRank` link. Wait 20 seconds. Now, you should see that nodes have different colors.

## Get rid of the colors

If you don't find the colors useful for your graph screenshots, you can run the command:

```
MATCH (n) REMOVE n.community REMOVE n.pagerank
```

# Helpful queries

Clear out all objects in database (start over)

```
MATCH (n) DETACH DELETE n
```

# Contributing

Please check out the [Good First Issues](https://github.com/CoalfireFederal/NetFrenzy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Feel free to contribute user stories to explain how new functionality could improve NetFrenzy. Issues with Help Wanted are requesting input from the community on implementation details and general usability.

**For CoalfireFederal organization members:**

Please make a new branch to make modifications, then submit a pull request rather than committing directly to the main branch. Your branch can be deleted once the pull request is merged. Assign yourself to an issue to let me know you're working on it.

