
function toggleElem(id) {
	var elem = document.getElementById(id);
	if (elem.style.display == "none") {
		elem.style.display = "block";
	} else {
		elem.style.display = "none";
	}
}
function toggleConfig() {
	toggleElem("configinputs");
}
function toggleQuery() {
	toggleElem("queryui");
}

function applyConfig() {
	var server = document.getElementById("server").value;
	var username = document.getElementById("username").value;
	var password = document.getElementById("password").value;
	var weight = document.getElementById("weight").value;
	var caption = document.getElementById("caption").value;
	window.config.server_url = server;
	window.config.server_user = username;
	window.config.server_password = password;
	switch (weight) {
		case "none":
			window.config.relationships["CONNECTED"]["thickness"] = "0.1";
			break;
		case "data_size":
			window.config.relationships["CONNECTED"]["thickness"] = "data_size";
			break;
		case "count":
			window.config.relationships["CONNECTED"]["thickness"] = "count";
			break;
	}
	switch (caption) {
		case "service":
			window.config.relationships["CONNECTED"]["caption"] = "service";
			break;
		case "name":
			window.config.relationships["CONNECTED"]["caption"] = "name";
			break;
	}
	if (query_history.length >= 1) {
		window.config.initial_cypher = query_history[query_history.length - 1];
	}
            window.viz = new NeoVis.default(window.config);
            window.viz.render();
}

function runQuery() {
	var q = document.getElementById("query").value;
	if (q === "") { return; }
	if (query_history[query_history.length - 1] != q) {
		query_history.push(q);
		query_history_pos = query_history.length - 1;
	}
	window.viz.renderWithCypher(q);
}

function customStartup() {
	var inp1 = document.getElementById("password");
	inp1.addEventListener("keyup", function(event) {
		if (event.keyCode === 13) {
			event.preventDefault();
			document.getElementById("submitconfig").click();
		}
	});
	var inp2 = document.getElementById("query");
	inp2.addEventListener("keyup", function(event) {
		if (event.keyCode === 13) {
			event.preventDefault();
			document.getElementById("runquery").click();
		}
	});

	var inp3 = document.getElementById("query");
	window.query_history = [window.config.initial_cypher];
	window.query_history_pos = 0;
	if (inp3.value != "") {
		window.query_history.push(inp3.value);
	}
	inp2.addEventListener("keyup", function(event) {
		if (event.keyCode === 38) { // Up arrow
			event.preventDefault();
			if (query_history_pos == 0 && query_history.length > 0) {
				query_history_pos = query_history.length - 1;
			} else if (query_history_pos >= 1) {
				query_history_pos--;
			} else {
				
			}
			this.value = query_history[query_history_pos];
			this.setSelectionRange(this.value.length,this.value.length);
		}
		if (event.keyCode === 40) { // Down arrow
			event.preventDefault();
			if (query_history_pos == query_history.length - 1) {
				query_history_pos = 0;
			} else {
				query_history_pos++;
			}
			this.value = query_history[query_history_pos];
		}
	});
}
