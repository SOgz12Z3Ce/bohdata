import os
import json

from .boh_data import BohData

class UnexpectedEncoding(Exception):
    """Unexpected encoding format. Raised when trying to read a file that is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE."""
    def __init__(self, message):
        super().__init__(message)

def read(target: str, type: str) -> BohData:
    """
    Read the game file(s) and convert them to BohData.

    Args:
        target (str): The file(s) path or root directory path.
        type (str): The type of file(s):
            - 'meta': Usual file.
            - 'zh': Localization file.
            - 'unknown': Unknown type file.

    Returns:
        BohData: The game data from the file(s).
    """
    if os.path.isdir(target):
        res = BohData(type, {})
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.json'):
                    res = res + read(os.path.join(root, file), type)
        return res

    encodings = ['utf-8', 'utf-8-sig', 'utf-16-le']  # Common encodings for A·K
    # Attempt to open the file
    content = ''
    for encoding in encodings:
        try:
            with open(target, 'r', encoding=encoding) as file:
                content = file.read()
                break
        except UnicodeDecodeError:
            continue
    
    if content == '':
    	# Failed to open the file
        raise UnexpectedEncoding(f'"{target}" is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE.')

    # Remove BOM character
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Load the file as JSON
    try:
        data = BohData(type, json.loads(content))
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(
            f'Error parsing "{target}": {error.msg}\nTip: Check A·K\'s JSON file, which may contain errors.\nPos', 
            error.doc, 
            error.pos
        ) from error

    return data

def check(dir: str) -> list[str]:
    """
    Check the game file(s).

    Args:
        dir (str): The root directory path of game file(s).

    Returns:
        list[str]: invalid JSON file path(s).
    """
    if os.path.isdir(dir):
        res = []
        for root, _, files in os.walk(dir):
            for file in files:
                if not file.endswith('.json'):
                    continue
                path = os.path.join(root, file)
                try:
                    read(path, 'unknown')
                except json.decoder.JSONDecodeError:
                    res.append(path)
        return res