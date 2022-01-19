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
  parser.add_argument('-d', '--debug', action='store_true', help='Use pdb to debug Neo4j responses')
  parser.add_argument('-nc', '--no-count', action='store_true', help='Disable count for progress bar')
  parser.add_argument('--count', type=int, help='Number of packets in the pcap (optional)')
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
    if args.debug:
        n4j.debug = True
    if 'ignore' in args:
        ws.ignore.append(args.ignore)
    if args.no_count:
        ws.do_count = False
    if args.count:
        ws.count = args.count
    ws.upload_to_neo4j(n4j)

if __name__=='__main__':
    main()
