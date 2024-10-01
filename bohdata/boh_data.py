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

    methods:
        append(obj: BohObj, root: str) -> None: Append a object.
    """
    
    def __init__(self, type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Transform original objects into BohObjs
        for root, objs in self.items():
            new_objs = []
            for obj in objs:
                new_objs.append(BohObj(type, root, obj))
            self[root] = new_objs

        self.__map()
        self.__root()

    def __add__(self, other: 'BohData') -> 'BohData':
        res = copy.deepcopy(self)
        for root, objs in other.items():
            for obj in objs:
                res.append(obj, root)
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

    def append(self, obj: BohObj, root: str) -> None:
        """
        Append a BohObj.

        Args:
            obj (BohObj): The BohObj to append.
            root (str): The root category of the BohObj.
        """
        if root not in self.keys():
            self[root] = [obj]
        elif obj not in self[root]:
            self[root].append(obj)

        self.roots.add(root)

        self.__map_append(obj)