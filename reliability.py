class ReliabilityManager:

    def __init__(self):

        self.received_sequences = set()
        self.chunks = {}

    def receive_packet(self, sequence_number, data):

        # Check for duplicate
        if sequence_number in self.received_sequences:

            return "duplicate"

        # Store sequence number
        self.received_sequences.add(sequence_number)

        # Store data using sequence number
        self.chunks[sequence_number] = data

        return "new"

    def get_missing_sequences(self):

        if not self.received_sequences:
            return []

        maximum = max(self.received_sequences)

        missing = []

        for sequence_number in range(1, maximum + 1):

            if sequence_number not in self.received_sequences:

                missing.append(sequence_number)

        return missing

    def get_chunks(self):

        return self.chunks

    def get_received_count(self):

        return len(self.received_sequences)