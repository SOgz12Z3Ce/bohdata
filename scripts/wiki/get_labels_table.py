# 输出用于[[模块:LabelsTable]]的 Lua 文件
import bohdata

meta = bohdata.read('./core/', 'meta')
zh = bohdata.read('./loc_zh-hans/', 'zh')

for id, obj in meta.map.items():
	if zh.map.get(id):
		obj.localizewith(zh.map[id])

content = 'local DATA = {\n'
for id, obj in sorted(meta.map.items()):
	if obj.label is None:
		continue
	
	id = id.replace('\'', '\\\'')

	label = obj.label
	label = label.replace('\n', '\\n')
	label = label.replace('\'', '\\\'')
	content = content + f'\t[\'{id}\'] = \'{label}\',\n'
content = content[:-2] +'\n}\n\nreturn DATA'

with open('./LabelsTabel.lua', 'w', encoding='utf-8') as file:
	file.write(content)

print('文件已生成。')