import csv
# import json


def sortCalendar(cal_file_loc, date):

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
    day_patterns = []
    for day in days:
        if days[day] not in day_patterns:
            day_patterns.append(days[day])
            # Creates a list of unique "day service patterns"
            # so that we only need to check each combination of services
            # once, instead of (say) checking Monday, Tuesday,
            # Wednesday, etc. individually.

    cf.close()
    print ("File closed: " + cal_file_loc)

    return day_patterns


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
        A string of the stop_ids joined by '@' symbols.
    """

    # Shouldn't need this:
    if type(trip) != list:
        raise Exception("Argument must be a list.")

    def getStopID(stop_time):

        if "@" not in stop_time["stop_id"]:
            return stop_time["stop_id"]
        else:
            raise Exception("'stop_id' cannot contain the '@' symbol")
            # "@" is being used to join stop_ids together
            # Could modify this function to substitute another character

    return "@".join(map(getStopID, trip))


def getStopList(stop_seq):
    """Takes a stop sequence string and returns a list of stop IDs."""

    return stop_seq.split("@")


class System:

    def __init__(self, file_loc):

        f = open(filename, "r")
        print ("File opened: " + file_loc)
        r = csv.DictReader(f)

        self.trips = groupBy(r, getTripID)
        print ("Trips aggregated.")

        self.services = groupBy(trips, getStopSeq)
        print ("Services aggregated.")

        f.close()
        print ("File closed: " + file_loc)


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

    def __init__(self, stop_id):

        self.stop_id = stop_id
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

        return

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


class Segment:

    pass


if __name__ == "__main__":

    system = System("data/spokane/stop_times.txt")
    c = sortCalendar("data/spokane/calendar.txt", 20150808)
