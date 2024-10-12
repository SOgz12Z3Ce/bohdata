# 获取 Wiki 使用的数据页面文件
import bohdata

alldata = bohdata.read('./core/', objtype=bohdata.BohObjType.META)
translationdata = bohdata.read('./loc_zh-hans/', objtype=bohdata.BohObjType.TRANSLATION)

for _, obj in alldata.map.items():
	obj.tojson('./output/', forwiki=True)

for _, obj in translationdata.map.items():
	obj.tojson('./output/', forwiki=True)

print('文件已生成。')