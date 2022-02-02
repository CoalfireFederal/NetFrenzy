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
        self.commit = self.commit.replace('localhost', self.connection.ip)
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
            print(f'Response:\t{resp.json()}')
            raise

    def nuke_all_data(self):
        query = 'MATCH (n) DETACH DELETE n'
        return self.execute_query(query)
    
    def create_node(self, label, name, properties=None):
        if properties is None:
            properties = {}
        if name is None:
            return
        if 'name' not in properties:
            properties['name'] = name
        prop = '{'
        for k in properties:
            prop += f'{k}: '
            if properties[k] is None or properties[k] == 'None':
                # Cannot merge on null value, so do not include it at all
                prop = prop.replace(f'{k}: ', '')
            elif type(properties[k]) == str:
                prop += f'"{properties[k]}", '
            elif type(properties[k]) == int:
                prop += f'{properties[k]}, '
            elif type(properties[k]) == bool:
                prop += f'{str(properties[k]).lower()}, '
            else:
                # Not sure what would fall into this else case
                prop += f'"{properties[k]}", '
        prop = prop[:-2] # cut off trailing ', '
        prop += '}'
        query = f'MERGE (n:{label} {prop}) RETURN id(n)'
        return self.execute_query(query)

    '''
    Deprecated. Use create_node
    '''
    def new_node(self, label, properties):
        query = f'MERGE (n:{label} {properties}) RETURN id(n)'
        return self.execute_query(query)

    def new_node_dup(self, label, properties):
        query = f'CREATE (n:{label} {properties}) RETURN id(n)'
        return self.execute_query(query)

    def new_relationship(self, name_a, name_b, reltype, relprops=''):
        query = f'''MATCH
    (a {{name: "{name_a}"}})
WITH a
MATCH
    (b {{name: "{name_b}"}})
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
