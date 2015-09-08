import csv
import json


def check(cal, js):

    # FIX; also can probably be more elegant
    patterns = []
    for pattern in js: # fix
        name = pattern[u"name"]
        rules_to_check = []
        for rule in pattern[u"rules"]:
            start = rule[u"start_time"].encode("ascii")
            end = rule[u"end_time"].encode("ascii")
            for day in rule[u"days"]:
                d = day.encode("ascii")
                if (cal[d], start, end) not in rules_to_check:
                    rules_to_check.append(cal[d], start, end)
    # Do something regarding 'patterns'
    return patterns


def loadJSON(json_file_loc):

    jf = open(json_file_loc, "r")
    js = json.loads(jf.read())
    jf.close()

    # js.encode("ascii")

    return js


def sortCalendar(cal_file_loc, date):
    """Takes the calendar file (calendar.txt) and matches service patterns
    with days of the week.

    Args:
        cal_file_loc: String location of the calendar file
        date: String date (YYYYMMDD) to be used to find the applicable
            service period

    Returns:
        A dictionary with days as keys and effective service IDs as values
    """

    cf = open(cal_file_loc, "r")
    print ("File opened: " + cal_file_loc)
    cr = csv.DictReader(cf)

    def inDateRange(x):

        return (int(x["start_date"]) < date < int(x["end_date"]))
        # Note: 'date' is as given as a parameter to sortCalendar()

    cl = filter(inDateRange, list(cr))

    # This can almost certainly be written more elegantly:
    days = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }
    for serv in cl:
        for i in serv:
            if i[-3:] == "day": # if key is a day of the week
                if serv[i] == "1":
                    days[i].append(serv["service_id"])
    # # Will leave out this part for now, to possibly be added later
    # # when I decide how to optimize day-handling:
    # day_patterns = []
    # for day in days:
    #     if days[day] not in day_patterns:
    #         day_patterns.append(days[day])
    #         # Creates a list of unique "day service patterns"
    #         # so that we only need to check each combination of services
    #         # once, instead of (say) checking Monday, Tuesday,
    #         # Wednesday, etc. individually.

    cf.close()
    print ("File closed: " + cal_file_loc)

    # return day_patterns
    return days


def groupBy(iterable, keyfunc):
    """Groups items in iterable based on keyfun

    Args:
        iterable: dict (or list) of dicts, containing items to be grouped
        keyfunc: a function that takes an item (from iterable) as its argument;
            used to return the key for groups_dict

    Returns:
        A dict where keys are the groups identified by keyfunc. If the iterable
        is a list, the values of the returned dict will be lists. If the
        iterable is a dict, the values of the returned dict will be dicts.
        As implemented, if iterable is a dict, keyfunc will act on the value
        of each item in the dict; the key will be ignored, though it will be
        included in the returned dict.
    """

    groups_dict = {}
    if type(iterable) == dict:
        for i in iterable:
            key = keyfunc(iterable[i])  # act on the value of the dict item
            if key not in groups_dict:
                groups_dict[key] = {}
            groups_dict[key][i] = iterable[i]
    elif (type(iterable) == list) or (isinstance(iterable, csv.DictReader)):
        for i in iterable:
            key = keyfunc(i)  # act on the list item
            if key not in groups_dict:
                groups_dict[key] = []
            groups_dict[key].append(i)
    else:
        raise Exception("Argument 'iterable' must be a dict or list.")

    return groups_dict


def getTripID(stop_time):
    """Returns the trip_id from a stop time."""

    return stop_time["trip_id"]


def getStopSeq(trip):
    """Returns the stop sequence for a given trip.

    Args:
        trip: List of dicts, where the list represents one trip
            and each dict holds the data for a stop on that trip

    Returns:
        A tuple of the stop_ids.
    """

    # Shouldn't need this:
    if type(trip) != list:
        raise Exception("Argument must be a list.")

    return tuple(map(lambda x: str(x["stop_id"]), trip))


def getStopList(stop_seq):
    """Takes a stop sequence string and returns a list of stop IDs."""

    # return stop_seq.split("@")
    return list(stop_seq)


class System:

    def __init__(self, st_file_loc, s_file_loc):

        sf = open(s_file_loc, "r")
        print ("File opened: " + s_file_loc)
        sr = csv.DictReader(sf)
        self.stops = {} # Dict where keys = stop_ids, values = Stop objects
        for stop in sr:
            self.stops[stop["stop_id"]] = Stop(stop)
        sf.close()
        print ("Stops compiled.")

        f = open(st_file_loc, "r")
        print ("File opened: " + st_file_loc)
        r = csv.DictReader(f)

        self.trips = groupBy(r, getTripID)
        # Takes the stop_times file and returns a dict where
        # keys = trip_ids, values = lists of dicts where
        # each dict is the info for a particular stop on that trip
        print ("Trips aggregated.")

        self.services = groupBy(self.trips, getStopSeq)
        # Takes self.trips and returns a dict where
        # keys = stop sequence tuples, values = dicts from self.trips
        # (where keys = trip_ids, values = lists of stop info dicts)
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
        # Set of the paths that haven't yet been assigned to a Segment
        for serv in self.services:
            current_seg = None
            path_services = None
            for s in range(len(serv)-1):
                path = (serv[s], serv[s+1])
                # path_services = self.paths[path]
                if path not in self.paths_ua:  # Path has already been assigned
                    if current_seg:
                        current_seg.setLastStop(serv[s])
                        self.segments.append(current_seg)
                        current_seg = None
                        path_services = None
                elif self.paths[path] == path_services:  # Continue Segment
                    current_seg.addStop(serv[s])
                    self.paths_ua.remove(path)
                else:  # Path has a different set of services
                    # End current Segment:
                    if current_seg:
                        current_seg.setLastStop(serv[s])
                        self.segments.append(current_seg)
                    # Start new Segment:
                    path_services = self.paths[path]
                    current_seg = Segment(serv[s], path_services)
                    self.paths_ua.remove(path)
        if len(self.paths_ua) > 0:
            raise Exception("Not all paths have been assigned to a Segment.")
        print ("Segments compiled.")

        f.close()
        print ("File closed: " + st_file_loc)


class Route:

    pass


class ServiceGroup:

    pass


class Service:

    def __init__(self, stop_seq):

        self.stop_seq = stop_seq
        self.stop_list = getStopList(stop_seq)
        self.trips = []

    def __repr__(self):

        return self.stop_seq

    def addTrip(self, trip):

        if isinstance(trip, Trip):
            self.trips.append(trip)
        else:
            raise Exception("Trip to add must be an instance of Trip")

    def getStopList(self):

        return self.stop_list


class Trip:

    def __init__(self, trip_id, service, stops_info):

        self.trip_id = trip_id
        self.service = service  # Service that it's a trip of
        self.stops_info = stops_info

        for s in stops_info:
            stop = s["stop_id"]
            time = s["arrival_time"]
            # stops[stop].addTrip(self, time)

    def __repr__(self):

        return self.trip_id

    def getService(self):

        return self.service

    def getStopList(self):

        return self.getService().getStopList()

    def getStopTimes(self):

        pass


class Stop:

    def __init__(self, stop_dict):

        self.stop_id = str(stop_dict["stop_id"])
        self.stop_lon = stop_dict["stop_lon"]
        self.stop_lat = stop_dict["stop_lat"]
        self.stop_name = stop_dict["stop_name"]
        self.stop_desc = stop_dict["stop_desc"]

        self.services = []
        self.trip_times = {} # keys = time points, values = Trips

    def __repr__(self):

        return self.stop_id

    def addTrip(self, trip, time):

        if isinstance(trip, Trip):
            if time not in self.trip_times:
                self.trip_times[time] = []
            self.trip_times[time].append(trip)
            # Allows multiple arrivals at a stop for a given time
        else:
            raise Exception("Trip to add must be an instance of Trip")

        return self

    def addService(self, new):

        # Modify to include number of times each service stops here?
        if isinstance(new, Service):
            if new not in self.services:
                self.services.append(new)
        else:
            raise Exception("Service to add must be an instance of Service")

        return self

    def getServices(self):

        return self.services

    def getLon(self):

        return self.stop_lon

    def getLat(self):

        return self.stop_lat


class Segment:

    def __init__(self, init_stop, services):

        self.init_stop = init_stop
        self.last_stop = None
        self.stops = [init_stop]
        self.services = services

    def addStop(self, stop_id):

        self.stops.append(stop_id)

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


if __name__ == "__main__":

    system = System("data/spokane/stop_times.txt", "data/spokane/stops.txt")
    c = sortCalendar("data/spokane/calendar.txt", 20150808)
    js = loadJSON("ff-config.json")
