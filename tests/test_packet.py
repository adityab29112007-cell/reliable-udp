from packet import create_packet, parse_packet


# Create test data
data = b"Hello UDP"

# Create a packet
packet = create_packet(
    packet_type=1,
    sequence_number=10,
    data=data
)

print("Packet created successfully!")
print("Packet size:", len(packet), "bytes")


# Parse the packet
result = parse_packet(packet)

print("\nParsed packet:")
print("Packet Type:", result[0])
print("Sequence Number:", result[1])
print("Data Length:", result[2])
print("Checksum:", result[3])
print("Data:", result[4])