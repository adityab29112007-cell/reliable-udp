import socket

from config import HOST, PORT, CHUNK_SIZE
from packet import create_packet


# Packet type
DATA = 1


def read_file_chunks(filename):
    """
    Read a file in chunks of CHUNK_SIZE bytes.
    Each chunk gets a sequence number.
    """

    with open(filename, "rb") as file:

        sequence_number = 0

        while True:

            data = file.read(CHUNK_SIZE)

            if not data:
                break

            yield sequence_number, data

            sequence_number += 1


def send_file(sock, filename):
    """
    Read a file, create UDP packets,
    and send each packet to the receiver.
    """

    print(f"\nSending file: {filename}")

    for sequence_number, data in read_file_chunks(filename):

        packet = create_packet(
            packet_type=DATA,
            sequence_number=sequence_number,
            data=data
        )

        sock.sendto(packet, (HOST, PORT))

        print(
            f"Sent file chunk | "
            f"Sequence: {sequence_number} | "
            f"Size: {len(data)} bytes"
        )

    print("File sent successfully!")


def start_sender():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sequence_number = 0

    print("=" * 40)
    print("       RELIABLE UDP SENDER")
    print("=" * 40)
    print(f"Sending to {HOST}:{PORT}")
    print()

    while True:

        message = input("Enter message: ")

        if message.lower() == "exit":
            break

        # File transfer command
        if message.startswith("file "):

            filename = message[5:].strip()

            try:
                send_file(sock, filename)

            except FileNotFoundError:
                print(f"File not found: {filename}")

            continue

        # Normal message
        data = message.encode()

        packet = create_packet(
            packet_type=DATA,
            sequence_number=sequence_number,
            data=data
        )

        sock.sendto(packet, (HOST, PORT))

        print(
            f"Sent packet | "
            f"Sequence: {sequence_number} | "
            f"Data: {message}"
        )

        sequence_number += 1

    sock.close()

    print("\nSender stopped.")


if __name__ == "__main__":
    start_sender()