# 获取 Wiki 使用的数据页面文件
import os
import bohdata

meta = bohdata.read('./core/', 'meta')
zh = bohdata.read('./loc_zh-hans/', 'zh')

for _, obj in meta.map.items():
	obj.tojson('./output/', True)
for _, obj in zh.map.items():
	obj.tojson('./output/', True)

print('文件已生成。')