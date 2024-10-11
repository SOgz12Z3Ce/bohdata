# 获取 Wiki 使用的数据页面文件
import bohdata

alldata = bohdata.read('./core/')
translationdata = bohdata.read('./loc_zh-hans/')

for _, obj in alldata.map.items():
	obj.tojson('./output/', True)

for _, obj in translationdata.map.items():
	obj.tojson('./output/', True)

print('文件已生成。')