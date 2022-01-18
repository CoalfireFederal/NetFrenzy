import json
import requests

class Neo4j:
    def __init__(self):
        self.commit = 'http://localhost:7474/db/data/transaction/commit'
        self.auth = None
        self.headers = {'Accept': 'application/json;charset=UTF-8', 'Content-Type': 'application/json'}

    def set_connection(self, connection):
        self.connection = connection
        # change default if configured
        self.commit.replace('localhost', self.connection.ip)
        self.auth = connection.requests_auth()

    def nuke_all_data(self):
        create = 'MATCH (n) DETACH DELETE n'
        data = {'statements': [{'statement': create}]}
        resp = requests.post(self.commit, data=data, auth=self.auth, headers=self.headers)
        return resp.json()['results'][0]['data'][0]['row']

    def new_node(self, label, properties):
        create = f'MERGE (n:{label} {properties}) RETURN id(n)'
        data = json.dumps({'statements': [{'statement': create}]})
        resp = requests.post(self.commit, data=data, auth=self.auth, headers=self.headers)
        return resp.json()['results'][0]['data'][0]['row']

    def new_node_dup(self, label, properties):
        create = f'CREATE (n:{label} {properties}) RETURN id(n)'
        data = json.dumps({'statements': [{'statement': create}]})
        resp = requests.post(self.commit, data=data, auth=self.auth, headers=self.headers)
        return resp.json()['results'][0]['data'][0]['row']

    def new_relationship(self, name_a, name_b, reltype, relprops=''):
        create = f'''MATCH
    (a),
    (b)
WHERE a.name="{name_a}" AND b.name="{name_b}"
MERGE (a)-[r:{reltype} {relprops}]->(b)
RETURN type(r)'''.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        data = {'statements': [{'statement': create}]}
        resp = requests.post(self.commit, json=data, auth=self.auth, headers=self.headers)
        return resp.json()['results'][0]['data'][0]['row']
        
    def new_relationship_id(self, name_a, name_b, reltype, relprops=''):
        create = f'''MATCH
    (a),
    (b)
WHERE id(a)={id_src} AND id(b)={id_dst}
MERGE (a)-[r:{reltype} {relprops}]->(b)
RETURN type(r)'''.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        data = {'statements': [{'statement': create}]}
        resp = requests.post(self.commit, data=json, auth=self.auth, headers=self.headers)
        return resp.json()['results'][0]['data'][0]['row']
        
