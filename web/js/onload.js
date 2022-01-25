
function draw() {
	window.config = {
		container_id: "viz",
		server_url: "bolt://localhost:7687",
		server_user: "neo4j",
		server_password: "neo4j",
		arrows: true,
		labels: {
			"IP": {
				"caption": "name",
				"size": "1",
			"font": {"size": 12}
			},
			"MAC": {
				"caption": "name",
				"size": "1",
			"font": {"size": 12, "color": "#0000BB"}
			},
			"SSID": {
				"caption": "name",
				"size": "1",
			"font": {"size": 12, "color": "#BB00BB"}
			},
			"ASSIGNED": {
				"caption": "name",
				"size": "0.1",
				"title_properties": [
					"name",
					"pagerank"
				],
			"font": {"size": 12, "color": "#0000BB"}
			}
		},
		relationships: {
			"CONNECTED": {
				"thickness": "data_size",
				"caption": "service"
			},
			"ASSIGNED": {
				"thickness": "0.1",
				"caption": true,
			},
			"ADVERTISES": {
				"thickness": "0.1",
				"caption": true,
			}
		},
		initial_cypher: "MATCH (n) RETURN *"
	};

	window.viz = new NeoVis.default(window.config);
	window.viz.render();
	customStartup();
}

// vim: ts=2 sts=2
