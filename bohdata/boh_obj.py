import os
import json

class UnexpectedBohObj(Exception):
    """Unexpected BohObj."""
    def __init__(self, message):
        super().__init__(message)

class BohObj(dict):
    """
    A class to represent a object in the game.

    Attributes:
        id (str): The ID of the object. All lowercase.
        real_id (str): The true ID from game files. Case sensitive.
        label (str): The in-game name of the object.
        type (str): The type of the object.
        root (str): The category of the object.
        meta (dict): The origin data of the object.
        zh (dict): The localization data of the object.
    
    methods:
        localizewith(loc: BohObj) -> None: Localize the object with a localization object.
        tojson(dir: str = './', forwiki: bool = False) -> None: Create a JSON file for the object in the given directory.
    """
    def __init__(self, type: str, root: str = 'unknown', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.real_id = self.get('id') or self.get('ID')
        self.id = self.real_id.lower()
        # 2024.A.2 'AGNES' from beta->live: - MODDING: IDs of entities are now completely case-insensitive for all purposes (in-game access, modifying, inheriting, localizing etc).
        # e.g.: Wooden
        self.label = self.get('label') or self.get('Label')
        self.type = type
        self.root = root
        if type == 'meta':
            self.meta = dict(self)
        elif type == 'zh':
            self.zh = dict(self)

    def localizewith(self, loc: 'BohObj') -> None:
        if self.id != loc.id:
            raise UnexpectedBohObj('\'loc\' must have the same ID.')
        if self.type != 'meta':
            raise UnexpectedBohObj('A object without \'meta\' type cannot be localized.')
        if loc.type != 'zh':
            raise UnexpectedBohObj('\'loc\' must have \'zh\' type.')

        def merge(meta, zh):
            if isinstance(meta, dict):
                res = {}
                for key, value in meta.items():
                    if zh.get(key) is None:
                        res[key] = value
                    elif isinstance(value, dict) or isinstance(value, list):
                        res[key] = merge(value, zh[key])
                    else:
                        res[key] = zh[key]
            elif isinstance(meta, list):
                # slots and preslots
                res = []
                zhmap = {}
                for value in zh:
                    zhmap[(value.get('id') or value.get('ID')).lower()] = value
                for value in meta:
                    id = (value.get('id') or value.get('ID')).lower()
                    if zhmap.get(id) is None:
                        res.append(value)
                    else:
                        res.append(merge(value, zhmap[id]))
            return res
        for key, value in merge(dict(self), dict(loc)).items():
            self[key] = value
        
        self.label = self.get('label') or self.get('Label')
        self.zh = loc
        self.type = 'localizedmeta'

    def tojson(self, dir: str = './', forwiki: bool = False) -> None:
        """
        Create a JSON file for the object in the given directory.

        Args:
            dir (str): Output directory.
            forwiki (bool): True if the JSON file is for update to the boh.huijiwiki.com, False otherwise.
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        fname = self.id
        if forwiki:
            fname = fname.replace(' ', '_')
            if fname.startswith('_'):
                fname = 'Underline' + fname
            if self.type == 'zh':
                if fname.endswith('_'):
                    fname = fname + 'zh'
                else:
                    fname = fname + '_zh'
            fname = fname.capitalize()
        else:
            fname = '_' + fname # Avoid invalid Windows file name
        fname = fname + '.json'

        with open(os.path.join(dir, fname), 'w', encoding='utf-8') as file:
            file.write(json.dumps(self, indent='\t', ensure_ascii=False))