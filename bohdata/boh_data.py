import copy

from .boh_obj import BohObj

class BohData(dict):
    """
    A class representing a set of game data, retaining the original JSON format.

    Attributes:
        map (dict[str, dict[str, Any]]): A dictionary of objects where:
            - keys (str): The ID of the object.
            - values (dict[str, Any]): A dictionary of the object where:
                - keys (str): The names of attributes.
                - values (Any): The attributes.
        repeat (dict[str, list[dict[str, Any]]]): A dictionary of objects with the same ID where:
            - keys (str): The ID of the objects.
            - values (list[dict[str, Any]]): A list of dictionaries for each object, where:
                - Each dictionary contains:
                    - keys (str): The names of the attributes.
                    - values (Any): The attributes.
        roots (set[str]): All categories of contained objects.
        file (str): The source file name.

    methods:
        append(obj: BohObj) -> None: Append a object.
        tocsv(dir: str = './') -> None: Create a CSV file for the object in the given directory.
    """
    
    def __init__(self, type, file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Transform original objects into BohObjs
        for root, objs in self.items():
            new_objs = []
            for obj in objs:
                new_objs.append(BohObj(type, root, obj))
            self[root] = new_objs
        
        self.file = file

        self.__map()
        self.__root()

    def __add__(self, other: 'BohData') -> 'BohData':
        res = copy.deepcopy(self)
        for root, objs in other.items():
            for obj in objs:
                res.append(obj)
        return res

    def __map_append(self, obj: BohObj) -> None:
        """Append a BohObj into the map (and repeat)."""
        if obj.id in self.repeat.keys():
            self.repeat[obj.id].append(obj)
        elif obj.id in self.map.keys() and obj != self.map[obj.id]:
            self.repeat[obj.id] = [self.map[obj.id], obj]
            del self.map[obj.id]
        else:
            self.map[obj.id] = obj

    def __map(self) -> None:
        """Get the object data dictionary indexed by ID."""
        self.map = {}
        self.repeat = {}    # List of objects with repeating IDs
        for _, objs in self.items():
            for obj in objs:
                self.__map_append(obj)
                
    def __root(self) -> None:
        """Get the root categories."""
        self.roots = set()

        for root, _ in self.items():
            self.roots.add(root)

    def append(self, obj: BohObj) -> None:
        """
        Append a BohObj.

        Args:
            obj (BohObj): The BohObj to append.
            root (str): The root category of the BohObj.
        """
        if obj.root not in self.keys():
            self[obj.root] = [obj]
        elif obj not in self[obj.root]:
            self[obj.root].append(obj)

        self.roots.add(obj.root)

        self.__map_append(obj)
    
    def tocsv(self, dir: str = "./") -> None:
        passkeys = ['AlternativeDefaultWorldSpherePaths', 'DefaultCardBack', 'DefaultGameSpeed', 'DefaultWorldSpherePath', 'GameOverScene', 'ID', 'LoadingScene', 'LogoScene', 'ManifestationType', 'MaxSuitabilityPulseFrequency', 'MenuScene', 'NewGameScene', 'NoteElementId', 'PlayfieldScene', 'QuoteScene', 'StoredManifestation', 'StoredPhyicalManifestation', 'SuitabilityPulseSpeed', 'WorldSphereType', 'achievements', 'actionid', 'ambittable', 'audio', 'audiooneshot', 'category', 'craftable', 'datatype', 'decayto', 'defaultcard', 'defaultvalue', 'effects', 'ending', 'flavour', 'fontscript', 'frompath', 'fx', 'fxreqs', 'hint', 'hints', 'icon', 'iconUnlocked', 'id', 'image', 'inherits', 'isHidden', 'ishidden', 'lalt', 'linked', 'manifestationtype', 'mutations', 'reqs', 'run', 'sort', 'spec', 'tabid', 'topath', 'ui', 'unique', 'uniquenessgroup', 'valuelabels', 'valuenotifications', 'verbicon', 'warmup', 'xtriggers']
        def get_lines(meta, zh, prefix):
            #if isinstance(meta, dict):
            #    for key, value in meta.items():
            #        if key in passkeys:
            #            continue
#
            #        if zh is None:
            #            zhValue = None
            #        else:
            #            zhValue = zh.get(key)
#
            #        if isinstance(value, str):
            #            line = prefix + '||' + key + ',"' + value.replace('\n', '\\n') + '","' + (zhValue or '').replace('\n', '\\n') + '"'
            #            res.append(line)
            #        elif isinstance(value, dict) or isinstance(value, list):
            #            # 值为字典或列表，递归调用
            #            res = res + getCSVLines(value, zhValue, prefix + '||' + key)
            #elif isinstance(meta, list):
            #    # 列表
            #    for index, value in enumerate(meta):
            #        # 获取本地化数据值
            #        if zh == None:
            #            zhValue = None
            #        else:
            #            try:
            #                zhValue = zh[index]
            #            except IndexError:
            #                zhValue = None
#
            #        if isinstance(value, str):
            #            # 值为字符串（需翻译文本）
            #            line = prefix + '||' + str(index) + ',"' + value.replace('\n', '\\n') + '","' + (zhValue or '').replace('\n', '\\n') + '"'
            #            res.append(line)
            #        elif isinstance(value, dict) or isinstance(value, list):
            #            # 值为字典或列表，递归调用
            #            res = res + getCSVLines(value, zhValue, prefix + '||' + str(index))

        #path = os.path.join(dir, self.file[:-4] + 'csv')

            pass