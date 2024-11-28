# Vice County

The basis for vice county checks is a file which lists, to 1km resolution, which
vice county holds each grid square. Where a grid square overlaps multiple vice
counties, then they are listed. Only British vice counties are covered.

This means that, if a vice county is included in the data for a record, we can
check if the spatial reference and vice county are consistent. If the vice
county is not provided, then the most likely vice county for the record can be
returned.


[Calculating a grid reference from a Lat/lon](countries.md)