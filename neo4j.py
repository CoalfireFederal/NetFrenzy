import json
import requests

class Neo4j:
    def __init__(self):
        self.commit = 'http://localhost:7474/db/data/transaction/commit'
        self.auth = None
        self.headers = {'Accept': 'application/json;charset=UTF-8', 'Content-Type': 'application/json'}
        self.debug = False

    def set_connection(self, connection):
        self.connection = connection
        # change default if configured
        self.commit.replace('localhost', self.connection.ip)
        self.auth = connection.requests_auth()

    def execute_query(self, query):
        data = {'statements': [{'statement': query}]}
        resp = requests.post(self.commit, json=data, auth=self.auth, headers=self.headers)
        if self.debug:
            import pdb; pdb.set_trace()
        try:
            return resp.json()['results'][0]['data'][0]['row']
        except Exception as e:
            print(f'Exception:\t{type(e)}: {e}')
            print(f'Query:\t{query}')
            print(f'Response:\tresp.json()')
            raise

    def nuke_all_data(self):
        query = 'MATCH (n) DETACH DELETE n'
        return self.execute_query(query)

    def new_node(self, label, properties):
        query = f'MERGE (n:{label} {properties}) RETURN id(n)'
        return self.execute_query(query)

    def new_node_dup(self, label, properties):
        query = f'CREATE (n:{label} {properties}) RETURN id(n)'
        return self.execute_query(query)

    def new_relationship(self, name_a, name_b, reltype, relprops=''):
        query = f'''MATCH
    (a),
    (b)
WHERE a.name="{name_a}" AND b.name="{name_b}"
MERGE (a)-[r:{reltype} {relprops}]->(b)
RETURN type(r)'''.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        return self.execute_query(query)
        
    def new_relationship_id(self, name_a, name_b, reltype, relprops=''):
        query = f'''MATCH
    (a),
    (b)
WHERE id(a)={id_src} AND id(b)={id_dst}
MERGE (a)-[r:{reltype} {relprops}]->(b)
RETURN type(r)'''.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        return self.execute_query(query)
        
    def increment_node_property(self, name, _property):
        query = f'MATCH (n {{name: "{name}"}}) SET n.{_property} = n.{_property} + 1 RETURN n.{_property}'
        return self.execute_query(query)

    # Finds a relationship between name_a and name_b with the properties rprop
    # then increments the relationship's _property value
    def increment_relationship_property(self, name_a, name_b, rprop, _property):
        query = f'MATCH (n {{name: "{name_a}"}})-[r {rprop}]->(m {{name: "{name_b}"}}) SET r.{_property} = r.{_property} + 1 RETURN r.{_property}'
        return self.execute_query(query)

    def raw_query(self, query):
        query = query.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        return self.execute_query(query)
