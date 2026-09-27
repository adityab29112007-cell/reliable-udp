import os


class FileManager:

    def __init__(self, output_directory="received"):
        self.output_directory = output_directory

        os.makedirs(
            self.output_directory,
            exist_ok=True
        )

    def save_file(self, filename, chunks):

        file_path = os.path.join(
            self.output_directory,
            filename
        )

        with open(file_path, "wb") as file:
            for chunk in chunks:
                file.write(chunk)

        return file_path