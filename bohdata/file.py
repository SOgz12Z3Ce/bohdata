#-*-coding:utf-8-*-
"""文件操作模块。

    此模块用于执行文件操作，包括从``.json``文件中读取游戏数据、检查``.json``文件。
"""
import os
import json

from bohdata.bohobj import getid
from bohdata.bohobj import BohObj
from bohdata.bohobj import BohObjType
from bohdata.bohdata import BohData

class UnexpectedEncoding(Exception):
    """意外的编码格式，读取非``UTF-8`` ``UTF-8 with BOM`` ``UTF-16LE``格式文件时抛出。
    
    Args:
        message (str): 可读的报错文本。
    """
    def __init__(self, message):
        super().__init__(message)


class UnexpectedFileFormat(Exception):
    """意外的文件格式，读取非``.json``文件时抛出。

    Args:
        message (str): 可读的报错文本。
    """
    def __init__(self, message):
        super().__init__(message)


def check(target: str) -> list[str]:
    """检查游戏``.json``文件。

    Args:
        target (str): 文件或目录路径。

    Returns:
        list[str]: 包含错误的``.json``文件。
    """
    if os.path.isdir(target):
        res = []
        for root, _, files in os.walk(target):
            for file in files:
                res = res + check(os.path.join(root, file))
        
        return res

    if not target.endswith('.json'):
        return []

    try:
        read(target)
        return []
    except json.decoder.JSONDecodeError:
        return [target]


def read(target: str, objtype: BohObjType=BohObjType.UNKNOWN) -> BohData:
    """读取游戏文件并转化为``BohData``对象。

    Args:
        target (str): 文件或文件夹路径。

    Returns:
        BohData: 游戏数据。
    """
    if os.path.isdir(target):
        res = BohData({}, objtype)
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.json'):
                    res = res + read(os.path.join(root, file), objtype)
        
        return res
    
    # 尝试打开文件
    encodings = ['utf-8', 'utf-8-sig', 'utf-16-le']  # A·K 常用编码
    content = ''
    for encoding in encodings:
        try:
            with open(target, 'r', encoding=encoding) as file:
                content = file.read()
                break
        except UnicodeDecodeError:
            continue

    if content == '':
        # 打开文件失败
        raise UnexpectedEncoding(f'"{target}" is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE.')

    # 移除 BOM 字符
    if content.startswith('\ufeff'):
        content = content[1:]

    # 加载文件
    try:
        data = BohData(json.loads(content), objtype)
        data.file = os.path.basename(target)
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(
            f'{error.msg}\n加载"{target}"时出错。\n提示：检查 A·K 的 .json 文件，其可能含有错误。\n位置', 
            error.doc, 
            error.pos
        ) from error

    return data


def pack(dir: str) -> None:
    """打包``paratranz.cn``数据。

    Args:
        dir (str): 文件目录，应有以下结构：\n
            dir\n
            ├── core\n
            └── raw\n
    """
    def islist(obj: dict) -> bool:
        """检测字典是否为可以转化为列表。（键为从``'0'``开始的连续数字字符串）"""
        # 检查是否都为数字
        if not all(key.isdigit() for key in obj.keys()):
            return False

        keys = sorted(obj, key=int) # 排序
        return all(str(i) == keys[i] for i in range(len(keys)))
    
    def tolist(obj: dict) -> list|dict:
        """转化可以转化为列表的字典和其子字典。"""
        # 处理子字典
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
    
    def prase(output: dict, key: str, translation: str) -> None:
        """将``translation``解析到``output``。"""
        if '||' not in key:
            # 解析到最后一个迭代
            output[key] = translation
            return
        
        current_key = key.split('||')[0]    # 本层迭代需要操作的键
        if output.get(current_key) is None:
            output[current_key] = {}

        prase(output[current_key], key.split('||', 1)[1], translation)

    def addid(attr: str, obj: dict) -> None:
        for index, item in enumerate(obj[attr]):
            item['id'] = alldata.map[getid(obj)][attr][index]['id']

    alldata = read(os.path.join(dir, 'core/'))
    for root, _, files in os.walk(os.path.join(dir, 'raw/')):
        for fname in files:
            # 加载翻译文件
            path = os.path.join(root, fname)
            with open(path,'r', encoding='utf-8') as file:
                entries = json.load(file)

            # 解析翻译文件
            translations = {}    # 解析后的翻译文件，是 ID-obj map。
            for entry in entries:
                prase(translations, entry['key'], entry['translation'])

            # 转化列表
            translations = tolist(translations)

            # 添加 ID
            attrs = ['slots', 'preslots']   # 存在无序含 ID 子对象的属性
            for id, obj in translations.items():
                obj['id'] = id
                if alldata.map.get(id) is None: # 无法确定原对象的翻译文件无法根据原对象赋予 ID
                    continue

                for attr in attrs:
                    if obj.get(attr) is not None:
                        addid(attr, obj)

            # 替换有大小写之分的 ID 键
            replaceids = [id for id in translations.keys() if id.lower()!= id]
            for id in replaceids:
                translations[id.lower()] = translations[id]
                del translations[id]

            # 读取对应游戏原文件
            relpath = os.path.relpath(path, os.path.join(dir, 'raw/')).replace('.csv', '')
            source = os.path.join(dir, 'core/', relpath)
            source_objs = list(read(source).items())[0][1]

            # 创建翻译文件的 BohData 对象
            outputdata = BohData({})
            outputdata.file = fname.replace('.csv', '')
            for obj in source_objs:
                id = getid(obj)
                if translations.get(id) is None or alldata.map.get(id) is None:
                    continue

                adding_obj = BohObj(translations[id])
                adding_obj.root = alldata.map[id].root
                outputdata.append(adding_obj)

            # 报错
            for id, obj in translations.items():
                if alldata.map.get(id) is None:
                    if alldata.repeats.get(id) is not None:
                        print(f'于"{path}"的对象"{id}"存在 ID 重复的对象。')
                    else:
                        print(f'于"{path}"的对象"{id}"不存在。')

            # 计算输出文件路径
            outputpath = os.path.join('./output/', relpath)
            
            # 写入文件
            os.makedirs(os.path.dirname(outputpath), exist_ok=True)
            with open(outputpath, 'w', encoding='utf-8') as file:
                file.write(json.dumps(outputdata, ensure_ascii=False))