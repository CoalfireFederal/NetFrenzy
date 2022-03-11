import sys
import argparse

import lib.pcap as pcap
import lib.neo4j as neo4j
import lib.connection as connection

def parse_args():
  parser = argparse.ArgumentParser(description='Import a pcap into Neo4j')
  parser.add_argument('-c', '--config', type=str, help='Config json file', default='config.json')
  parser.add_argument('-p', '--pcap', type=str, help='Path to pcap file')
  parser.add_argument('-i', '--ignore', type=str, help='MAC address to ignore (like the GW which would correspond to all other IPs)')
  parser.add_argument('-d', '--debug', action='store_true', help='Use pdb to debug Neo4j responses')
  parser.add_argument('-da', '--debug-at', type=int, help='Use pdb to debug Neo4j responses at a specific iteration')
  parser.add_argument('--debug-time', action='store_true', help='Enable Neo4j time performance tracking')
  parser.add_argument('--debug-cache', action='store_true', help='Print cache stats after execution')
  parser.add_argument('-nc', '--no-count', action='store_true', help='Disable count for progress bar')
  parser.add_argument('--cache-max', type=int, help='Max cache size for each of the cache types', default=50)
  parser.add_argument('--count', type=int, help='Number of packets in the pcap (optional)')
  parser.add_argument('-r', '--reduce', action='store_true', help='Reduce information stored about connections')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()
  return args

def main():
    args = parse_args()

    if not args.pcap:
        print(f'try --help')
        return
    print(f'Filename: {args.pcap}')
    print(f'Config: {args.config}')

    pc = pcap.Pcap(args.pcap)
    n4j = neo4j.Neo4j()
    conn = connection.Connection(config=args.config)
    conn.init_config()
    n4j.set_connection(conn)
    if args.debug:
        n4j.debug = True
    if 'ignore' in args:
        pc.ignore.append(args.ignore)
    if args.no_count:
        pc.do_count = False
    if args.count:
        pc.count = args.count
    if args.debug_at:
        pc.debug_at = args.debug_at
    if args.debug_time:
        pc.debug_time = args.debug_time

    if args.debug_cache:
        pc.debug_cache = args.debug_cache
    pc.cache_max = args.cache_max
    pc.reduce = args.reduce

    pc.upload_to_neo4j(n4j)

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print('Received Ctrl-C. Exiting')
