from . import Sref


class SrefBase:

    _value: Sref = None

    def __init__(self):
        pass

    @property
    def value(self) -> Sref:
        return self._value

    @property
    def srid(self) -> int:
        return self._value.srid

    @property
    def gridref(self) -> str:
        return self._value.gridref
