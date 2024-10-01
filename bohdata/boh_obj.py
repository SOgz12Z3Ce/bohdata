import os
import json

class BohObj(dict):
    """
    A class to represent a object in the game.

    Attributes:
        id (str): The ID of the object.
        type (str): The type of the object.
        root (str): The category of the object.
    
    methods:
        tojson(dir: str, forwiki: bool = False) -> None: Create a JSON file for the object in the given directory.
        localizewith(loc: BohObj) -> None: Localize the object with a localization object.
    """
    def __init__(self, type: str, root: str = 'unknown', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = (self.get('id') or self.get('ID')).lower() # 2024.A.2 'AGNES' from beta->live: - MODDING: IDs of entities are now completely case-insensitive for all purposes (in-game access, modifying, inheriting, localizing etc).
        self.type = type
        self.root = root

    def tojson(self, dir: str, forwiki: bool = False) -> None:
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

    def localizewith(self, loc: 'BohObj') -> None:
        pass