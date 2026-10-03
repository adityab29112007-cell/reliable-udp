import time


class TransferStatistics:

    def __init__(self):

        self.data_packets_sent = 0
        self.data_packets_received = 0

        self.ack_packets_sent = 0
        self.ack_packets_received = 0

        self.packets_lost = 0
        self.packets_corrupted = 0

        self.retransmissions = 0

        self.start_time = None
        self.end_time = None

    def start_timer(self):

        self.start_time = time.time()

    def stop_timer(self):

        self.end_time = time.time()

    def transfer_time(self):

        if self.start_time is None or self.end_time is None:

            return 0

        return self.end_time - self.start_time

    def print_statistics(self):

        print("\n")
        print("=" * 50)
        print("             TRANSFER STATISTICS")
        print("=" * 50)

        print(
            f"DATA packets sent       : "
            f"{self.data_packets_sent}"
        )

        print(
            f"DATA packets received   : "
            f"{self.data_packets_received}"
        )

        print(
            f"ACK packets sent        : "
            f"{self.ack_packets_sent}"
        )

        print(
            f"ACK packets received    : "
            f"{self.ack_packets_received}"
        )

        print(
            f"Packets lost            : "
            f"{self.packets_lost}"
        )

        print(
            f"Packets corrupted       : "
            f"{self.packets_corrupted}"
        )

        print(
            f"Retransmissions         : "
            f"{self.retransmissions}"
        )

        print(
            f"Transfer time           : "
            f"{self.transfer_time():.2f} seconds"
        )

        print("=" * 50)