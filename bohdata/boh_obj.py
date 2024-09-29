class BohObj(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = self.get('id') or self.get('ID')