# 检查目录下存在错误的 JSON 文件
import bohdata

files = bohdata.check(input('输入游戏文件根目录：'))
if len(files) == 0:
	print('未检查到错误。')
else:
	print('在以下文件中检测到错误：')
	for file in files:
		print(file)