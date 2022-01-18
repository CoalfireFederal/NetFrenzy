import pyshark
import neo4j

class Wireshark:
    def __init__(self, pcap_filename):
        self.filename = pcap_filename
        self.cap = pyshark.FileCapture(self.filename)

    def upload_to_neo4j(self, neo4j):
        for packet in self.cap:
            proto = get_protocol(packet)
            time = get_time(packet)
            length = get_length(packet)
            mac_src, mac_dst = get_macs(packet)
            ip_src, ip_dst = get_ips(packet)
            port_src, port_dst = get_ports(packet)

            # Create/merge nodes for the IP addresses
            neo4j.new_node('IP', f'{{name: "{ip_src}"}}')
            neo4j.new_node('IP', f'{{name: "{ip_dst}"}}')

            # Create/merge nodes for the MAC addresses
            neo4j.new_node('MAC', f'{{name: "{mac_src}"}}')
            neo4j.new_node('MAC', f'{{name: "{mac_dst}"}}')

            # Assign the IP addresses to the MAC addresses
            neo4j.new_relationship(ip_src, mac_src, 'ASSIGNED')
            neo4j.new_relationship(ip_dst, mac_dst, 'ASSIGNED')

            # Create a connection between IP addresses
            create_connection(neo4j, ip_src, ip_dst, port_dst, proto, time, length)

def create_connection(neo4j, ip_src, ip_dst, port_dst, proto, time, length):
    query = f'''MATCH (n:IP {{name: "{ip_src}"}})
MATCH (m:IP {{name: "{ip_dst}"}})
MERGE (n)-[r:CONNECTED {{name: "{port_dst}/{proto}", port: {port_dst}, protocol: "{proto}"}}]->(m)
    ON CREATE SET r += {{last_seen: {time}, data_size: {length}, count: 1}}
    ON MATCH SET r += {{last_seen: {time}, data_size: r.data_size+{length}, count: r.count+1}}
return r
'''
    neo4j.raw_query(query)

'''
Deprecated, creates too many edges which probably aren't useful anyway
'''
def create_port_relationship(neo4j, ip_src, ip_dst, port_src, port_dst, proto, time, length):
    props = '{'
    props += f'srcport: {port_src}, '
    props += f'dstport: {port_dst}, '
    props += f'protocol: "{proto}", '
    props += f'time: {time}, '
    props += f'length: {length}'
    props += '}'
    neo4j.new_relationship(ip_src, ip_dst, 'CONNECTED', relprops=props)

def get_protocol(packet):
    for layer in packet.layers:
        if layer.layer_name == 'udp':
            return 'udp'
        elif layer.layer_name == 'tcp':
            return 'tcp'
    return 'other'

def get_macs(packet):
    return packet.layers[0].src, packet.layers[0].dst

def get_ips(packet):
    for layer in packet.layers:
        if layer.layer_name == 'ip':
            return layer.src, layer.dst
    return None, None

def get_ports(packet):
    for layer in packet.layers:
        if layer.layer_name in ('udp', 'tcp'):
            return layer.srcport, layer.dstport
    return None, None

def get_time(packet):
    return float(packet.sniff_timestamp)

def get_length(packet):
    return int(packet.captured_length)
