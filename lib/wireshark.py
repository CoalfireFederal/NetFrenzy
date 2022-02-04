from collections import deque
import time
import tqdm

import pyshark
from OuiLookup import OuiLookup

from . import multicast

class Wireshark:
    def __init__(self, pcap_filename, keep_packets=False):
        self.filename = pcap_filename
        self.cap = pyshark.FileCapture(self.filename, keep_packets=keep_packets)
        self.ignore = []
        self.count = None
        self.do_count = True
        self.debug_at = -2
        self.debug_time = False
        self._time_start = 0
        self.debug_time_neo4j = 0
        self.debug_cache = False
        self.cache = {}
        self.cache_max = 0
        self.cache_init()
        self.preprocess = False

    def ingest(self, neo4j):
        if self.preprocess:
            self.preprocess_to_neo4j(neo4j)
        else:
            self.upload_to_neo4j(neo4j)

    def preprocess_to_neo4j(self, neo4j):
        nodes = {'IP': [], 'MAC': [], 'SSID': []}
        edges = {'CONNECTED': [], 'ASSIGNED': [], 'ADVERTISES': []}
        
        # Count packets for process bar
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
        
        for packet in cap_iter:
            proto = get_protocol(packet)
            time = get_time(packet)
            length = get_length(packet)
            macs = get_macs(packet, cached=self.is_cached)
            ip_src, ip_dst = get_ips(packet)
            port_src, port_dst = get_ports(packet)
            service, service_layer = get_service(packet)
            ssid = get_ssid(packet)
            
            # Is MERGE on a Python array faster than a MERGE in Neo4j?
            # IP nodes and MAC nodes and (:IP)-[:CONNECTED]-(:IP) and (:IP)-[:ASSIGNED]-(:MAC)
            if None not in [ip_src, ip_dst]:
                # IP nodes
                node = {'name': ip_src, 'multicast': multicast.ip_multicast(ip_src)}
                if node not in nodes['IP']:
                    nodes['IP'].append(node)
                node = {'name': ip_dst, 'multicast': multicast.ip_multicast(ip_dst)}
                if node not in nodes['IP']:
                    nodes['IP'].append(node)
                
                # MAC nodes
                for k, mac in macs.items():
                    if mac['mac'] is not None:
                        node = {'name': mac['mac'], 'manufacturer': mac['oui'], 'multicast': multicast.mac_multicast(mac['mac'])}
                        if node not in nodes['MAC']:
                            nodes['MAC'].append(node)

                # (:IP)-[:CONNECTED]-(:IP)
                found_edge = None
                for edge in edges['CONNECTED']:
                    if match_IP_edge(edge, ip_src, ip_dst, proto, port_dst):
                        found_edge = edge
                if found_edge:
                    found_edge['properties']['data'] += length
                    if found_edge['properties']['first_seen'] > time:
                        found_edge['properties']['first_seen'] = time
                    if found_edge['properties']['last_seen'] < time:
                        found_edge['properties']['last_seen'] = time
                    if found_edge['properties']['service_layer'] < service_layer:
                        found_edge['properties']['service'] = service
                else:
                    found_edge = create_IP_edge(ip_src, ip_dst, proto, port_dst, time, length, service, service_layer)
                    edges['CONNECTED'].append(found_edge)
                
                # (:IP)-[:ASSIGNED]-(:MAC)
                edge = {'mac': macs['src']['mac'], 'ip': ip_src} 
                if edge not in edges['ASSIGNED']:
                    edges['ASSIGNED'].append(edge)
                edge = {'mac': macs['src']['mac'], 'ip': ip_dst} 
                if edge not in edges['ASSIGNED']:
                    edges['ASSIGNED'].append(edge)

            # (:MAC)-[:CONNECTED]-(:MAC)
            elif None not in (macs['src']['mac'], macs['dst']['mac'], macs['tra']['mac'], macs['rec']['mac']):
                # This is for wlan frames that have ra and ta
                # We are connecting the sender to transmitter, receiver to destination

                # self.create_connection_mac(neo4j, macs['src']['mac'], macs['tra']['mac'], proto, time, length, service, service_layer)
                found_edge = None
                for edge in edges['CONNECTED']:
                    if match_MAC_edge(edge, macs['src']['mac'], macs['tra']['mac'], proto):
                        found_edge = edge
                if found_edge:
                    found_edge['properties']['data'] += length
                    if found_edge['properties']['first_seen'] > time:
                        found_edge['properties']['first_seen'] = time
                    if found_edge['properties']['last_seen'] < time:
                        found_edge['properties']['last_seen'] = time
                    if found_edge['properties']['service_layer'] < service_layer:
                        found_edge['properties']['service'] = service
                else:
                    found_edge = create_MAC_edge(macs['src']['mac'], macs['tra']['mac'], proto, time, length, service, service_layer)
                    edges['CONNECTED'].append(found_edge)
                
                # self.create_connection_mac(neo4j, macs['rec']['mac'], macs['dst']['mac'], proto, time, length, service, service_layer)
                found_edge = None
                for edge in edges['CONNECTED']:
                    if match_edge(edge, macs['rec']['mac'], macs['dst']['mac'], proto):
                        found_edge = edge
                if found_edge:
                    found_edge['properties']['data'] += length
                    if found_edge['properties']['first_seen'] > time:
                        found_edge['properties']['first_seen'] = time
                    if found_edge['properties']['last_seen'] < time:
                        found_edge['properties']['last_seen'] = time
                    if found_edge['properties']['service_layer'] < service_layer:
                        found_edge['properties']['service'] = service
                else:
                    found_edge = create_MAC_edge(macs['rec']['mac'], macs['dst']['mac'], proto, time, length, service, service_layer)
                    edges['CONNECTED'].append(found_edge)

            # (:MAC)-[:CONNECTED]-(:MAC)
            elif None not in (macs['src']['mac'], macs['dst']['mac']):
                # (:MAC)-[:CONNECTED]-(:MAC)
                found_edge = None
                for edge in edges['CONNECTED']:
                    if match_MAC_edge(edge, macs['src']['mac'], macs['dst']['mac'], proto):
                        found_edge = edge
                if found_edge:
                    found_edge['properties']['data'] += length
                    if found_edge['properties']['first_seen'] > time:
                        found_edge['properties']['first_seen'] = time
                    if found_edge['properties']['last_seen'] < time:
                        found_edge['properties']['last_seen'] = time
                    if found_edge['properties']['service_layer'] < service_layer:
                        found_edge['properties']['service'] = service
                else:
                    found_edge = create_MAC_edge(macs['src']['mac'], macs['dst']['mac'], proto, time, length, service, service_layer)
                    edges['CONNECTED'].append(found_edge)

            # SSID nodes and (:MAC)-[:ADVERTISES]-(:SSID)
            if ssid is not None:
                # SSID nodes
                edge = {'name': ssid}
                if edge not in nodes['SSID']:
                    nodes['SSID'].append(edge)
                
                # (:MAC)-[:ADVERTISES]-(:SSID)
                edge = {'src': macs['src']['mac'], 'dst': ssid, 'properties': []} 
                if edge not in edges['ADVERTISES']:
                    edges['ADVERTISES'].append(edge)

        # This code is after the packet loop

        # nodes = {'IP': [], 'MAC': [], 'SSID': []}
        # edges = {'CONNECTED': [], 'ASSIGNED': [], 'ADVERTISES': []}

        # Create all nodes in Neo4j
        for k, v in nodes.items():
            print(f'Debug: {k} length: {len(v)}')
            for node in v:
                neo4j.create_node(k, '', properties=node)

        for k, v in edges.items():
            print(f'Debug: {k} length: {len(v)}')
            for edge in v:
                neo4j.create_relationship(k, edge['src'], edge['dst'], properties=edge['properties'])

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
            macs = get_macs(packet, cached=self.is_cached)
            ip_src, ip_dst = get_ips(packet)
            port_src, port_dst = get_ports(packet)
            service, service_layer = get_service(packet)
            ssid = get_ssid(packet)

            # Create/merge nodes for the IP addresses
            self.create_ip(neo4j, ip_src)
            self.create_ip(neo4j, ip_dst)

            # Create/merge nodes for the MAC addresses
            self.create_macs(neo4j, macs)

            # Assign the IP addresses to the MAC addresses
            self.create_mac_assignment(neo4j, ip_src, macs['src']['mac'])
            self.create_mac_assignment(neo4j, ip_dst, macs['dst']['mac'])

            # Create or update the connection relationship for the packet
            if None not in (ip_src, ip_dst):
                # Create a connection between IP addresses
                self.create_connection(neo4j, ip_src, ip_dst, port_dst, proto, time, length, service, service_layer)
            elif None not in (macs['src']['mac'], macs['dst']['mac']):
                # Create a connection between MAC addresses
                self.create_connection_mac(neo4j, macs['src']['mac'], macs['dst']['mac'], proto, time, length, service, service_layer)
            if None not in (macs['src']['mac'], macs['dst']['mac'], macs['tra']['mac'], macs['rec']['mac']):
                # Create a connection between MAC addresses
                # This is for wlan frames that have ra and ta
                # We are connecting the sender to transmitter, receiver to destination
                self.create_connection_mac(neo4j, macs['src']['mac'], macs['tra']['mac'], proto, time, length, service, service_layer)
                self.create_connection_mac(neo4j, macs['rec']['mac'], macs['dst']['mac'], proto, time, length, service, service_layer)

            self.create_ssid(neo4j, ssid, macs['src']['mac'])

            debug_count += 1
        self.print_debug_time()
        self.print_cache_stats()

    def debug_time_start(self):
        if self.debug_time:
            self._time_start = time.time()

    def debug_time_end(self):
        if self.debug_time:
            _time_end = time.time()
            self.debug_time_neo4j += _time_end - self._time_start

    def print_debug_time(self):
        if self.debug_time:
            print(f'Time in Neo4j: {self.debug_time_neo4j}')

    def cache_init(self):
        self.cache = {
            'IP': {
                'cache': deque([]),
                'hits': 0,
                'misses': 0,
            },
            'MAC': {
                'cache': deque([]),
                'hits': 0,
                'misses': 0,
            },
            'ASSIGN': {
                'cache': deque([]),
                'hits': 0,
                'misses': 0,
            },
            'SSID': {
                'cache': deque([]),
                'hits': 0,
                'misses': 0,
            },
            'ADVERTISE': {
                'cache': deque([]),
                'hits': 0,
                'misses': 0,
            },
        }
        self.cache_max = 50

    def print_cache_stats(self):
        if not self.debug_cache:
            return
        keys = ['IP', 'MAC', 'ASSIGN', 'SSID', 'ADVERTISE']
        print(f'cache_max: {self.cache_max}')
        for k in keys:
            print(f'cache[{k}]:')
            print(f'\tHits:\t{self.cache[k]["hits"]}')
            print(f'\tMiss:\t{self.cache[k]["misses"]}')
            print(f'\tUse:\t{len(self.cache[k]["cache"])}/{self.cache_max}')

    def cached(self, value, _type):
        is_cached = False
        if value in self.cache[_type]['cache']:
            is_cached = True
            self.cache[_type]['hits'] += 1
        else:
            self.cache[_type]['misses'] += 1
            self.cache[_type]['cache'].append(value)
            if len(self.cache[_type]['cache']) > self.cache_max:
                self.cache[_type]['cache'].popleft()
        return is_cached

    # Like cached(), but doesn't update cache
    def is_cached(self, value, _type):
        cached = False
        if value in self.cache[_type]['cache']:
            cached = True
            self.cache[_type]['hits'] += 1
        else:
            self.cache[_type]['misses'] += 1
        return cached
    
    '''
    Deprecated, creates too many edges which probably aren't useful anyway
    '''
    def create_port_relationship(self, neo4j, ip_src, ip_dst, port_src, port_dst, proto, time, length):
        props = '{'
        props += f'srcport: {port_src}, '
        props += f'dstport: {port_dst}, '
        props += f'protocol: "{proto}", '
        props += f'time: {time}, '
        props += f'length: {length}'
        props += '}'
        self.debug_time_start()
        neo4j.new_relationship(ip_src, ip_dst, 'CONNECTED', relprops=props)
        self.debug_time_end()

    def create_ip(self, neo4j, ip):
        if ip is None:
            return
        if self.cached(ip, 'IP'):
            return
        properties = {}
        properties['multicast'] = multicast.ip_multicast(ip)
        self.debug_time_start()
        neo4j.create_node('IP', ip, properties=properties)
        self.debug_time_end()
    
    def create_macs(self, neo4j, macs):
        if macs is None:
            return
        for k in macs:
            mac = macs[k]['mac']
            if mac is None:
                continue
            if self.cached(mac, 'MAC'):
                continue
            oui = macs[k]['oui']
            properties = {}
            properties['manufacturer'] = oui
            properties['multicast'] = multicast.mac_multicast(mac)
            self.debug_time_start()
            neo4j.create_node('MAC', mac, properties=properties)
            self.debug_time_end()
    
    def create_mac_assignment(self, neo4j, ip, mac):
        if mac not in self.ignore and ip is not None:
            if self.cached([ip, mac], 'ASSIGN'):
                return
            self.debug_time_start()
            neo4j.new_relationship(ip, mac, 'ASSIGNED')
            self.debug_time_end()
    
    def create_connection(self, neo4j, ip_src, ip_dst, port_dst, proto, time, length, service, service_layer):
        if port_dst is None:
            port_dst = -1
    
        # Create CONNECTED relationship between IPs
        query = f'''MATCH (n:IP {{name: "{ip_src}"}})
    MATCH (m:IP {{name: "{ip_dst}"}})
    MERGE (n)-[r:CONNECTED {{name: "{port_dst}/{proto}", port: {port_dst}, protocol: "{proto}"}}]->(m)
        ON CREATE
            SET r += {{first_seen: {time}, last_seen: {time}, data_size: {length}, service: "{service}", service_layer: {service_layer}, count: 1}}
        ON MATCH
            SET r.first_seen = (CASE WHEN {time} > r.first_seen THEN r.first_seen ELSE {time} END)
            SET r.last_seen = (CASE WHEN {time} < r.last_seen THEN r.last_seen ELSE {time} END)
            SET r += {{data_size: r.data_size+{length}, count: r.count+1}}
    return r'''
        self.debug_time_start()
        neo4j.raw_query(query)
        self.debug_time_end()
        # Update service for CONNECTED relationship
        query = f'''MATCH (n:IP {{name: "{ip_src}"}})
    MATCH (m:IP {{name: "{ip_dst}"}})
    MERGE (n)-[r:CONNECTED {{name: "{port_dst}/{proto}", port: {port_dst}, protocol: "{proto}"}}]->(m)
        SET r.service = (CASE WHEN {service_layer} > r.service_layer THEN "{service}" ELSE r.service END)
        SET r.service_layer = (CASE WHEN {service_layer} > r.service_layer THEN "{service_layer}" ELSE r.service_layer END)
    return r.service'''
        self.debug_time_start()
        neo4j.raw_query(query)
        self.debug_time_end()
    
    def create_connection_mac(self, neo4j, mac_src, mac_dst, proto, time, length, service, service_layer):
        # Create CONNECTED relationship between MACs
        query = f'''MATCH (n:MAC {{name: "{mac_src}"}})
    MATCH (m:MAC {{name: "{mac_dst}"}})
    MERGE (n)-[r:CONNECTED {{name: "{proto}", protocol: "{proto}"}}]->(m)
        ON CREATE
            SET r += {{first_seen: {time}, last_seen: {time}, data_size: {length}, service: "{service}", service_layer: {service_layer}, count: 1}}
        ON MATCH
            SET r.first_seen = (CASE WHEN {time} > r.first_seen THEN r.first_seen ELSE {time} END)
            SET r.last_seen = (CASE WHEN {time} < r.last_seen THEN r.last_seen ELSE {time} END)
            SET r += {{data_size: r.data_size+{length}, count: r.count+1}}
    return r'''
        self.debug_time_start()
        neo4j.raw_query(query)
        self.debug_time_end()
        # Update service for CONNECTED relationship
        query = f'''MATCH (n:MAC {{name: "{mac_src}"}})
    MATCH (m:MAC {{name: "{mac_dst}"}})
    MERGE (n)-[r:CONNECTED {{name: "{proto}", protocol: "{proto}"}}]->(m)
        SET r.service = (CASE WHEN {service_layer} > r.service_layer THEN "{service}" ELSE r.service END)
        SET r.service_layer = (CASE WHEN {service_layer} > r.service_layer THEN "{service_layer}" ELSE r.service_layer END)
    return r.service'''
        self.debug_time_start()
        neo4j.raw_query(query)
        self.debug_time_end()

    def create_ssid(self, neo4j, ssid, mac_src):
        if ssid is None:
            return
        if not self.cached(ssid, 'SSID'):
            self.debug_time_start()
            neo4j.create_node('SSID', ssid)
            self.debug_time_end()
        if mac_src is None:
            return
        if not self.cached([mac_src, ssid], 'ADVERTISE'):
            self.debug_time_start()
            neo4j.new_relationship(mac_src, ssid, 'ADVERTISES')
            self.debug_time_end()

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

def get_macs(packet, cached=None):
    macs = {}
    macs['src'] = {'mac': None, 'oui': None}
    macs['dst'] = {'mac': None, 'oui': None}
    macs['tra'] = {'mac': None, 'oui': None}
    macs['rec'] = {'mac': None, 'oui': None}

    if 'eth' in packet:
        macs['src']['mac'] = packet.eth.get_field('src')
        macs['dst']['mac'] = packet.eth.get_field('dst')
    if 'wlan' in packet:
        macs['src']['mac'] = packet.wlan.get_field('sa')
        macs['dst']['mac'] = packet.wlan.get_field('da')
        macs['tra']['mac'] = packet.wlan.get_field('ta')
        macs['rec']['mac'] = packet.wlan.get_field('ra')
        if macs['src']['mac'] == macs['tra']['mac']:
            macs['tra']['mac'] = None
        if macs['dst']['mac'] == macs['rec']['mac']:
            macs['rec']['mac'] = None
    
    for k in macs:
        if macs[k]['mac'] is not None:
            if cached is not None and cached(macs[k]['mac'], 'MAC'):
                continue
            macs[k]['oui'] = get_oui(macs[k]['mac'])

    return macs

'''
Deprecated. Use get_macs()
'''
def get_macs_old(packet):
    if 'eth' in packet:
        mac_src = packet.eth.get_field('src')
        mac_dst = packet.eth.get_field('dst')
        mac_tra = None
        mac_rec = None
    if 'wlan' in packet:
        mac_src = packet.wlan.get_field('sa')
        mac_dst = packet.wlan.get_field('da')
        mac_tra = packet.wlan.get_field('ta')
        mac_rec = packet.wlan.get_field('ra')
        if mac_src == mac_tra:
            mac_tra = None
        if mac_dst == mac_rec:
            mac_rec = None

    return mac_src, mac_dst, mac_tra, mac_rec

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

def get_oui(mac):
    try:
        for k, v in OuiLookup().query(mac)[0].items():
            return v
    except:
        pass
    return None

'''
Deprecated. Use get_oui()
'''
def get_oui_old(packet):
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
    return "unknown", 0-len(packet.layers)

def get_ssid(packet):
    # This is the Wildcard SSID.
    # It's noisy and I'm not sure what to make of it
    ignore = ('SSID: ')
    ssid = None
    if 'wlan.mgt' in packet:
        ssid = packet['wlan.mgt'].get_field('wlan_ssid')
    if ssid is not None and ssid in ignore:
        ssid = None
    return ssid

def match_IP_edge(edge, ip_src, ip_dst, proto, port_dst):
    if ip_src != edge['src']:
        return False
    if ip_dst != edge['dst']:
        return False
    if proto != edge['properties']['proto']:
        return False
    if port_dst != edge['properties']['port']:
        return False
    return True
                    
def create_IP_edge(ip_src, ip_dst, proto, port_dst, time, length, service, service_layer):
    edge = {
        'src': ip_src,
        'dst': ip_dst,
        'properties': {
            'name': f'{port_dst}/{proto}',
            'proto': proto,
            'port': port_dst,
            'first_seen': time,
            'last_seen': time,
            'data': length,
            'service': service,
            'service_layer': service_layer,
        }
    }
    return edge

def match_MAC_edge(edge, mac_src, mac_dst, proto):
    if mac_src != edge['src']:
        return False
    if mac_dst != edge['dst']:
        return False
    if proto != edge['properties']['proto']:
        return False
    return True

def create_MAC_edge(mac_src, mac_dst, proto, time, length, service, service_layer):
    edge = {
        'src': mac_src,
        'dst': mac_dst,
        'properties': {
            'name': service,
            'proto': proto,
            'first_seen': time,
            'last_seen': time,
            'data': length,
            'service': service,
            'service_layer': service_layer,
        }
    }
    return edge
