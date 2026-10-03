import socket
import random
import time

from packet import parse_packet
from statistics import TransferStatistics


LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 5001

RECEIVER_HOST = "127.0.0.1"
RECEIVER_PORT = 5000

PACKET_LOSS = 0.10
DELAY = 0.0
CORRUPTION = 0.0

BUFFER_SIZE = 2048

DATA = 1
ACK = 2
FIN = 3
FIN_ACK = 4


class NetworkSimulator:

    def __init__(self):

        self.statistics = TransferStatistics()

        self.statistics.start_timer()

    def transmit(self, packet):

        # Identify packet type
        try:

            packet_type, _, _, _, _ = parse_packet(packet)

        except Exception:

            return None

        # -------------------------
        # Count packet direction
        # -------------------------

        if packet_type == DATA or packet_type == FIN:

            self.statistics.data_packets_sent += 1

        elif packet_type == ACK or packet_type == FIN_ACK:

            self.statistics.ack_packets_sent += 1

        # -------------------------
        # Packet loss
        # -------------------------

        if random.random() < PACKET_LOSS:

            self.statistics.packets_lost += 1

            print(
                f"NETWORK: Packet lost | "
                f"Type: {packet_type}"
            )

            return None

        # -------------------------
        # Network delay
        # -------------------------

        if DELAY > 0:

            time.sleep(DELAY)

        # -------------------------
        # Packet corruption
        # -------------------------

        if random.random() < CORRUPTION:

            packet = bytearray(packet)

            if len(packet) > 13:

                position = random.randint(
                    13,
                    len(packet) - 1
                )

                packet[position] ^= 255

            packet = bytes(packet)

            self.statistics.packets_corrupted += 1

            print(
                f"NETWORK: Packet corrupted | "
                f"Type: {packet_type}"
            )

        return packet

    def print_statistics(self):

        self.statistics.stop_timer()

        self.statistics.print_statistics()


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

    print("=" * 50)
    print("             UDP NETWORK SIMULATOR")
    print("=" * 50)

    print(
        f"Listening on : "
        f"{LISTEN_HOST}:{LISTEN_PORT}"
    )

    print(
        f"Receiver     : "
        f"{RECEIVER_HOST}:{RECEIVER_PORT}"
    )

    print(
        f"Packet Loss  : "
        f"{PACKET_LOSS * 100}%"
    )

    print(
        f"Delay        : "
        f"{DELAY * 1000} ms"
    )

    print(
        f"Corruption   : "
        f"{CORRUPTION * 100}%"
    )

    print("\nNetwork simulator running...\n")

    try:

        while True:

            packet, source_address = sock.recvfrom(
                BUFFER_SIZE
            )

            # -------------------------
            # Packet from sender
            # -------------------------

            if source_address != receiver_address:

                sender_address = source_address

                result = simulator.transmit(packet)

                if result is not None:

                    sock.sendto(
                        result,
                        receiver_address
                    )

            # -------------------------
            # Packet from receiver
            # -------------------------

            else:

                if sender_address is not None:

                    result = simulator.transmit(packet)

                    if result is not None:

                        sock.sendto(
                            result,
                            sender_address
                        )

    except KeyboardInterrupt:

        print("\nNetwork simulator stopped.")

        simulator.print_statistics()

    finally:

        sock.close()


if __name__ == "__main__":
    start_network()