
function toggleElem(id) {
	var elem = document.getElementById(id);
	if (elem.style.display == "none" || elem.style.display == "") {
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
function toggleHistory() {
	toggleElem("queryhistory");
}
function toggleInfo() {
	toggleElem("queryinfo");
}
function toggleError() {
	toggleElem("error-floater");
}

function applyConfig() {
	var server = document.getElementById("server").value;
	var username = document.getElementById("username").value;
	var password = document.getElementById("password").value;
	var layout = document.getElementById("layout").value;
	var sort = document.getElementById("sort").value;
	var weight = document.getElementById("weight").value;
	var caption = document.getElementById("caption").value;
	var commweight = document.getElementById("commweight").value;
	window.config.server_url = server;
	window.config.server_user = username;
	window.config.server_password = password;
	
	switch (layout) {
		case "none":
			window.config.hierarchical = false;
			document.getElementById("sort").disabled = true;
			break;
		case "hierarchical":
			window.config.hierarchical = true;
			document.getElementById("sort").disabled = false;
			break;
	}
	switch (sort) {
		case "hubsize":
			window.config.hierarchical_sort_method = "hubsize";
			break;
		case "directed":
			window.config.hierarchical_sort_method = "directed";
			break;
	}
	
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
		case "none":
			window.config.relationships["CONNECTED"]["caption"] = false;
			break;
		case "service":
			window.config.relationships["CONNECTED"]["caption"] = "service";
			break;
		case "name":
			window.config.relationships["CONNECTED"]["caption"] = "name";
			break;
	}
	
	switch (commweight) {
		case "none":
			window.config.relationships["COMMUNICATES"]["thickness"] = "0.1";
			break;
		case "total":
			window.config.relationships["COMMUNICATES"]["thickness"] = "total";
			break;
		case "data":
			window.config.relationships["COMMUNICATES"]["thickness"] = "data";
			break;
		case "ports":
			window.config.relationships["COMMUNICATES"]["thickness"] = "ports";
			break;
	}
	
	// Toggle error visibility if required
	var elem = document.getElementById("error-floater");
	if (elem.style.display == "block") {
		elem.style.display = "none";
	}
	
	if (query_history.length >= 1) {
		window.config.initial_cypher = query_history[query_history.length - 1];
	}
	window.viz = new NeoVis.default(window.config);
	
	window.viz.registerOnEvent('error', neo4jErrorHandler);
	
	window.viz.render();
}

function neo4jErrorHandler(e) {
	var elem = document.getElementById("error-message");
	elem.innerText = e.error_msg.message;
	// Toggle error visibility if required
	var elem = document.getElementById("error-floater");
	if (elem.style.display == "none" || elem.style.display == "") {
		elem.style.display = "block";
	}
}

function runQuery() {
	var q = document.getElementById("query").value;
	if (q === "") { return; }
	manage_qhistory_new(q);
	// Toggle error visibility if required
	var elem = document.getElementById("error-floater");
	if (elem.style.display == "block") {
		elem.style.display = "none";
	}
	window.viz.renderWithCypher(q);
}

function manage_qhistory_init(elem) {
	window.query_history = [window.config.initial_cypher];
	window.query_history_pos = 0;
	if (elem.value != "" && elem.value != window.query_history[0]) {
		window.query_history.push(elem.value);
	}
	manage_qhistory_list();
}

function manage_qhistory_list() {
	var elem = document.getElementById("queryhistoryol");

	while (elem.firstChild) {
		elem.removeChild(elem.firstChild);
	}

	for (var i=0; i<query_history.length; i++) {
		var listitem = document.createElement("li");
		listitem.innerText = query_history[i];
		listitem.setAttribute("class", "qh-item");
		listitem.onclick = function() {
			document.getElementById("query").value = this.innerText;
		}
		elem.appendChild(listitem);
	}
}

function manage_qhistory_new(query) {
	if (query === "") { return; }
	
	// Prevent duplicate queries in a row in the history
	if (query_history[query_history.length - 1] === query) {
		return;
	}

	query_history.push(query);
	query_history_pos = query_history.length - 1;

	manage_qhistory_list();
}

function manage_qhistory_clear() {
	query_history_pos = 0;
	query_history = [query_history[query_history.length - 1]];
	manage_qhistory_list();
}

function initHelpfulQueries() {
	var elem = document.getElementById("customqueries");

	while (elem.firstChild) {
		elem.removeChild(elem.firstChild);
	}

	for (const prop in helpfulqueries) {
		var listitemitem = document.createElement("li");
		var listitem = document.createElement("a");
		listitem.innerText = prop;
		listitem.setAttribute("class", "hq-item");
		listitem.setAttribute("title", helpfulqueries[prop]);
		listitem.onclick = function() {
			document.getElementById("query").value = this.getAttribute("title");
		}
		listitemitem.appendChild(listitem);
		elem.appendChild(listitemitem);
	}
}

//toggle between <input> and <textarea> query forms
function toggleTextArea(){
	if (document.getElementById('query').tagName == 'INPUT') {
		var input = document.getElementById('query');
		var text = document.createElement('textarea');
		text.setAttribute('name', input.getAttribute('name'));
		text.setAttribute('id', input.getAttribute('id'));
		text.setAttribute('rows', '8');
		text.value = input.value;
		input.parentNode.replaceChild(text, input);
		document.getElementById('linetoggle').setAttribute("value", "↥")
		setTabListener(text)
	}
	else if (document.getElementById('query').tagName == 'TEXTAREA') {
		var text = document.getElementById('query');
		var input = document.createElement('input');
		input.setAttribute('name', text.getAttribute('name'));
		input.setAttribute('id', text.getAttribute('id'));
		input.value = text.value;
		text.parentNode.replaceChild(input, text);
		document.getElementById('linetoggle').setAttribute("value", "↧")
		setEnterListener(input)
	}
}

function createcommunity(i) {
	var commands = [
		"CALL gds.graph.drop('networkgraph')",
		"MATCH (r1)-[r3:CONNECTED]->(r2) WITH r1, r2, COUNT(*) AS ports, sum(r3.count) as total, sum(r3.data_size) as data MERGE (r2)<-[r:COMMUNICATES]-(r1) SET r.ports = ports, r.total = total, r.data = data",
		"CALL gds.graph.create('networkgraph', ['IP', 'MAC'], 'COMMUNICATES', { relationshipProperties: 'total' })",
		"CALL gds.labelPropagation.write('networkgraph', { writeProperty: 'community' })",
		"CALL gds.pageRank.write('networkgraph',{writeProperty: 'pagerank'})",
	]
	
	console.log(commands[i]);
	window.viz.renderWithCypher(commands[i]);
	
	if (i < commands.length - 1) {
		setTimeout(function() {
			createcommunity(i+1);
		}, 5000);
	}
}

function setEnterListener(el) {
	el.addEventListener("keyup", function(event) {
		if (event.keyCode === 13) {
			event.preventDefault();
			document.getElementById("runquery").click();
		}
	});
}

//https://stackoverflow.com/questions/6637341/use-tab-to-indent-in-textarea
function setTabListener(el) {
	el.addEventListener('keydown', function(e) {
		if (e.key == 'Tab') {
			e.preventDefault();
			var start = this.selectionStart;
			var end = this.selectionEnd;
			this.value = this.value.substring(0, start) + "\t" + this.value.substring(end);
			this.selectionStart = this.selectionEnd = start + 1;
		}
	});
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
	setEnterListener(inp2)
	
	var inp3 = document.getElementById("query");
	manage_qhistory_init(inp3);
	
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
	
	initHelpfulQueries();
}

// vim: ts=2 sts=2
