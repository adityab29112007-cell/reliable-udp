import socket
import os

from config import HOST, PORT, CHUNK_SIZE
from packet import create_packet, parse_packet

DATA = 1
ACK = 2
FIN = 3
FIN_ACK = 4

TIMEOUT = 2


def send_packet_and_wait_ack(sock, packet, sequence_number):

    while True:

        sock.sendto(packet, (HOST, PORT))

        print(
            f"Sent packet | Sequence: {sequence_number}"
        )

        sock.settimeout(TIMEOUT)

        try:

            ack_packet, address = sock.recvfrom(2048)

            packet_type, ack_sequence, _, _, _ = parse_packet(
                ack_packet
            )

            if (
                packet_type == ACK
                and ack_sequence == sequence_number
            ):

                print(
                    f"ACK received | Sequence: {ack_sequence}"
                )

                return

        except socket.timeout:

            print(
                f"Timeout! Retransmitting | "
                f"Sequence: {sequence_number}"
            )


def send_file(filename):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("=" * 45)
    print("          RELIABLE UDP FILE SENDER")
    print("=" * 45)

    print(f"File: {filename}")
    print()

    sequence_number = 0

    with open(filename, "rb") as file:

        while True:

            data = file.read(CHUNK_SIZE)

            if not data:
                break

            packet = create_packet(
                packet_type=DATA,
                sequence_number=sequence_number,
                data=data
            )

            send_packet_and_wait_ack(
                sock,
                packet,
                sequence_number
            )

            sequence_number += 1

    # Send FIN packet
    fin_packet = create_packet(
        packet_type=FIN,
        sequence_number=sequence_number,
        data=b""
    )

    sock.sendto(fin_packet, (HOST, PORT))

    print("\nFIN sent.")

    sock.settimeout(TIMEOUT)

    try:

        fin_ack_packet, address = sock.recvfrom(2048)

        packet_type, _, _, _, _ = parse_packet(
            fin_ack_packet
        )

        if packet_type == FIN_ACK:

            print("FIN_ACK received.")
            print("File transfer completed successfully.")

    except socket.timeout:

        print("FIN_ACK not received.")

    sock.close()


if __name__ == "__main__":

    filename = input("Enter file name: ")

    if not os.path.exists(filename):

        print("File not found.")

    else:

        send_file(filename)