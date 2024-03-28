# Country Boundaries

At validation we can, if a vice county is provided, check a spatial reference
falls within that vice county. See valid_vc.md

At verification, we may have to check a record falls within the known
distribution for the species. See rules/without_polygon.md

In both cases the rule data is a list of grid squares while a record may be
supplied with a latitude and longitude.

There are two ways to determine if a point is in a list of grid squares:

* Convert the list of grid squares in to a polygon in a spatially enabled
database (or similar) and perform an intersection with the point.
* Convert the point in to a grid reference and see if it matches an entry in
the list.

To transform a lat/lon in to a grid reference, we need to know which grid 
reference system to use - British, Irish or Channel Islands. That can be decided
quickly by seeing if the point falls within certain bounding boxes as shown 
in the image.

![Map showing bounding boxes for Ireland and Channel Islands](assets/country_bboxes.png)

