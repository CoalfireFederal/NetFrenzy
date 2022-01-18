import sys

import wireshark
import neo4j
import connection

def main():
    ws = wireshark.Wireshark(sys.argv[1])
    n4j = neo4j.Neo4j()
    conn = connection.Connection(config=sys.argv[2])
    conn.init_config()
    n4j.set_connection(conn)
    ws.upload_to_neo4j(n4j)

if __name__=='__main__':
    main()
