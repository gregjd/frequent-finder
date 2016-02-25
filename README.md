# frequent-finder
A program for auto-generating frequent network maps of public transit systems, using GTFS data as input.

There are two basic pieces to the puzzle. One is taking the GTFS feed and producing a GeoJSON file of the frequent services. The other is taking that GeoJSON and creating a map. I'm interested in three options for creating maps:

* interactive maps (using Mapbox)
* SVGs (using D3), which would probably be not-too-attractive, but would provide a base for editing in a vector graphics program like Illustrator to create a nice static map
* shapefile exports, which could be used in a program like QGIS or ArcGIS to create a static map

![The two parts of the process](/images/FF-OverallFlow.png)

The three main components of FrequentFinder are:

* **frequent-finder.py** (will likely be renamed ff.py): GTFS to GeoJSON, using user-defined parameters for frequency categories
* **ff_mb.js**: GeoJSON to interactive map
* **ff_d3.js**: GeoJSON to SVG

Note that there is no need for me to build something that converts GeoJSON to shapefiles, as this can already be done in existing GIS programs.

See [my website](http://www.gregjd.com/) for links to more of my work.

<br>

### Current status

FrequentFinder works!

Here's Spokane's official transit system map, with frequent services in red:

![Screenshot of Spokane transit map](/images/Spokane_Transit_Map_Screenshot.png)

Here's my GeoJSON export from FrequentFinder, displayed in QGIS:

![Screenshot of FrequentFinder's output for Spokane](/images/Spokane_QGIS_Screenshot_0.png)

Note that my map has fewer frequent services shown because for this one I set frequency parameters that are more strict than those used by the transit authority. (Also, see those short red segments? Those are places where bus lines overlap to create a short frequent corrider. Yes, FrequentFinder handles those easily.)

I am currently working on the Mapbox and D3 portions of this project, and will post them when they are in a useful state. Also note that I am planning to reorganize some of the code in frequent-finder.py/ff.py in order to make it more readable.

I am planning a number of other enhancements to FrequentFinder. I will also write up documentation for how to use FrequentFinder, particularly for people with little coding experience. I'm hoping it will be accessible to "non-coders."

<br>

### Usage

There are several ways you can run frequent-finder.py, but here is one. It requires having Python 2.7 and QGIS installed. This should take about 5-10 minutes if you're doing it for the first time.

**1.** Download the GTFS files for your city of interest. You should be able to find them at the [GTFS Data Exchange](http://www.gtfs-data-exchange.com/agencies), but if you want it to feel more "official" you can go to your transit agency's website and see if they have the data there.

**2.** Create a folder and copy `frequent-finder.py` to the folder. Rename it to `ff.py`. (If you don't have GitHub installed on your computer, you can also just [go to the file](https://github.com/gregjd/frequent-finder/blob/master/frequent-finder.py), copy its contents, paste them into a blank text document using a simple text editor, and name it `ff.py`. Make sure there's no `.txt` extension at the end of the name after you save it.)

**3.** Extract all the GTFS files you downloaded. I recommend placing them in a folder with your city as its name, as a sub-folder of a "data" folder, as a sub-folder of the original folder (containing `ff.py`). See the directory structure of this repo for an example.

**4.** Create a `ff_config.json` file in your folder that has the GTFS data. The basic format should look like [this](https://github.com/gregjd/frequent-finder/blob/master/data/spokane/ff_config.json). Actually, I suggest copying the contents of that file to use as a template. This file is structured as one large array, with each object in the array being a frequency category. The sample values listed should give you a pretty good idea of what kind of input is expected. Specifically:

* `name` is the name for your category.
* `headway` is the maximum headway (time between buses/trains) in minutes.
* `error_mins` is the number of minutes allowed for error, i.e. slight deviations from the maximum headway. If you have a 15-minute headway and a 3-minute error, that means it's okay for two buses/trains to be 18 minutes apart. But...
* `error_pct` is what percent of the time such error is allowed. So a value of 5 means that if you take the minimum number of buses/trains needed to meet the headway standard, and take 5% of that number, that's how many times a headway of `error_mins` is allowed before the corridor in question does not qualify for this frequency standard anymore.
* `rules` is an array of rules for days of the week and start/end times on those days. Include the days of the week for which you want to apply the frequency test. Each rule is an object with three fields: `days`, `start_time`, and `end_time`. If you have multiple rules (most likely in the form of a later `start_time` and earlier `end_time` on the weekends), you should put the rules in order of likely increasing service, i.e. Sundays first, then Saturdays, then weekdays. This will make the program run faster.
* `days` is an array property of a rule. It specifies the days for which the rule's start and end times apply. You'll probably at least want to put all weekdays in here. The days should be all lowercase.
* `start_time` is a property of a rule. It represents the time of day the program should start checking for the headway standard to be met. It should be a four-digit number in 24-hour time, surrounded by quotation marks.
* `end_time` is a property of a rule. It represents the time of day the program should stop checking for the headway standard to be met. It should be a four-digit number in 24-hour time, surrounded by quotation marks.

**5.** Go to your favorite place to run Python. This could be the terminal, IDLE, or wherever. (For me, it's [SublimeREPL](https://github.com/wuub/SublimeREPL).) Type the following commands:
```python
import os
os.chdir("C:/your-folder")
```

Of course, `your-folder` should be the extension for your folder that has `ff.py` in it. If you want to verify that you're in the right place now, type `os.getcwd()` and you should see the correct folder path. Now type:
```python
import ff
freq = ff.System("data/your-city/", 20151001)
```

Note that in the second line, the string argument is the path for the folder containing your GTFS data, with `data/your-city/` being the suggested location, replacing `your-city` with the city name. The second argument to `System` is a number representing a date in YYYYMMDD format. The program will take this date and find the appropriate set of schedules for the time period the date falls within.

After you enter the second line, you should see a bunch of messages indicating files were opened and closed. Then enter:
```python
freq.saveGeoJSON("data/your-city/frequency.geojson")
```

The argument to `saveGeoJSON` should be the location/name of your output GeoJSON file.

**6.** Open up QGIS. Go to add a vector layer (Layer > Add Layer > Add Vector Layer). In the popup box, click *Browse* and find the GeoJSON file. Click *Open*. You should now see a map that looks like your transit system.

**7.** In the list of layers (probably on the left side of the screen), double-click the layer name. On the left side of the popup box, click *Style*. At the top of the main panel, click the drop-down that says *Single Symbol* and change it to *Categorized*. Toward the bottom of the box, click the *Classify* button. The list of frequency categories (that applied to this data set) should be above. The blank category is for corridors that didn't meet any frequency standard. If you double-click on a symbol, you can change its appearance. I recommend thicker lines for more frequent services and the color red for your highest frequency category. When you're done, click *OK* at the bottom of the layer properties box. Voila! Your frequent network map has arrived.

[I will add more in-depth instructions with screenshots for people with little coding/QGIS experience.]

<br>

### Unexpected results

If your resulting frequent network map is not what you envisioned, there could be several reasons.

One is that there's a problem with the data. Remember the good old saying, "garbage in, garbage out." FrequentFinder can only work its magic on what it was given. Hopefully, though, this isn't the issue.

A larger likely culprit is start and end times. FrequentFinder applies the same frequency standard all day from the given `start_time` to the given `end_time`. It does not discriminate as to whether frequency standard violations are in the middle of the day or at the beginning/end, as standards are standards. Try setting a later `start_time` and earlier `end_time` and see if your results change. Also see if your transit agency holds Sunday schedules to the frequency standards.

It could also be that your transit agency is exaggerating its claims. For example, a supposed "15-minute map" might really be a map of services that come four times an hour (e.g. departures at 9:00, 9:10, 9:30, and 9:40). FrequentFinder will sniff this out, even if your agency isn't being upfront about it. Alternatively, it could be that a route/segment often adheres to a frequency standard, but there are more "errors" than you have allowed for in your `ff_config.json` file. And note that a *single* violation of the `error_mins` allowance will disqualify a service from a given frequency category.

Finally, there could be an issue with FrequentFinder. Please let me know if you think this is the case! Due to the complexity of the program and the transit data that's being fed to it, it's hard to say for sure whether your results are accurate or not. I think they should be, but I make no promises. I haven't yet written any test cases of complex systems because that would require going through all the schedules by hand to try to figure out what the results "should" be, and that's not a high priority right now, given how long that would take due to FrequentFinder's precision.

*Note:* Most cities I have tried so far have worked fine, but for some reason San Francisco seems to not be classifying anything in either of my two highest frequency categories. That said, it is still separating all segments into one of two categories, and the lowest-frequency services are correctly being put into the lower category. I need to investigate whether this is accurate (meaning, the problem is with the data itself or the schedule) or if there's a problem with FrequentFinder. I think/hope it's the former, but I'm not sure.

<br>

### Issues and challenges

One of the big challenges of this project is its relationship with the source data. GTFS data is great for "specific" transit information: figuring out what service is available at an exact time and place on an exact day in time. What I'm trying to do is the opposite: create a generalized picture of the transit system. This sparks many questions about how exactly to do this:

* How do you handle days of the week? Holidays? Schedule change dates?
* How do you decide how frequently a line runs? What are the starting and ending times for this query? Do those times apply to all portions of the line or just one location?
* What if buses/trains aren't evenly spaced? What if a line is generally frequent but there are a couple exceptions?
* How do you handle lines that split into branches, or multiple lines that have a shared segment? How do you describe a street has frequent service on all parts of it but different overlapping lines on different segments?
* If multiple lines overlap for just a couple blocks but provide frequent service there, do you really want to count that?
* How do you deal with one-way street pairs? Loops? What do you do if a line visits the same stop twice in a single journey (yes, this really happens)? What if a line visits the same two stops in the same order twice in a single trip (again, this happens --- see London's Circle Line)?
* What do you do about lines with both local service and limited, express, or skip-stop service?
* What do you do if a frequent line splits into two parts for a short section and then the parts rejoin (this is very common)?

All of these issues are present in real-world transit systems. They present serious challenges to any attempt at automating frequent network determination. FrequentFinder needs to be able to deal with them. And it does. That's part of what makes it different from a much simpler frequency-determination program.

<br>

### Motivation

Jarrett Walker, author of the [blog](http://www.humantransit.org/) and [book](http://www.humantransit.org/human-transit-the-book-introduction.html) *Human Transit*, is 100% responsible for inspiring this. He is probably the world's most famous [promoter of frequent network mapping](http://www.humantransit.org/2010/08/basics-the-case-for-frequency-mapping.html), and more generally is the best voice in urban transit I know of. If you don't already read his blog, you really, really, really should.

<br>

### FAQ

**Hasn't someone done this before?**

Yes and no.

Others have certainly thought of the idea. I've seen plenty of people express a [desire](http://seattletransitblog.com/2011/09/12/spokanes-frequent-transit-map/#comment-185795) for something like this. But so far, my web searches have not been very fruitful.

[Conveyal](http://conveyal.com/) has many tools that are useful for analyzing transit, and I haven't yet had time to dig through them all, but at a glance it doesn't seem there's anything that quite does this.

If you [search GitHub](https://github.com/search?utf8=%E2%9C%93&q=transit+frequent+network+map) for "transit frequent network map," this repo is the only result.

The most promising example seems to be [an example](http://www.humantransit.org/2010/09/frequent-network-maps-by-routefriend.html) made by David Marcus at Routefriend. But it appears as if not much has been done since this map. The Routefriend website [has a page](http://www.routefriend.com/frequencymap.html) with a drop-down menu for selecting one of several cities, but I haven't had any luck with it; the page says "Loading (this may take a sec)" but no lines ever appear on the map. Perhaps it once worked but no longer does... or maybe it takes a really long time.

So, no, I haven't found any example that does exactly what I want. Hence my motivation for making FrequentFinder!

There are a few key features about my approach:

* *I want it to be open.* It's all here on GitHub, partially because I believe in open source technology and partially because I'd really like advice on how it can be improved. I also like the idea that other people might be able to use what I've done and do even more great things, like something involving [OpenTripPlanner](http://www.opentripplanner.org/).
* *It should work for any city's GTFS feed.* It seems like the attempts that have been made so far only targeted individual cities. FrequentFinder should work anywhere.
* *I want there to be options users can easily customize.* I don't want to hard-code a frequency standard of 15 minutes into the program. While there are default options, users can choose frequency thresholds, allowable deviation from the standard, starting and ending times of day, days of the week, etc.
* *I'd like interactive mapping to be done on Mapbox.* Part of this is the commitment to open source and part of it is because Mapbox allows for easy customization of styles and has many great base maps.
* *I want to make it easy to use my tools to make things I never considered.* I have a clear separation between finding the frequent network and mapping it, specifically so that people can take the GeoJSON and do whatever they want with it.

**Is this supposed to be a replacement for "hand-drawn" frequent network maps?**

Absolutely not. I feel strongly that custom-drawn, abstract transit maps are superior to auto-generated ones. ([Relevant Human Transit blog post.](http://www.humantransit.org/2010/09/montreal-the-pleasure-of-maps-by-hand.html)) But making the former takes much more time and effort than the latter. FrequentFinder is intended to do a few things that custom-drawn maps can't. Thanks to the fact that they're auto-generated, these maps can:
* serve as frequent network maps for cities where custom-drawn maps don't exist
* allow quick visualization of the effect of service changes on the frequent network
* serve as an inspiration for custom-drawn frequent network maps
(that third reason is probably the most important one)

I want to highlight a [Human Transit post comment by Alon Levy](http://www.humantransit.org/2010/09/transit-network-maps-draw-and-sell-your-own.html?cid=6a00d83454714d69e20133f43d38c0970b#comment-6a00d83454714d69e20133f43d38c0970b): "When I made my New York maps, the main challenge was to collect the set of frequent buses. Drawing was tedious, and I had to make some simplifications for routes that have short one-way pair segments, but it only has to be done once. Ideally, a transit agency would have a customizable map, allowing you to check boxes for all buses you want to see. That would also take care of questions like 10 versus 15 minutes, or [8am-7pm] versus [6am-9pm]." Alon, say hello to FrequentFinder! (Alon's blog, [Pedestrian Observations](https://pedestrianobservations.wordpress.com/), is a must-read.)

So no, I don't see this as an end in itself.

That said, as I continute to develop FrequentFinder, there are certainly features I could add that would enhance its smartness and abstractness:

* simplifying line geometry to make lines smoother
* calculating stop distance/operating speed to determine which lines are rapid transit
* making the background very muted to minimize the importance of minor geographic features


**Why is there no graphical user interface (GUI)?**

Because developing a GUI takes time, and for now I'd rather devote that time and energy toward improving the core capabilities of FrequentFinder. While a GUI would be nice, I think it's far from necessary as the directions for how to use FrequentFinder aren't that complicated.

As it stands, FrequentFinder is not a web app or smartphone app. The reason is simple: it doesn't yet offer the speed for those kinds of uses, and frankly those uses don't matter that much right now. The point of a frequent network map is that it's widely usable. Unlike getting in-the-moment transit directions, this one map is useful for the span of service it applies to (i.e. what hours of the day it's true for). So it wouldn't make any sense to keep generating a new one for the same city unless there's a service change. The point isn't so that you can whip out your smartphone and see the map instantly, though you could certainly do that if you've already generated it; instead, the focus is on building a map that's broadly applicable to many situations, times of day, and days of the week.

In any case, when it comes to navigating a transit system (or just staring at a transit map so you can absort its information), I would strongly suggest looking at a more abstract, custom-drawn one, not these auto-generated ones (though they're much better than nothing!).

**How's the speed?**

This really depends. I've gotten results for Spokane in around 10 seconds, while San Francisco's (SFMTA) took about a minute and a half. The key issues here are how much data there is (particularly in the `stop_times.txt` file) and what the patterns in the data are.

Regardless, this doesn't seem like a big deal right now. For starters, FrequentFinder isn't really about blazing speed, since it's not intended to be an in-the-moment service. The current runtime is fine.

That said, after I've added more core functionality, I will look as possibilities for optimization.

**Why did you choose Python and JavaScript?**

Initially I was actually going to use JavaScript for everything, taking advantage of some of [Underscore](http://underscorejs.org/)'s features to help out. The idea was to use "one language for everything" (similar to part of why Node.js is gaining popularity), and I knew I was going to need JavaScript for Mapbox and D3.

Then... I realized that I'm much more used to doing these kinds of operations (file I/O, heavy computation, graph/network modeling) in Python. So I switched to Python.

Are Python and JavaScript the right tools? Well JavaScript is the right tool for Mapbox and D3. But what about the Python part? Could that be in another language? Sure. I'm actually quite interested in the idea if trying to write that part in another language, mostly for fun. But for now, the point is to write it with a language that I know and is suitable for the task, and Python meets those criteria. (Also, since so many people know Python, it makes it easier for others to comment/contribute.) Rewriting it in another language is not even on my radar screen right now.
