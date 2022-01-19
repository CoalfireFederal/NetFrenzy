import pyshark
import neo4j
import tqdm

class Wireshark:
    def __init__(self, pcap_filename, keep_packets=False):
        self.filename = pcap_filename
        self.cap = pyshark.FileCapture(self.filename, keep_packets=keep_packets)
        self.ignore = []
        self.count = None
        self.do_count = True
        self.debug_at = -2

    def upload_to_neo4j(self, neo4j):
        if self.do_count and self.count is None:
            print('Counting packets in pcap. Takes approx 1ms/packet')
            self.count = 0
            for c in self.cap:
                self.count += 1
        cap_iter = None
        if self.do_count or self.count:
            cap_iter = tqdm.tqdm(self.cap, total=self.count)
        else:
            cap_iter = tqdm.tqdm(self.cap)

        debug_count = 0
        for packet in cap_iter:
            if debug_count == self.debug_at + 1:
                neo4j.debug = True
            elif debug_count > 0 and debug_count != self.debug_at:
                neo4j.debug = False

            proto = get_protocol(packet)
            time = get_time(packet)
            length = get_length(packet)
            mac_src, mac_dst = get_macs(packet)
            ip_src, ip_dst = get_ips(packet)
            port_src, port_dst = get_ports(packet)
            oui_src, oui_dst = get_oui(packet)
            service, service_layer = get_service(packet)

            # Create/merge nodes for the IP addresses
            if ip_src is not None:
                neo4j.new_node('IP', f'{{name: "{ip_src}"}}')
            if ip_src is not None:
                neo4j.new_node('IP', f'{{name: "{ip_dst}"}}')

            # Create/merge nodes for the MAC addresses
            neo4j.new_node('MAC', f'{{name: "{mac_src}", manufacturer: "{oui_src}"}}')
            neo4j.new_node('MAC', f'{{name: "{mac_dst}", manufacturer: "{oui_dst}"}}')

            # Assign the IP addresses to the MAC addresses
            if mac_src not in self.ignore and ip_src is not None:
                neo4j.new_relationship(ip_src, mac_src, 'ASSIGNED')
            if mac_dst not in self.ignore and ip_dst is not None:
                neo4j.new_relationship(ip_dst, mac_dst, 'ASSIGNED')

            # Create or update the connection relationship for the packet
            if None not in (ip_src, ip_dst):
                # Create a connection between IP addresses
                create_connection(neo4j, ip_src, ip_dst, port_dst, proto, time, length, service, service_layer)
            else:
                # Create a connection between MAC addresses
                create_connection_mac(neo4j, mac_src, mac_dst, proto, time, length, service, service_layer)

            debug_count += 1

def create_connection(neo4j, ip_src, ip_dst, port_dst, proto, time, length, service, service_layer):
    if port_dst is None:
        port_dst = -1

    query = f'''MATCH (n:IP {{name: "{ip_src}"}})
MATCH (m:IP {{name: "{ip_dst}"}})
MERGE (n)-[r:CONNECTED {{name: "{port_dst}/{proto}", port: {port_dst}, protocol: "{proto}"}}]->(m)
    ON CREATE SET r += {{first_seen: {time}, last_seen: {time}, data_size: {length}, service: "{service}", service_layer: {service_layer}, count: 1}}
    ON MATCH SET r += {{last_seen: {time}, data_size: r.data_size+{length}, count: r.count+1}}
return r'''
    neo4j.raw_query(query)
    query = f'''MATCH (n:IP {{name: "{ip_src}"}})
MATCH (m:IP {{name: "{ip_dst}"}})
MERGE (n)-[r:CONNECTED {{name: "{port_dst}/{proto}", port: {port_dst}, protocol: "{proto}"}}]->(m)
    SET r.service = (CASE WHEN {service_layer} > r.service_layer THEN "{service}" ELSE r.service END)
    SET r.service_layer = (CASE WHEN {service_layer} > r.service_layer THEN "{service_layer}" ELSE r.service_layer END)
return r.service'''
    neo4j.raw_query(query)

def create_connection_mac(neo4j, mac_src, mac_dst, proto, time, length, service, service_layer):
    query = f'''MATCH (n:MAC {{name: "{mac_src}"}})
MATCH (m:MAC {{name: "{mac_dst}"}})
MERGE (n)-[r:CONNECTED {{name: "{proto}", protocol: "{proto}"}}]->(m)
    ON CREATE SET r += {{first_seen: {time}, last_seen: {time}, data_size: {length}, service: "{service}", service_layer: {service_layer}, count: 1}}
    ON MATCH SET r += {{last_seen: {time}, data_size: r.data_size+{length}, count: r.count+1}}
return r'''
    neo4j.raw_query(query)
    query = f'''MATCH (n:MAC {{name: "{mac_src}"}})
MATCH (m:MAC {{name: "{mac_dst}"}})
MERGE (n)-[r:CONNECTED {{name: "{proto}", protocol: "{proto}"}}]->(m)
    SET r.service = (CASE WHEN {service_layer} > r.service_layer THEN "{service}" ELSE r.service END)
    SET r.service_layer = (CASE WHEN {service_layer} > r.service_layer THEN "{service_layer}" ELSE r.service_layer END)
return r.service'''
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
    if 'ip' in packet:
        # eth -> ip -> ???
        return packet.layers[2].layer_name
    else:
        # eth -> ???
        return packet.layers[1].layer_name

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

def get_oui(packet):
    oui_src = None
    if 'eth' in packet and 'src_oui_resolved' in packet.eth.field_names:
        oui_src = packet.eth.src_oui_resolved
    oui_dst = None
    if 'eth' in packet and 'dst_oui_resolved' in packet.eth.field_names:
        oui_dst = packet.eth.dst_oui_resolved
    return oui_src, oui_dst

def get_service(packet):
    # What could potentially have many other formats in lower layers
    for service in ('http', 'https', 'ftp'):
        if service in packet:
            return service, 999

    '''
    Some services reported by Wireshark/pyshark need to be ignored,
    like this first example 'data-text-lines' which is a layer lower
    than HTTP (the HTML itself) but we don't care about that really
    '''
    ignore = ('data-text-lines', 'data', 'mime_multipart')
    for l in range(-1, 0 - len(packet.layers), -1):
        if packet.layers[l].layer_name not in ignore:
            return packet.layers[l].layer_name, l+len(packet.layers)
