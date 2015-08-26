# frequent-finder
A library for auto-generating frequent network maps for public transit systems, using GTFS data as input.


There are two basic parts to this. One is taking the GTFS feed and producing a GeoJSON file of the frequent services. The other is taking that GeoJSON and creating a map; I'm interested in three options for creating maps:

* interactive maps (using Mapbox)
* SVGs (using D3), which would probably be not-too-attractive, but would provide a base for editing in a vector graphics program like Illustrator to create a nice static map
* shapefile exports, which could be used in a program like QGIS or ArcGIS to create a static map

![The two parts of the process](/images/FF-OverallFlow.png)

The overall approach here is to get something simple working then keep adding features to make it more advanced. What this means for the left side of the process shown above is to start with a very basic method for identifying frequent services; this will need to be greatly refined thanks to the complexity of many transit systems. For the right side of this flowchart, my first priority is creating a Mapbox map, with a D3-generated SVG being a much lower priority (though it shouldn't be too hard to make an ugly version). I don't envision doing anything regarding shapefile exports; there are already existing tools that can convert GeoJSON to shapefiles.


### Issues and challenges

One of the big challenges of this project is its relationship with the source data. GTFS data is great for "specific" transit information: figuring out what service is available at an exact time and place on an exact day in time. What I'm trying to do is the opposite: create a generalized picture of the transit system. This sparks many questions about how exactly to do this:

* How do you handle days of the week? Holidays? Schedule change dates?
* How do you decide how frequently a line runs? What are the starting and ending times for this query? Do those times apply to all portions of the line or just one location?
* What if buses/trains aren't evenly spaced? What if a line is generally frequent but there are a couple exceptions?
* How do you handle lines that split into branches, or multiple lines that have a shared segment? How do you describe a street has frequent service on all parts of it but different overlapping lines on different segments?
* If multiple lines overlap for just a couple blocks but provide frequent service there, do you really want to count that?
* How do you deal with one-way street pairs? Loops? What do you do if a line visits the same stop twice in a single journey (yes, this really happens)?
* What do you do about lines with both local service and limited, express, or skip-stop service?
* What do you do if a frequent line splits into two parts for a short section and then the parts rejoin?

All of these issues are present in real-world transit systems. They present serious challenges to any attempt at automating frequent network determination. FrequentFinder needs to be able to deal with them.


Links:
[The Case]: http://www.humantransit.org/2010/08/basics-the-case-for-frequency-mapping.html
eeed



### FAQ



**Hasn't someone done this before?**

Yes and no.

Others have certainly thought of the idea. I've seen plenty of people express a [desire](http://seattletransitblog.com/2011/09/12/spokanes-frequent-transit-map/#comment-185795) for something like this. But so far, my web searches have not been very fruitful.

[Conveyal](http://conveyal.com/) has many tools that are useful for analyzing transit, and I haven't yet had time to dig through them all, but at a glance it doesn't seem there's anything that quite does this.

If you [search GitHub](https://github.com/search?utf8=%E2%9C%93&q=transit+frequent+network+map) for "transit frequent network map," this repo is the only result.

The most promising example seems to be [an example](http://www.humantransit.org/2010/09/frequent-network-maps-by-routefriend.html) made by David Marcus at Routefriend. But it appears as if not much has been done since this map. The Routefriend website [has a page](http://www.routefriend.com/frequencymap.html) with a drop-down menu for selecting one of several cities, but I haven't had any luck with it; the page says "Loading (this may take a sec)" but no lines ever appear on the map. Perhaps it once worked but no longer does... or maybe it takes a really long time.

And then there's this ____

But again

So, no, I haven't found any example that does exactly what I want. Hence my motivation for making FrequentFinder!

There are a few key features about my approach:

* *I want it to be open.* It's all here on GitHub, partially because I believe in open source technology and partially because I'd really like advice on how it can be improved. I also like the idea that other people might be able to use what I've done and do even more great things, like something involving [OpenTripPlanner](http://www.opentripplanner.org/).
* *It should work for any city's GTFS feed.* It seems like the attempts that have been made so far only targeted individual cities. FrequentFinder should work anywhere.
* *I want there to be options users can easily customize.* I don't want to hard-code a frequency standard of 15 minutes into the program. While there are default options, users can choose frequency thresholds, allowable deviation from the standard, starting and ending times of day, days of the week, etc.
* *I'd like interactive mapping to be done on Mapbox.* Part of this is the commitment to open source and part of it is because Mapbox allows for easy customization of styles and has many great base maps.
* *I want to make it easy to use my tools to make things I never considered.* I have a clear separation between finding the frequent network and mapping it, specifically so that people can take the GeoJSON and do whatever they want with it.




**Is this supposed to be a replacement for "hand-drawn" frequent network maps?**

http://www.humantransit.org/2010/09/montreal-the-pleasure-of-maps-by-hand.html

Absolutely not. I feel strongly that custom-drawn, abstract transit maps are superior to auto-generated ones. But making the former takes much more time and effort than the latter. This is intended to do a few things that custom-drawn maps can't. Thanks to the fact that they're auto-generated, these maps can:
* serve as frequent network maps for cities where custom-drawn maps don't exist
* allow quick visualization of the effect of service changes on the frequent network
* serve as an inspiration for custom-drawn frequent network maps
(that third reason is probably the most important one)

I want to highlight a [comment](http://www.humantransit.org/2010/09/transit-network-maps-draw-and-sell-your-own.html?cid=6a00d83454714d69e20133f43d38c0970b#comment-6a00d83454714d69e20133f43d38c0970b) by Alon Levy: "When I made my New York maps, the main challenge was to collect the set of frequent buses. Drawing was tedious, and I had to make some simplifications for routes that have short one-way pair segments, but it only has to be done once. Ideally, a transit agency would have a customizable map, allowing you to check boxes for all buses you want to see. That would also take care of questions like 10 versus 15 minutes, or [8am-7pm] versus [6am-9pm]." (Alon's blog, [Pedestrian Observations](https://pedestrianobservations.wordpress.com/), is a must-read.)


So no, I don't see this as an end in itself.

That said, as I continute to develop FrequentFinder, there are certainly features I could add that would enhance its smartness and abstractness:

* simplifying line geometry to make lines smoother
* calculating stop distance/operating speed to determine which lines are rapid transit
* making the background very muted to minimize the importance of minor geographic features




**Why is there no graphical user interface (GUI)?**

Because developing a GUI takes time, and for now I'd rather devote that time and energy toward improving the core capabilities of Frequent Finder. While a GUI would be nice, I think it's far from necessary as the directions for how to use FrequentFinder aren't that complicated.

As it stands, FrequentFinder is not a web app or smartphone app. The reason is simple: it doesn't yet offer the speed for those kinds of uses, and frankly those uses don't matter that much right now. The point of a frequent network map is that it's widely usable. Unlike getting in-the-moment transit directions, this one map is useful for the span of service it applies to (i.e. what hours of the day it's true for). So it wouldn't make any sense to keep generating a new one for the same city unless there's a service change. Instead, the point of this
This is more for calculating a frequent network. The point isn't so that you can whip out your smartphone and see the map instantly, though you could certainly do that if you've already generated it.

In any case, when it comes to navigating a transit system (or just staring at a transit map so you can absort its information), I would strongly suggest looking at a more abstract, custom-drawn one, not these auto-generated ones (though they're much better than nothing!).



I'm not concerned about having such blazing speed


**Why did you choose Python and JavaScript?**

Initially I was actually going to use JavaScript for everything, taking advantage of some of [Underscore](http://underscorejs.org/)'s features to help out. The idea was to use "one language for everything" (similar to part of why Node.js is gaining popularity), and I knew I was going to need JavaScript for Mapbox and D3.

Then... I realized that I'm much more used to doing these kinds of operations (file I/O, heavy computation, graph/network modeling) in Python. So I switched to Python.

Are Python and JavaScript the right tools? Well JavaScript is the right tool for Mapbox and D3. But what about the Python part? Could that be in another language? Sure. I'm actually quite interested in the idea if trying to write that part in another language (particularly a language I'm currently trying to learn, like Clojure). But for now, the point is to write it with a language that I know and is suitable for the task, and Python meets those criteria. (Also, since so many people know Python, it makes it easier for others to comment/contribute.)