# frequent-finder
A library for auto-generating frequent network maps for public transit systems, using GTFS data as input.


There are two basic parts to this. One is taking the GTFS feed and producing a GeoJSON file of the frequent services. The other is taking that GeoJSON and creating a map; I'm interested in three options for creating maps:

* interactive maps (using Mapbox)
* SVGs (using D3), which would probably be not-too-attractive, but would provide a base for editing in a vector graphics program like Illustrator to create a nice static map
* shapefile exports, which could be used in a program like QGIS or ArcGIS to create a static map