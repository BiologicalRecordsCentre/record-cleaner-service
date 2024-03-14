class NiGrid:

    def __init__(self, sref: str):
        self.sref = sref

    def validate(self) -> bool:
        if len(self.sref) == 8:
            return True
        else:
            return False
