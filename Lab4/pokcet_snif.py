import sys
import socket
from struct import unpack
import pprint
from hexdump import hexdump

from collections import namedtuple

# interface = sys.argv[1]
interface = 'enp7s0'
# interface = 'lo'

raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
raw_socket.setsockopt(socket.SOL_SOCKET, 25, interface.strip().encode('ascii') + b'\0')
packet_stats = {'total_number_of_packets': 0}


def extract_tcp_ip_header(packet_payload):
    ip_header = packet_payload[:20]
    ip_header = unpack('!BBHHHBBH4s4s', ip_header)

    version = ip_header[0] >> 4
    header_length = (ip_header[0] & 0xF) * 4

    ttl = ip_header[5]
    protocol = ip_header[6]

    source_addr = socket.inet_ntoa(ip_header[8])
    destination_addr = socket.inet_ntoa(ip_header[9])

    IPHeader = namedtuple(
        'IPHeader',
        (
            'version', 'header_length', 'ttl', 'protocol', 'source_addr',
            'destination_addr'
        )
    )

    return IPHeader(version, header_length, ttl, protocol, source_addr, destination_addr)


def extract_tcp_header(packet_payload, ip_header):
    tcp_header = packet_payload[ip_header.header_length:ip_header.header_length + 20]
    tcp_header = unpack('!HHLLBBHHH', tcp_header)

    TCPHeader = namedtuple(
        'TCPHeader',
        (
            'source_port', 'destination_port', 'sequence', 'ack',
            'header_length'
        )
    )

    header_length = (tcp_header[4] >> 4) * 4

    return TCPHeader(
        tcp_header[0], tcp_header[1], tcp_header[2], tcp_header[3],
        header_length)


def extract_data(packet_payload, ip_header, tcp_header):
    total_header_size = ip_header.header_length + tcp_header.header_length
    data_size = len(packet_payload) - total_header_size

    return packet_payload[total_header_size:], data_size


def receive_and_process():
    packet = raw_socket.recvfrom(65565)
    packet_payload = packet[0]

    ip_header = extract_tcp_ip_header(packet_payload)
    tcp_header = extract_tcp_header(packet_payload, ip_header)
    data, data_size = extract_data(packet_payload, ip_header, tcp_header)

    if ip_header.source_addr not in packet_stats:
        packet_stats[ip_header.source_addr] = {
            'number_of_packets': 0,
            'number_of_bytes': 0,
            'average_packet_size': 0
        }

    p_stat = packet_stats[ip_header.source_addr]
    p_stat['average_packet_size'] = (
        data_size if p_stat['number_of_packets'] == 0 else
        (p_stat['average_packet_size'] + data_size) / 2
    )
    p_stat['number_of_packets'] += 1
    p_stat['number_of_bytes'] += data_size
    packet_stats['total_number_of_packets'] += 1

    if packet_stats['total_number_of_packets'] % 1000 == 0:
        pprint.pprint(packet_stats)

    # print(ip_header)
    # print(tcp_header)

    return ip_header.source_addr, ip_header.destination_addr, ip_header.protocol, tcp_header.source_port, tcp_header.destination_port, hexdump(data, result='return')


#
# def run():
#     while True:
#         receive_and_process()
#
#
# if __name__ == '__main__':
#     try:
#         run()
#     except KeyboardInterrupt:
#         # pprint.pprint(packet_stats)
#         pass
