import socket

from config import HOST, PORT, BUFFER_SIZE
from packet import parse_packet, verify_checksum, create_packet
from reliability import ReliabilityManager
from file_manager import FileManager

DATA = 1
ACK = 2
FIN = 3
FIN_ACK = 4


def create_ack(sequence_number):

    return create_packet(
        packet_type=ACK,
        sequence_number=sequence_number,
        data=b""
    )


def create_fin_ack():

    return create_packet(
        packet_type=FIN_ACK,
        sequence_number=0,
        data=b""
    )


def start_receiver():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((HOST, PORT))

    reliability = ReliabilityManager()
    file_manager = FileManager()

    print("=" * 45)
    print("          RELIABLE UDP RECEIVER")
    print("=" * 45)
    print(f"Listening on {HOST}:{PORT}")
    print("Waiting for packets...\n")

    while True:

        packet, address = sock.recvfrom(BUFFER_SIZE)

        packet_type, sequence_number, data_length, checksum, data = parse_packet(
            packet
        )

        # DATA packet
        if packet_type == DATA:

            print(
                f"Received DATA | "
                f"Sequence: {sequence_number} | "
                f"Size: {data_length} bytes"
            )

            # Verify checksum
            if not verify_checksum(data, checksum):

                print(
                    f"Checksum error | "
                    f"Sequence: {sequence_number}"
                )

                continue

            result = reliability.receive_packet(
                sequence_number,
                data
            )

            # Send ACK even for duplicate packets
            ack_packet = create_ack(sequence_number)

            sock.sendto(
                ack_packet,
                address
            )

            if result == "duplicate":

                print(
                    f"Duplicate packet | "
                    f"Sequence: {sequence_number}"
                )

            else:

                print(
                    f"ACK sent | "
                    f"Sequence: {sequence_number}"
                )

        # FIN packet
        elif packet_type == FIN:

            print("\nFIN received.")
            print("Transfer finished.")

            ordered_chunks = reliability.get_ordered_chunks()

            filename = "received_file"

            file_path = file_manager.save_file(
                filename,
                ordered_chunks
            )

            print(f"File saved to: {file_path}")

            fin_ack = create_fin_ack()

            sock.sendto(
                fin_ack,
                address
            )

            print("FIN_ACK sent.")

            break

    sock.close()

    print("\nReceiver stopped.")


if __name__ == "__main__":
    start_receiver()