from enum import Enum

from .gb_grid import GbGrid
from .ie_grid import IeGrid
from .ci_grid import CiGrid


class SrefSystem(int, Enum):
    GB_GRID = 1
    NI_GRID = 2
    CI_GRID = 3
    GB_NI_CI_GRID = 4
    WGS84 = 5
    OSGB36 = 6
    IRENET75 = 7
    UTM30N = 8


class_map = {
    SrefSystem.GB_GRID: GbGrid,
    SrefSystem.NI_GRID: IeGrid,
    SrefSystem.CI_GRID: CiGrid
    #     SrefSystem.GB_NI_CI_GRID,
    #     SrefSystem.WGS84,
    #     SrefSystem.OSGB36,
    #    SrefSystem.IRENET75,
    #    SrefSystem.UTM30N
}
