import socket

from config import HOST, PORT
from packet import create_packet


DATA = 1


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