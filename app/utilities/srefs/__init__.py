from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SrefSystem(int, Enum):
    GB_GRID = 27700
    IE_GRID = 29903
    CI_GRID = 23030
    GB_NI_CI_GRID = 0
    WGS84 = 4326
    OSGB36 = 4277
    IRENET75 = 7
    UTM30N = 8


class SrefAccuracy(int, Enum):
    KM10 = 10000
    KM2 = 2000
    KM1 = 1000
    M100 = 100
    M10 = 10
    M1 = 1


class SrefCountry(str, Enum):
    GB = 'Great Britain'
    IE = 'Ireland'
    CI = 'Channel Islands'


class Sref(BaseModel):
    srid: SrefSystem
    gridref: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    easting: Optional[int] = None
    northing: Optional[int] = None
    accuracy: Optional[SrefAccuracy] = 1000
    country: Optional[SrefCountry] = None
