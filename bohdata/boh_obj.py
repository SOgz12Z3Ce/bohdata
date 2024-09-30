class BohObj(dict):
    """
    A class to represent a object in the game.

    Attributes:
        id (str): The ID of the object.
        root (str): The category of the object.
    """
    def __init__(self, root: str = 'unknown', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = (self.get('id') or self.get('ID')).lower() # 2024.A.2 'AGNES' from beta->live: - MODDING: IDs of entities are now completely case-insensitive for all purposes (in-game access, modifying, inheriting, localizing etc).
        self.root = root