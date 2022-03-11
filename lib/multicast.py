import ipaddress
import struct
import socket

# https://www.iana.org/assignments/multicast-addresses/multicast-addresses.xhtml

multicast_cidrs = [
    #'224.0.0/24',
    #'224.0.1/24',
    #'224.0.2.0-224.0.255.255', # 224.0/16
    #'224.1/16',
    #'224.2/26',
    #'224.3/16',
    #'224.4/16',
    #'224.5.0.0-224.251.255.255',
    #'224.252/14', # 224/8
    '224.0.0.0/8',
    '225.0.0.0/8',
    '226.0.0.0/8',
    '227.0.0.0/8',
    '228.0.0.0/8',
    '229.0.0.0/8',
    '230.0.0.0/8',
    '231.0.0.0/8',
    '233.252.0.0/14',
    '234.0.0.0/8',
    '235.0.0.0/8',
    '236.0.0.0/8',
    '237.0.0.0/8',
    '238.0.0.0/8',
    '239.0.0.0/8',
]
multicast_array = []

for cidr in multicast_cidrs:
    n = ipaddress.ip_network(cidr)
    netw = int(n.network_address)
    mask = int(n.netmask)
    multicast_array.append([cidr, netw, mask])

def ip_multicast(ip):
    ip = ipaddress.ip_address(ip)
    return ip.is_multicast

def mac_multicast(mac):
    if int(mac[1], 16) & 0x1 == 0x01:
        return True
    return False
