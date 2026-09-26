import os


class FileManager:

    def __init__(self, output_directory="received"):

        self.output_directory = output_directory

        # Create received folder
        os.makedirs(
            self.output_directory,
            exist_ok=True
        )

    def save_file(self, filename, chunks):

        output_path = os.path.join(
            self.output_directory,
            filename
        )

        # Write chunks in sequence-number order
        with open(output_path, "wb") as file:

            for sequence_number in sorted(chunks.keys()):

                file.write(
                    chunks[sequence_number]
                )

        return output_path

    def verify_file(self, filename):

        output_path = os.path.join(
            self.output_directory,
            filename
        )

        if os.path.exists(output_path):

            return os.path.getsize(output_path) > 0

        return False