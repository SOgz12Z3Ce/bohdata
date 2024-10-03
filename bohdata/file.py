import os
import json

from .boh_obj import BohObj
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
        res = BohData(type, None, {})
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
        data = BohData(type, os.path.basename(target), json.loads(content))
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(
            f'Error parsing "{target}": {error.msg}\nTip: Check A·K\'s JSON file, which may contain errors.\nPos', 
            error.doc, 
            error.pos
        ) from error

    return data

def pack(dir: str) -> None:
    """
    Trans paratranz.cn JSON files into JSON files for BOH.

    Args:
        dir (str): The root directory path of para JSON files and game files. It should be like this:
            dir
            ├── core
            └── raw
    """
    def islist(obj):
        """Check if a dict is able to be transed into a list."""
        for key, _ in obj.items():
            if key.isdigit() == False:
                return False
        keys = sorted(obj.keys(), key=int)
        return all(str(i) == keys[i] for i in range(len(keys)))
    
    def tolist(obj):
        """Trans a dict and its sub-dict(s) into list(s)."""
        for key, value in obj.items():
            if isinstance(value, dict):
                obj[key] = tolist(value)
        if not islist(obj):
            return obj
        res = []
        key = '0'
        while obj.get(key) is not None:
            res.append(obj[key])
            key = str(int(key) + 1)
        return res

    def prase(output, key, translation):
        """Prase para entry into a dict."""
        if '||' not in key:
            output[key] = translation
        else:
            current_key = key.split('||')[0]
            if output.get(current_key) is None:
                output[current_key] = {}
            prase(output[current_key], key.split('||', 1)[1], translation)

    alldata = read(os.path.join(dir, 'core/'), 'meta')
    for root, _, files in os.walk(os.path.join(dir, 'raw/')):
        for fname in files:
            path = os.path.join(root, fname)
            with open(path,'r', encoding='utf-8') as file:
                entries = json.load(file)

            output = {}
            for entry in entries:
                prase(output, entry['key'], entry['translation'])
                id = entry['key'].split('||')[0]
                output[id]['id'] = id
                
                if id.lower() != id:
                    output[id.lower()] = output[id]
                    del output[id]
            tolist(output)

            relpath = os.path.relpath(path, os.path.join(dir, 'raw/')).replace('.csv', '')
            outputpath = os.path.join('./output/', relpath)

            outputdata = BohData('zh', fname.replace('.csv', ''), {})
            for id, obj in output.items():
                if alldata.map.get(id) is None:
                    print(f'Object "{id}" at "{path}" needs to be manually processed.')
                    continue
                outputdata.append(BohObj('zh', alldata.map[id].root, obj))

            os.makedirs(os.path.dirname(outputpath), exist_ok=True)
            with open(outputpath, 'w', encoding='utf-8') as file:
                file.write(json.dumps(outputdata, ensure_ascii=False))

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