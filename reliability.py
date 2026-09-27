class ReliabilityManager:

    def __init__(self):
        self.received_sequences = set()
        self.chunks = {}

    def receive_packet(self, sequence_number, data):
        # Check for duplicate packet
        if sequence_number in self.received_sequences:
            return "duplicate"

        # Store packet
        self.received_sequences.add(sequence_number)
        self.chunks[sequence_number] = data

        return "received"

    def get_ordered_chunks(self):
        return [
            self.chunks[sequence]
            for sequence in sorted(self.chunks)
        ]

    def get_missing_sequences(self):
        if not self.received_sequences:
            return []

        maximum = max(self.received_sequences)

        return [
            sequence
            for sequence in range(maximum + 1)
            if sequence not in self.received_sequences
        ]