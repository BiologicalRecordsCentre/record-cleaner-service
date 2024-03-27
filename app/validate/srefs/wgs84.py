# from .sref_base import SrefBase
from .ci_grid import CiGrid


class Wgs84:  # (SrefBase):

    def __init__(self, latitude: float, longitude: float):
        self.srid = 4326
        self.sref = (latitude, longitude)

    @property
    def sref(self) -> tuple:
        return self._sref

    @sref.setter
    def sref(self, value: tuple):
        latitude, longitude = value
        if latitude < -90 or value > 90:
            raise ValueError("Latitude must be between -90 and 90.")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180.")
        self._sref = value
