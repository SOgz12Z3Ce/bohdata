from .boh_obj import BohObj

class BohData(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__map()

    def __map(self):
        self.map = {}
        for _, objs in self.items():
            for obj in objs:
                self.map[obj.get('id') or obj.get('ID')] = BohObj(obj)

    def merge(self, obj):
        pass