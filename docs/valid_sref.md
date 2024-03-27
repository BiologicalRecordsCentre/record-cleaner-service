#Spatial Reference

Spatial references can be entered in the following formats:

Format | Example | Notes
--- | --- | ---
sridBritish Gridref | {<br>&emsp;"system":27700<br>&emsp;"gridref":"TL123678"<br>} | OSGB grid references as used on Ordnance Survey maps. Up to 1m resolution (10-figure) references are supported as well as the 2km, "DINTY" notation.
British Easting/Northing | {<br>&emsp;"system":27700<br>&emsp;"easting":"TL123"<br>&emsp;"northing":"TL678"<br>} | OSGB coordinates from the origin in metres.
Lat/Long (WGS84) | {<br>&emsp;"system":4326<br>&emsp;"longitude":"TL123"<br>&emsp;"latitude":"TL678"<br>}