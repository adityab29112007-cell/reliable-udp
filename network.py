import socket
import random
import time

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 5001

RECEIVER_HOST = "127.0.0.1"
RECEIVER_PORT = 5000

PACKET_LOSS = 0.20
DELAY = 0.0
CORRUPTION = 0.0

BUFFER_SIZE = 2048


class NetworkSimulator:

    def __init__(self):
        self.packets_forwarded = 0
        self.packets_lost = 0
        self.packets_corrupted = 0

    def transmit(self, packet):

        # Simulate packet loss
        if random.random() < PACKET_LOSS:

            self.packets_lost += 1
            print("NETWORK: Packet lost")

            return None

        # Simulate delay
        if DELAY > 0:
            time.sleep(DELAY)

        # Simulate corruption
        if random.random() < CORRUPTION:

            packet = bytearray(packet)

            if len(packet) > 13:

                position = random.randint(
                    13,
                    len(packet) - 1
                )

                packet[position] ^= 255

            packet = bytes(packet)

            self.packets_corrupted += 1

            print("NETWORK: Packet corrupted")

        self.packets_forwarded += 1

        return packet


def start_network():

    simulator = NetworkSimulator()

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.bind(
        (LISTEN_HOST, LISTEN_PORT)
    )

    receiver_address = (
        RECEIVER_HOST,
        RECEIVER_PORT
    )

    sender_address = None

    print("=" * 45)
    print("        UDP NETWORK SIMULATOR")
    print("=" * 45)
    print(f"Listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"Forwarding to {RECEIVER_HOST}:{RECEIVER_PORT}")
    print(f"Packet Loss : {PACKET_LOSS * 100}%")
    print(f"Delay       : {DELAY * 1000} ms")
    print(f"Corruption  : {CORRUPTION * 100}%")
    print()

    while True:

        packet, source_address = sock.recvfrom(
            BUFFER_SIZE
        )

        # Packet from sender
        if source_address != receiver_address:

            sender_address = source_address

            result = simulator.transmit(packet)

            if result is not None:

                sock.sendto(
                    result,
                    receiver_address
                )

        # ACK/response from receiver
        else:

            if sender_address is not None:

                result = simulator.transmit(packet)

                if result is not None:

                    sock.sendto(
                        result,
                        sender_address
                    )


if __name__ == "__main__":
    start_network()