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

            neo4j.new_node('IP', f'{{name: "{ip_src}"}}')
            neo4j.new_node('IP', f'{{name: "{ip_dst}"}}')
            props = '{'
            props += f'srcport: {port_src}, '
            props += f'dstport: {port_dst}, '
            props += f'protocol: "{proto}", '
            props += f'time: {time}, '
            props += f'length: {length}'
            props += '}'
            neo4j.new_relationship(ip_src, ip_dst, 'CONNECTED', relprops=props)

            neo4j.new_node('MAC', f'{{name: "{mac_src}"}}')
            neo4j.new_node('MAC', f'{{name: "{mac_dst}"}}')
            neo4j.new_relationship(ip_src, mac_src, 'ASSIGNED')
            neo4j.new_relationship(ip_dst, mac_dst, 'ASSIGNED')


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
