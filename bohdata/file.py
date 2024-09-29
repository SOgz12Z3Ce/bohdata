import json

from .boh_data import BohData

class UnexpectedEncoding(Exception):
    """Unexpected encoding format. Raised when trying to read a file that is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE."""
    def __init__(self, message):
        super().__init__(message)

def read(path):
    """
    Read the game file and convert it to JSON.

    Args:
        path (str): The file path.

    Returns:
        dict: JSON data.
    """
    encodings = ['utf-8', 'utf-8-sig', 'utf-16-le']  # Common encodings for A·K
    # Attempt to open the file
    content = ''
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as file:
                content = file.read()
                break
        except UnicodeDecodeError:
            continue
    
    # Failed to open the file
    if content == '':
        raise UnexpectedEncoding(f'"{path}" is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE.')

    # Remove BOM character
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Load the file as JSON
    try:
        data = BohData(json.loads(content))
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(
            f'Error parsing "{path}": {error.msg}\nTip: Check A·K\'s JSON file, which may contain errors.\nPos', 
            error.doc, 
            error.pos
        ) from error

    return data