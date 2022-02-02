var helpfulqueries = {
	"Display all nodes and relationships": "MATCH (n), (o)-[r]-(m) RETURN *",
	"Find all connections from an IP": "MATCH (n:IP {name: \"192.168.119.151\"})-[r:CONNECTED]->(m) RETURN *",
	"Display all paths which do not involve a multicast address": "MATCH path=(n)-[r]-(m) WHERE NONE(n IN nodes(path) WHERE n.multicast OR (n)-[:ASSIGNED]-(:MAC {multicast: true})) RETURN path",
	"Display all connections to/from privileged ports": "MATCH (n)<-[r:CONNECTED]-(m) WHERE r.port < 1024 AND r.port > 0 RETURN *",
	"Display all MAC addresses with only one IP assigned": "MATCH (n:IP)-[r:ASSIGNED]->(m:MAC) WITH m, COUNT(r) AS count WHERE count = 1 MATCH (n)-[r:ASSIGNED]->(m) RETURN n,r,m",
	"Display all connections from IPs who do not share their MAC address": "MATCH (n:IP)-[r:ASSIGNED]->(m:MAC) WITH m, COUNT(r) AS count WHERE count = 1 MATCH (n)-[r:ASSIGNED]->(m) WITH n MATCH (o:MAC)-[r1]-(n:IP)-[r:CONNECTED]-(m:IP) RETURN n,r,r1,m,o",
	"Find all 80/tcp connections": "MATCH (n)-[r:CONNECTED {port: 80, protocol: \"tcp\"}]->(m) RETURN *",
	"Top 10 IPs with most outbound connections": "MATCH (n:IP), (m:IP), (n)-[r:CONNECTED]->(m) WITH n, count(r) AS rel_count ORDER BY rel_count DESC LIMIT 10 MATCH p=(m)<-[r:CONNECTED]-(n) RETURN p",
	"Top 10 connections by data transferred": "MATCH ()-[r:CONNECTED]->(:IP) WITH r, r.data_size AS data ORDER BY data DESC LIMIT 10 MATCH (n)-[r]-(m) RETURN n,r,m",
}

// vim: ts=2 sts=2
