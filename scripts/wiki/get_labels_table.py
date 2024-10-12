# 输出用于[[模块:LabelsTable]]的 Lua 文件
import bohdata

alldata = bohdata.read('./core/', objtype=bohdata.BohObjType.META)
translationdata = bohdata.read('./loc_zh-hans/', objtype=bohdata.BohObjType.TRANSLATION)

for id, obj in alldata.map.items():
    if translationdata.map.get(id):
        obj.translatewith(translationdata.map[id])

content = 'local DATA = {\n'
for id, obj in sorted(alldata.map.items()):
    if obj.label == '（无名称）':
        continue

    label = obj.label.replace('\n', '\\n').replace('\'', '\\\'')
    content = content + f'    [\'{obj.origin_id.replace('\'', '\\\'')}\'] = \'{label}\',\n'

content = content[:-2] +'\n}\n\nreturn DATA'

with open('./LabelsTabel.lua', 'w', encoding='utf-8') as file:
    file.write(content)

print('文件已生成。')