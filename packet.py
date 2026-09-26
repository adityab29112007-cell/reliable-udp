import struct

# Packet header:
# Packet Type    -> 1 byte
# Sequence No.   -> 4 bytes
# Data Length    -> 4 bytes
# Checksum       -> 4 bytes

HEADER_FORMAT = "!BIII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def create_packet(packet_type, sequence_number, data, checksum=0):
    data_length = len(data)

    header = struct.pack(
        HEADER_FORMAT,
        packet_type,
        sequence_number,
        data_length,
        checksum
    )

    return header + data


def parse_packet(packet):
    header = packet[:HEADER_SIZE]
    data = packet[HEADER_SIZE:]

    packet_type, sequence_number, data_length, checksum = struct.unpack(
        HEADER_FORMAT,
        header
    )

    return (
        packet_type,
        sequence_number,
        data_length,
        checksum,
        data
    )