# frequent-finder
A library for auto-generating frequent network maps for public transit systems, using GTFS data as input.


There are two basic parts to this. One is taking the GTFS feed and producing a GeoJSON file of the frequent services. The other is taking that GeoJSON and creating a map; I'm interested in options for creating both interactive maps (using Mapbox) and SVGs (using D3).
