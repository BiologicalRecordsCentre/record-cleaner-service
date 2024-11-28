# Spatial Reference

Spatial references can be entered in the following formats:

Format | Example | Notes
--- | --- | ---
British Gridref | {<br>&emsp;"srid":27700<br>&emsp;"gridref":"TL123678"<br>} | OSGB grid references as used on Ordnance Survey maps. Up to 1m resolution (10-figure) references are supported as well as the 2km, "DINTY" notation.
British Easting/Northing | {<br>&emsp;"srid":27700<br>&emsp;"easting":367890<br>&emsp;"northing":234560<br>&emsp;"accuracy":10<br>} | OSGB coordinates from the origin in metres. Accuracy is required.
Irish Gridref | {<br>&emsp;"srid":29903<br>&emsp;"gridref":"C123678"<br>} | Irish grid references (TM75). Up to 1m resolution (10-figure) references are supported as well as the 2km, "DINTY" notation.
Irish Easting/Northing | {<br>&emsp;"srid":29903<br>&emsp;"easting":123400<br>&emsp;"northing":234500<br>&emsp;"accuracy":100<br>} | Irish (TM75) coordinates from the origin in metres. Accuracy is required.
Channel Islands Gridref | {<br>&emsp;"srid":23030<br>&emsp;"gridref":"WV595475"<br>} | UTM30 (ED50) or WA/WV grid references. Up to 1m resolution (10-figure) references are supported as well as the 2km, "DINTY" notation.
Channel Islands Easting/Northing | {<br>&emsp;"srid":23030<br>&emsp;"easting":559549<br>&emsp;"northing":5447576<br>&emsp;"accuracy":1<br>} | UTM30 (ED50) coordinates from the origin in metres. Accuracy is required.
Any Gridref | {<br>&emsp;"srid":0<br>&emsp;"gridref":"TL123678"<br>} | OSGB, Irish, or Channel Island grid references.Can be used to process datasets including records from all these regions.
Lat/Long (WGS84) | {<br>&emsp;"srid":4326<br>&emsp;"longitude":-2.34<br>&emsp;"latitude":56.78<br>&emsp;"accuracy":1000<br>} | WGS84 decimal latitude and longitude. Accuracy is required.