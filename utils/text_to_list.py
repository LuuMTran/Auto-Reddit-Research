import os
def read_txt_to_list(file_path):
    """
    Reads a text file and returns a list of lines without newline characters.
    
    :param file_path: Path to the text file
    :return: List of strings (each line as an element)
    """
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read and strip newline/whitespace from each line
            lines = [line.strip() for line in file if line.strip() != ""]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied for file '{file_path}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return lines

def get_file_names(folder_path):
    try:
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        return files

    except Exception as e:
        print(f"Error: {e}")
        return []
