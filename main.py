import sys
import argparse

import wireshark
import neo4j
import connection

def parse_args():
  parser = argparse.ArgumentParser(description='Import a pcap into Neo4j')
  parser.add_argument('-c', '--config', type=str, help='Config json file')
  parser.add_argument('-p', '--pcap', type=str, help='Path to pcap file')
  parser.add_argument('-i', '--ignore', type=str, help='MAC address to ignore (like the GW which would correspond to all other IPs)')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()
  return args

def main():
    args = parse_args()

    ws = wireshark.Wireshark(args.pcap)
    n4j = neo4j.Neo4j()
    conn = connection.Connection(config=args.config)
    conn.init_config()
    n4j.set_connection(conn)
    if 'ignore' in args:
        ws.ignore.append(args.ignore)
    ws.upload_to_neo4j(n4j)

if __name__=='__main__':
    main()
