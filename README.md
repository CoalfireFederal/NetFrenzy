# NetFrenzy
Import a pcap file into Neo4j and view the network graph

# Contributing

Please make a new branch to make modifications, then submit a pull request rather than committing directly to the main branch.

If you have an old version of this repository, you can update your remote origin by:
```
git remote rename origin old
git remote add origin git@github.com:CoalfireFederal/NetFrenzy.git # If you use your SSH key to authenticate to GitHub
git remote add origin https://github.com/CoalfireFederal/NetFrenzy.git # If you use an access token to authenticate to GitHub
```

# Usage

## Setup

Install Neo4j with the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-neo4j-on-ubuntu-20-04)

`./setup.sh` will install the Python dependencies and install Neo4j's Graph Data Science Library

## Run

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

Found at `/web/NetFrenzy.html`, just open it in your browser

I made this

 - Config and Query UI can be hidden with a toggle
 - Query bar has a history. Use up/down arrow. Clears upon page reload
 - Pause button halts the graph movement physics
 - i button toggles a list of helpful queries you can click on, modify, and run
 - h button toggles your history, also clickable

![Preview](/screenshots/neovis-demo.png "Neovis.js client")

# Using community and pagerank

This will color nodes based on the clusters they form within the graph. This is most useful when you have a capture from a core network point rather than your local machine. Nodes will also appear larger based on the number of incoming/outgoing connections compared to other nodes.

![Preview](/screenshots/community.png "Community and PageRank")

## Setup

Requires the Neo4j [Graph Data Science Library](https://neo4j.com/download-center/#algorithms) downloaded and moved to `/var/lib/neo4j/plugins/` with the proper `neo4j:adm` ownership. If you have run `setup.sh`, this has already been done.

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
