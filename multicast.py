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

def is_multicast(ip):
    a = struct.unpack('!I', socket.inet_aton(ip))[0]
    for m in multicast_array:
        #print(f'{ip}, {m}')
        if (a & m[2]) == m[1]:
            #print('is_multicast: True')
            return True
    return False
