from .wgs84 import Wgs84
from .ci_grid import CiGrid
from .ie_grid import IeGrid
from .gb_grid import GbGrid
from . import Sref, SrefSystem


class SrefFactory:
    def __new__(self, sref: Sref):
        match sref.srid:
            case SrefSystem.GB_GRID:
                return GbGrid(sref)
            case SrefSystem.IE_GRID:
                return IeGrid(sref)
            case SrefSystem.CI_GRID:
                return CiGrid(sref)
            case SrefSystem.GB_NI_CI_GRID:
                if sref.gridref is None:
                    raise ValueError("Invalid spatial reference. A gridref "
                                     "must be provided.")
                if sref.gridref[:2] == "WA" or sref.gridref[:2] == "WV":
                    return CiGrid(sref)
                elif sref.gridref[1:2].isnumeric():
                    return IeGrid(sref)
                else:
                    return GbGrid(sref)
            case SrefSystem.WGS84:
                return Wgs84(sref)
