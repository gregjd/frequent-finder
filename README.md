# frequent-finder
A library for auto-generating frequent network maps for public transit systems, using GTFS data as input.


There are two basic parts to this. One is taking the GTFS feed and producing a GeoJSON file of the frequent services. The other is taking that GeoJSON and creating a map; I'm interested in three options for creating maps:

* interactive maps (using Mapbox)
* SVGs (using D3), which would probably be not-too-attractive, but would provide a base for editing in a vector graphics program like Illustrator to create a nice static map
* shapefile exports, which could be used in a program like QGIS or ArcGIS to create a static map

![The two parts of the process](/images/FF-OverallFlow.png)

The overall approach here is to get something simple working then keep adding features to make it more advanced. What this means for the left side of the process shown above is to start with a very basic method for identifying frequent services; this will need to be greatly refined thanks to the complexity of many transit systems. For the right side of this flowchart, my first priority is creating a Mapbox map, with a D3-generated SVG being a much lower priority (though it shouldn't be too hard to make an ugly version). I don't envision doing anything regarding shapefile exports; there are already existing tools that can convert GeoJSON to shapefiles.
