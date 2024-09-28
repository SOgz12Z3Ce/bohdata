import json

class UnexpectedEncoding(Exception):
	"""Unexpected encoding format. Raised when trying to read a file that is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE."""
	def __init__(self, message):
		super().__init__(message)

def read(path):
	encodings = ['utf-8', 'utf-8-sig', 'utf-16-le']  # Common encodings for A·K
	# 尝试打开文件
	content = ''
	for encoding in encodings:
		try:
			with open(path, 'r', encoding=encoding) as file:
				content = file.read()
		except UnicodeDecodeError:
			continue
	
	# 打开文件失败
	if content == '':
		raise UnexpectedEncoding(f'"{path}" is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE.')

	# 删除bom字符
	if content.startswith('\ufeff'):
		content = content[1:]
	
	# 读取文件为json
	try:
		jsonData = json.loads(content)
	except json.decoder.JSONDecodeError as error:
		raise json.decoder.JSONDecodeError(
			f'Error parsing "{path}": {error.msg}\nTip: Check A·K\'s JSON file, which may contain errors.', 
			error.doc, 
			error.pos
		) from error

	return jsonData