import csv
import json
import datetime
import math


class System:

    def __init__(self, data_dir, date):

        self.data_dir = data_dir

        # To-do: break this code into separate functions

        # LOAD JSON CONFIG FILE

        json_file_loc = data_dir + "ff_config.json"
        print ("File opened: " + json_file_loc)
        jf = open(json_file_loc, "r")
        self.js = json.loads(jf.read())
        jf.close()
        print ("File closed: " + json_file_loc)

        # LOAD STOPS FILE

        s_file_loc = data_dir + "stops.txt"
        sf = open(s_file_loc, "r")
        print ("File opened: " + s_file_loc)
        sr = csv.DictReader(sf)
        self.stops = {}  # Dict where keys = stop_ids, values = Stop objects
        for stop in sr:
            self.stops[stop["stop_id"]] = Stop(stop)
        sf.close()
        # print ("Stops compiled.")
        print ("File closed: " + s_file_loc)

        # LOAD STOP_TIMES AND TRIPS FILES

        t_file_loc = data_dir + "trips.txt"
        tf = open(t_file_loc, "r")
        print ("File opened: " + t_file_loc)
        tr = csv.DictReader(tf)
        self.trips = dict((t_dict["trip_id"], Trip(t_dict)) for t_dict in tr)
        print ("File closed: " + t_file_loc)

        st_file_loc = data_dir + "stop_times.txt"
        f = open(st_file_loc, "r")
        print ("File opened: " + st_file_loc)
        r = csv.DictReader(f)

        for st_dict in r:
            st_dict["departure_time"] = fixTime(st_dict["departure_time"])
            st_dict["trip_obj"] = self.trips[st_dict["trip_id"]]
            st_obj = StopTime(st_dict)
            self.trips[st_dict["trip_id"]].addStopTime(st_obj)
            self.stops[st_dict["stop_id"]].addStopTime(st_obj)
        print ("Trips aggregated.")

        self.services = set(t.getStopSeq() for t in self.trips.values())
        # Takes self.trips and returns a set of stop sequence tuples
        print ("Services aggregated.")

        self.paths = {}  # Keys = path tuples (stop0, stop1), values = dicts
        for serv in self.services:
            for s in range(len(serv)-1):
                path = (serv[s], serv[s+1])
                if path not in self.paths:
                    self.paths[path] = {}
                    # Keys = services (stop sequence tuples),
                    # values = number of times that service travels this path
                if serv not in self.paths[path]:
                    self.paths[path][serv] = 1
                else:
                    self.paths[path][serv] += 1
                    # This service travels this path multiple times on a trip
        print ("Paths compiled.")

        self.segments = []  # List of segments
        self.paths_ua = set(self.paths)
        # paths_ua = set of the paths that haven't been assigned to a Segment
        for serv in self.services:
            current_seg = None
            path_services = None
            for s in range(len(serv)-1):
                path = (serv[s], serv[s+1])
                stop_obj = self.stops[serv[s]]
                if path not in self.paths_ua:  # Path has already been assigned
                    if current_seg:
                        current_seg.setLastStop(stop_obj)
                        self.segments.append(current_seg)
                        current_seg = None
                        path_services = None
                elif self.paths[path] == path_services:  # Continue Segment
                    current_seg.addStop(stop_obj)
                    self.paths_ua.remove(path)
                else:  # Path has a different set of services
                    # End current Segment:
                    if current_seg:
                        current_seg.setLastStop(stop_obj)
                        self.segments.append(current_seg)
                    # Start new Segment:
                    path_services = self.paths[path]
                    current_seg = Segment(stop_obj, path_services)
                    self.paths_ua.remove(path)
        if len(self.paths_ua) > 0:
            raise Exception("Not all paths have been assigned to a Segment.")
        print ("Segments compiled.")

        f.close()
        print ("File closed: " + st_file_loc)

        # LOAD CALENDAR FILE

        self.days = sortCalendar(data_dir + "calendar.txt", date)

        # CHECK SEGMENTS

        self.ss = map(assignCategory(self.js, self.days), self.segments)

    def readCSV(self, file_name, function):
        """Reads a CSV file, creates a DictReader, and runs a given function.

        Args:
            file_name: The str name of the file, including '.txt' (or '.csv').
            function: The function to be run, which accepts a single argument
                (the csv.DictReader generated from the CSV)

        Returns:
            Nothing.

        Side effects:
            The side effects of 'function'.
        """

        file_loc = self.data_dir + file_name
        f = open(file_loc, "r")
        print ("File opened: " + file_loc)
        r = csv.DictReader(f)

        function(r)

        f.close()
        print ("File closed: " + file_loc)

        return

    def saveGeoJSON(self, new_file_name):

        print ("Generating GeoJSON export.")

        geoj = {
            "type": "FeatureCollection",
            "features": [s.getJSON() for s in self.ss]
        }

        print ("Saving file: " + new_file_name + " ...")

        nf = open(new_file_name, "w")
        json.dump(geoj, nf, indent=4, sort_keys=True)
        nf.close()

        print ("Saved file: " + new_file_name)

        return


class StopTime:

    def __init__(self, stop_time_dict):

        self.departure_time = stop_time_dict["departure_time"]
        self.trip_id = stop_time_dict["trip_id"]
        self.trip_obj = stop_time_dict["trip_obj"]
        self.stop_id = stop_time_dict["stop_id"]
        self.service_id = self.trip_obj.getServID()
        self.service = self.trip_obj.getStopSeq()

    def getTime(self):

        return self.departure_time

    def getServID(self):

        return self.service_id

    def getTripID(self):

        return self.trip_id

    def getTripObj(self):

        return self.trip_obj

    def getStopID(self):

        return self.stop_id

    def getService(self):

        return self.service


class Trip:

    def __init__(self, trip_dict):

        self.trip_id = trip_dict["trip_id"]
        self.service_id = trip_dict["service_id"]
        self.shape_id = trip_dict["shape_id"]
        self.route_id = trip_dict["route_id"]
        self.stop_times = []

    def addStopTime(self, stop_time):

        self.stop_times.append(stop_time)

        return self

    def getTripID(self):

        return self.trip_id

    def getServID(self):

        return self.service_id

    def getShapeID(self):

        return self.shape_id

    def getRouteID(self):

        return self.route_id

    def getStopTimes(self):

        return self.stop_times

    def getStopSeq(self):

        return tuple(x.getStopID() for x in self.stop_times)

    def getService(self):

        return self.service


class Service:

    def __init__(self):

        self.stop_seq = None

        self.trips = None

    def getStopSeq(self):

        return self.stop_seq

    def getTrips(self):

        return self.trips


class Route:

    pass


class Stop:

    def __init__(self, stop_dict):

        self.stop_id = str(stop_dict["stop_id"])
        self.stop_lon = float(stop_dict["stop_lon"])
        self.stop_lat = float(stop_dict["stop_lat"])
        self.stop_name = stop_dict["stop_name"]
        self.stop_desc = stop_dict["stop_desc"]

        self.trip_times = {}  # keys = time points, values = Trips
        self.stop_times = []  # list of StopTime objects

    def __repr__(self):

        return ("Stop " + self.stop_id)

    def addStopTime(self, stop_time):

        self.stop_times.append(stop_time)

        return self

    def getStopTimes(self, filter_func=None):

        if filter_func:
            return filter(filter_func, self.stop_times)
        else:
            return self.stop_times

    def getLonLat(self):

        return [self.stop_lon, self.stop_lat]


class Segment:

    def __init__(self, init_stop, services):

        # Note: All stops are Stop objects, not stop_ids
        self.init_stop = init_stop
        self.last_stop = None
        self.stops = [init_stop]
        self.services = services

        self.category = None

    def setCategory(self, category):

        self.category = category

        return self

    def addStop(self, stop):

        self.stops.append(stop)

        return self

    def setLastStop(self, last_stop):

        self.addStop(last_stop)
        self.last_stop = last_stop

        return self

    def getInitStop(self):

        return self.init_stop

    def getLastStop(self):

        return self.last_stop

    def getStops(self):

        return self.stops

    def getServices(self):

        return self.services

    def getJSON(self):

        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [s.getLonLat() for s in self.stops]
            },
            "properties": {
                "category": self.category
            }
        }


def assignCategory(js, days):
    """Returns a function that assigns a frequency category to a Segment."""

    def assignCategoryFunc(segment):

        # Not really necessary, but here for safety:
        if not isinstance(segment, Segment):
            raise Exception("Argument 'segment' must be a Segment.")

        return segment.setCategory(findCategory(segment, js, days))

    return assignCategoryFunc


def findCategory(segment, js, days):
    """Finds the appropriate frequency pattern for a given Segment.

    Proceeds through the JSON contents in order, so if the JSON config file
    (ff-config.json) contains multiple frequency categories, they should be
    in order of decreasing frequency, as this function will return the first
    category whose standards are met for that segment.
    """

    for pattern in js:
        if checkPattern(segment, pattern, days):
            return pattern["name"]
    return None


def checkPattern(segment, pattern, days):

    def checkStop(stop):

        def checkRule(r):

            def checkCombo(c):

                # Get stop times for this day and time range:
                times = stop.getStopTimes(
                    lambda st: (bool(st.getServID() in c)) &
                    # (st.getService() in segment.getServices()) &
                    (r[u"start_time"] < st.getTime() < r[u"end_time"])
                )
                times = sorted(times, key=lambda st: st.getTime())
                times = [convertTime(st.getTime()) for st in times]

                # Create fake stop times to represent the start and end times
                times.insert(0, start)
                times.append(end)

                # Check if there are enough total trips in the day:
                if len(times) < min_trips-3:  # -3 in case of weird edge cases
                    return False

                # Go through all stop times and check headways:
                errors = 0
                for i in range(len(times)-1):
                    if (times[i+1] - times[i]) > headway:
                        if (times[i+1] - times[i]) <= (headway + error_mins):
                            errors += 1
                        else:
                            return False
                    if errors > error_times:
                        return False

                return True

            # Get unique combinations of service_ids for the days in this rule:
            combos = set(tuple(days[x.encode("ascii")]) for x in r[u"days"])

            # Calculate allowable error:
            # (Note: expects start and end times as strings in "HHMM" format)
            start = datetime.timedelta(
                hours=int(r["start_time"].encode("ascii")[0:2]),
                minutes=int(r["start_time"].encode("ascii")[2:4])
            )
            end = datetime.timedelta(
                hours=int(r["end_time"].encode("ascii")[0:2]),
                minutes=int(r["end_time"].encode("ascii")[2:4])
            )
            duration = end - start
            headway = datetime.timedelta(minutes=pattern[u"headway"])
            min_trips = int(duration.total_seconds()/headway.total_seconds())
            error_mins = datetime.timedelta(minutes=pattern[u"error_mins"])
            error_times = int(math.ceil(pattern[u"error_pct"]*0.01*min_trips))

            for c in combos:
                if not checkCombo(c):
                    return False
            return True

        for rule in pattern[u"rules"]:
            if not checkRule(rule):
                return False
        return True

    # Check the init stop across all days before checking the last stop,
    # because it's unlikely the two will have different results for checkStop,
    # so we might as well try to return a False value as soon as possible.
    if not checkStop(segment.getInitStop()):
        return False
    elif not checkStop(segment.getLastStop()):
        return False
    return True


def sortCalendar(cal_file_loc, date):
    """Takes the calendar file (calendar.txt) and matches service patterns
    with days of the week.

    Args:
        cal_file_loc: String location of the calendar file
        date: Int/string date (YYYYMMDD) to be used to find the applicable
            service period

    Returns:
        A dict where keys = days, values = sets of effective service IDs
    """

    cf = open(cal_file_loc, "r")
    print ("File opened: " + cal_file_loc)
    cr = csv.DictReader(cf)

    def inDateRange(x):

        return (int(x["start_date"]) < int(date) < int(x["end_date"]))

    cl = filter(inDateRange, list(cr))
    days = {
        "monday": set(),
        "tuesday": set(),
        "wednesday": set(),
        "thursday": set(),
        "friday": set(),
        "saturday": set(),
        "sunday": set()
    }
    for serv in cl:
        for i in serv:
            if i[-3:] == "day":  # if key is a day of the week
                if serv[i] == "1":  # if this service_id applies on this day
                    days[i].add(serv["service_id"])

    cf.close()
    print ("File closed: " + cal_file_loc)

    return days


def fixTime(time):
    """Takes a str time and converts the hour to a two-digit value if needed.

    Needed because GTFS allows AM (morning) times to have a one- or two-digit
    hour, but sorting string times requires two-digit hours to work properly.
    """

    if time.find(":") == 2:
        return time
    elif time.find(":") == 1:
        return "0" + time
    else:
        raise Exception("Time must begin with a one- or two-digit hour.")


def convertTime(time):
    """Converts a str time ("HH:MM:SS") to a datetime.timedelta object."""

    h, m, s = time.split(":")

    return datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))


if __name__ == "__main__":

    # system = System("data/spokane/", "ff-config.json", 20150808)
    system2 = System("data/spokane/", 20150808)
    system2.saveGeoJSON("data/spokane/frequency2.geojson")
