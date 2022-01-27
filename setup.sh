#!/bin/bash

# Install our own requirements
python3 -m pip install -r requirements.txt

# Download the graph data library from neo4j
wget https://s3-eu-west-1.amazonaws.com/com.neo4j.graphalgorithms.dist/graph-data-science/neo4j-graph-data-science-1.8.3-standalone.zip -O /tmp/gds.zip
unzip /tmp/gds.zip

# Install the graph data library into the plugins folder
sudo mv neo4j-graph-data-science-1.8.3.jar /var/lib/neo4j/plugins/neo4j-graph-data-science-1.8.3.jar
sudo chown neo4j:adm /var/lib/neo4j/plugins/neo4j-graph-data-science-1.8.3.jar

# Change config
sudo echo "dbms.security.procedures.unrestricted=gds.*" >> /etc/neo4j/neo4j.conf

# Restart neo4j
sudo systemctl restart neo4j
