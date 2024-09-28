import json

class UnexpectedEncoding(Exception):
	"""意料之外的编码格式，在尝试读取编码不为 UTF-8、UTF-8 with BOM、UTF-16LE 之一的文件时抛出。"""
	def __init__(self, message):
		super().__init__(message)

def read(path):
	encodings = ['utf-8', 'utf-8-sig', 'utf-16-le'] # A·K 的常用编码
	for encoding in encodings:
		try:
			with open(path, 'r', encoding=encoding) as file:
				content = file.read()
		except UnicodeDecodeError:
			continue
		if content.startswith('\ufeff'):
			content = content[1:]
		return json.loads(content)
	raise UnexpectedEncoding(f'"{path}"未使用 UTF-8、UTF-8 with BOM 或 UTF-16LE 编码。')