import json

class UnexpectedEncoding(Exception):
	"""Unexpected encoding format. Raised when trying to read a file that is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE."""
	def __init__(self, message):
		super().__init__(message)

def read(path):
	encodings = ['utf-8', 'utf-8-sig', 'utf-16-le']  # Common encodings for A·K
	for encoding in encodings:
		try:
			with open(path, 'r', encoding=encoding) as file:
				content = file.read()
		except UnicodeDecodeError:
			continue
		except json.decoder.JSONDecodeError as error:
			print(f'Error parsing "{path}":')
			print(error)
			print('Tip: Check A·K\'s JSON file, which may contain errors.')

		if content.startswith('\ufeff'):
			content = content[1:]
		return json.loads(content)
	raise UnexpectedEncoding(f'"{path}" is not encoded in UTF-8, UTF-8 with BOM, or UTF-16LE.')