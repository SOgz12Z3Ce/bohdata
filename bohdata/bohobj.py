#-*-coding:utf-8-*-
"""游戏对象类。

    此模块包含了一个类，用于表示游戏对象。另有一枚举类表明对象类型。
"""
from enum import Enum

import os
import json

class InvalidOriginObject(Exception):
    """无效的原始对象。传入的初始化对象不是游戏对象时抛出。

    Args:
        message (str): 可读的报错文本。
    """
    def __init__(self, message):
        super().__init__(message)


class InvalidRoot(Exception):
    """无效的根分类。尝试将 root 设置为游戏中不存在的分类时抛出。

    Args:
        message (str): 可读的报错文本。
    """
    def __init__(self, message):
        super().__init__(message)


class BohObjType(Enum):
    """游戏对象类型的枚举。"""

    META = 1
    """原始游戏对象。"""

    TRANSLATION = 2
    """翻译文件对象。"""

    TRANSLATED = 3
    """已翻译的游戏对象。"""


def istext(obj: dict|list) -> bool:
    """检查一个字典或列表是否全为文本和 ID，用于判断对象是否为翻译文件对象。"""
    TEXT_KEYS = {'AlphaLabelOverride', 'Desc', 'Label', 'StartDescription', 'comments', 'desc', 'description', 'descriptionunlocked', 'family', 'id', 'label', 'preface', 'preslots', 'slot', 'slots', 'startdescription', 'startlabel', 'xexts'}
    if isinstance(obj, dict):
        for key, value in obj.items():
            # 跳过 xexts
            if key == 'xexts':
                continue

            if key not in TEXT_KEYS:
                return False
            
            if isinstance(value, dict) or isinstance(value, list):
                if istext(value) is False:
                    return False
    elif isinstance(obj, list):
        for value in obj:
            if istext(value) is False:
                return False

    return True


def getid(obj: dict) -> str:
    """获取一个对象的 ID。

    Args:
        obj (dict): 对象，可以是独立的游戏对象、翻译文件对象或是``slots``等属性值中的对象。

    Returns:
        str: 对象 ID。
    """
    return (obj.get('id') or obj.get('ID')).lower()


class BohObj(dict):
    """表示游戏对象的类。

    ``root``属性需要在对象被创建时手动设置，若不设置将默认为``'unknown'``。
    ``root``相同的对象才会被认为是相等的，若等号两侧的其中一者``root``为``'unknown'``也会被认为是相等的。

    Attributes:
        id (str): 对象 ID，全小写。
        origin_id (str): 游戏文件中的原始对象 ID，未转化大小写。
        label (str): 对象名称。
        type (BohObjType): 对象类型。
        root (str): 对象的根分类。默认为``'unknown'``。

    Raises:
        InvalidOriginObject: 传入无效的对象原始数据。
        InvalidRoot: 尝试为对象的``root``属性赋予游戏中不存在的根类型。
    """
    @property
    def root(self) -> str:
        if self._root is None:
            return 'unknown'
        return self._root
    
    @root.setter
    def root(self, value: str):
        VALID_ROOTS = {'dicta', 'cultures', 'achievements', 'decks', 'elements', 'recipes', 'endings', 'settings', 'legacies', 'verbs'}
        if value not in VALID_ROOTS:
            raise InvalidRoot(f"错误的根分类：{value}")
        self._root = value

    def __init__(self, obj):
        super().__init__(obj)

        # ID
        self.origin_id = self.get('id') or self.get('ID')
        if self.origin_id is None:
            raise InvalidOriginObject(f"无 ID 的原始游戏对象：{str(self)}")
        self.id = self.origin_id.lower()
        # 2024.A.2 'AGNES' from beta->live: - MODDING: IDs of entities are now completely case-insensitive for all purposes (in-game access, modifying, inheriting, localizing etc).
        # e.g.: Wooden

        # Label
        self._setLabel()

        # Type
        if istext(self):
            self.type = BohObjType.TRANSLATION
        else:
            self.type = BohObjType.META

        # Root
        self._root = None

    def __eq__(self, other) -> bool:
        if not isinstance(other, BohObj):
            return False
        
        return super().__eq__(other) and (self.root == other.root or self.root == 'unknown' or other.root == 'unknown')

    def translatewith(self, translation: 'BohObj') -> None:
        """使用翻译文件对象翻译原始游戏对象。

        Args:
            translation (BohObj): 翻译文件对象。
        """
        def merge(meta: dict|list, translation: dict|list) -> None:
            """将 translation 合并到 meta。"""
            if isinstance(meta, dict):
                for key, value in translation.items():
                    if isinstance(value, str):
                        meta[key] = value
                    else:   # dict 或 list
                        merge(meta[key], value)
            else:   # list
                map_ = {getid(item): item for item in translation}   # list 中所有 dict 的 map
                for item in meta:
                    merge(item, map_[getid(item)])
        
        merge(self, translation)
        self._setLabel()
        self.type = BohObjType.TRANSLATED

    def tojson(self, dir: str = './', forwiki: bool = False) -> None:
        """在给定目录下创建对象的``.json``文件。

        Args:
            dir (str, optional): 输出路径。默认为``'./'``。
            forwiki (bool, optional): 是否为``boh.huijiwiki.com``所用文件。默认为``False``。
        """
        if not os.path.exists(dir):
            os.makedirs(dir)

        fname = self.id
        if forwiki:
            fname = fname.replace('_', ' ')
            if fname.startswith(' '):
                fname = f'Underline{fname}'
            if self.type == BohObjType.TRANSLATION:
                if fname.endswith(' '):
                    fname = f'{fname}zh'
                else:
                    fname = f'{fname} zh'
            fname = fname[0].upper() + fname[1:]
        fname = f'{fname}.json'

        with open(os.path.join(dir, fname), 'w', encoding='utf-8') as file:
            file.write(json.dumps(self, indent='\t', ensure_ascii=False))

    def _setLabel(self) -> None:
        """更新自身``label``属性。"""
        if self.get('label') == '' or self.get('Label') == '':
            self.label = ""
        else:
            self.label = self.get('label') or self.get('Label') or "（无名称）"