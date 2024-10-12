#-*-coding:utf-8-*-
"""游戏数据类。

    此模块包含了一个类，用于存储游戏数据。
"""

import os
import re
import copy

from bohdata.bohobj import BohObj
from bohdata.bohobj import BohObjType

class InvalidFileName(Exception):
    """无效文件名。在尝试设置 Windows 下无效的文件名时抛出。

    Args:
        message (str): 可读的报错文本。
    """
    def __init__(self, message):
        super().__init__(message)


class BohData(dict):
    """存储游戏数据用的类。

    Attributes:
        map (dict[str, dict[str, Any]]): ID 到游戏对象的映射表，其中：
            - keys (str): 游戏对象的 ID。
            - values (dict[str, Any]): 游戏对象。
        repeats (dict[str, set[dict[str, Any]]]): 存储拥有重复 ID 游戏对象的变量，其中：
            - keys (str): 重复的 ID。
            - values (list[dict[str, Any]]]): 重复对象的列表，每个成员都是游戏对象。
        roots (set[str]): 所含游戏对象的所有根分类。
        file (str): 来源文件（如有）。默认为一内部分配的默认名``Unnamed<file_index>.json``。
    
    Raise:
        InvalidFileName: 尝试为对象的``file``属性赋予非法的文件名。
    """
    file_index = 1
    """用于默认文件名的文件序号。"""
    
    @property
    def file(self) -> str:
        if self._file is None:
            self._file = f'Unnamed{str(BohData.file_index)}.json'
            BohData.file_index = BohData.file_index + 1
        return self._file
    
    @file.setter
    def file(self, value: str):
        if value.startswith(' '):
            raise InvalidFileName(f"无效的文件名（以空格开头）：{value}")
        if re.search(r'[<>:"/\\|?*]', value):
            raise InvalidFileName(f"无效的文件名（包含非法字符）：{value}")
        if os.path.splitext(value)[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                                                  'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}:
            raise InvalidFileName(f"无效的文件名（使用保留文件名）：{value}")
        if len(value) > 255:
            raise InvalidFileName(f"无效的文件名（文件名过长）：{value}")
        if not value.endswith('.json'):
            raise InvalidFileName(f"无效的文件名（未以 .json 结尾）：{value}")

        self._file = value

    def __init__(self, obj: dict, objtype: BohObjType=BohObjType.UNKNOWN):
        """初始化函数，使用传入的一个游戏文件 json 对象初始化。亦可使用空字典``{}``。"""
        super().__init__(obj)

        if self == {}:
            self.map = {}
            self.repeats = {}
            self.roots = set()
            self._file = None
            return

        # 转化原始游戏对象
        root, origin_objs = list(self.items())[0]   # 一个游戏文件只可能拥有一个根分类
        new_objs = []
        for origin_obj in origin_objs:
            new_obj = BohObj(origin_obj, objtype)
            new_obj.root = root
            new_objs.append(new_obj)
        self[root] = new_objs

        # 设置根分类
        self.roots = {root}

        # 创建映射表
        self._map()

    def __add__(self, other: 'BohData') -> 'BohData':
        res = copy.deepcopy(self)
        objs = list(other.map.values())
        for obj in objs:
            res.append(obj)
        return res

    def append(self, obj: BohObj) -> None:
        """添加``BohObj``对象。

        Args:
            obj (BohObj): 将添加的对象。
        """
        if obj.root == 'unknown':
            self._map_append(obj)
            return
        
        if obj.root not in self.keys():
            self[obj.root] = [obj]
        elif obj not in self[obj.root]:
            self[obj.root].append(obj)

        self.roots.add(obj.root)
        self._map_append(obj)

    def tocsv(self, dir: str='./') -> None:
        """输出用于``paratranz.cn``的``.csv``文件。

        Args:
            dir (str, optional): 输出路径。默认为``'./'``。
        """
        passkeys = ['AlternativeDefaultWorldSpherePaths', 'DefaultCardBack', 'DefaultGameSpeed', 'DefaultWorldSpherePath',
                    'GameOverScene', 'ID', 'LoadingScene', 'LogoScene', 'ManifestationType',
                    'MaxSuitabilityPulseFrequency', 'MenuScene', 'NewGameScene', 'NoteElementId', 'PlayfieldScene',
                    'QuoteScene', 'StoredManifestation', 'StoredPhyicalManifestation', 'SuitabilityPulseSpeed',
                    'WorldSphereType', 'achievements', 'actionid', 'ambittable', 'audio', 'audiooneshot', 'category',
                    'craftable', 'datatype', 'decayto', 'defaultcard', 'defaultvalue', 'effects', 'ending', 'flavour',
                    'fontscript', 'frompath', 'fx', 'fxreqs', 'hint', 'hints', 'icon', 'iconUnlocked', 'id', 'image',
                    'inherits', 'isHidden', 'ishidden', 'lalt', 'linked', 'manifestationtype', 'mutations', 'reqs', 'run',
                    'sort', 'spec', 'tabid', 'topath', 'ui', 'unique', 'uniquenessgroup', 'valuelabels',
                    'valuenotifications', 'verbicon', 'warmup', 'xtriggers']    # 应跳过的不含需翻译文本的键
        # TODO: 完成这些
        # if isinstance(meta, dict):
        #     for key, value in meta.items():
        #         if key in passkeys:
        #             continue
        # 
        #         if zh is None:
        #             zhValue = None
        #         else:
        #             zhValue = zh.get(key)
        # 
        #         if isinstance(value, str):
        #             line = prefix + '||' + key + ',"' + value.replace('\n', '\\n') + '","' + (zhValue or '').replace('\n', '\\n') + '"'
        #             res.append(line)
        #         elif isinstance(value, dict) or isinstance(value, list):
        #             # 值为字典或列表，递归调用
        #             res = res + getCSVLines(value, zhValue, prefix + '||' + key)
        # elif isinstance(meta, list):
        #     # 列表
        #     for index, value in enumerate(meta):
        #         # 获取本地化数据值
        #         if zh == None:
        #             zhValue = None
        #         else:
        #             try:
        #                 zhValue = zh[index]
        #             except IndexError:
        #                 zhValue = None
        # 
        #         if isinstance(value, str):
        #             # 值为字符串（需翻译文本）
        #             line = prefix + '||' + str(index) + ',"' + value.replace('\n', '\\n') + '","' + (zhValue or '').replace('\n', '\\n') + '"'
        #             res.append(line)
        #         elif isinstance(value, dict) or isinstance(value, list):
        #             # 值为字典或列表，递归调用
        #             res = res + getCSVLines(value, zhValue, prefix + '||' + str(index))
        # path = os.path.join(dir, self.file[:-4] + 'csv')

    def _map(self):
        """创建对象映射表。"""
        self.map = {}
        self.repeats = {}
        
        objs = list(self.items())[0][1]
        for obj in objs:
            self._map_append(obj)
    
    def _map_append(self, obj: BohObj) -> None:
        """在映射表中添加对象。"""
        if obj.id in self.repeats.keys():
            self.repeats[obj.id].append(obj)
        elif obj.id in self.map.keys() and obj != self.map[obj.id]:
            self.repeats[obj.id] = [self.map[obj.id], obj]
            del self.map[obj.id]
        else:
            self.map[obj.id] = obj