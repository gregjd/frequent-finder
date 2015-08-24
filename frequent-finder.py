import csv
# import json


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


def getTripID(stoptime):
    """Returns the trip_id from a stop time."""

    return stoptime["trip_id"]


def getStopSeq(trip):
    """Returns the stop sequence for a given trip.

    Stop sequence is given as a string of the stop_ids joined by '@' symbols.

    Args:
        trip: List of dicts, where the list represents one trip
            and each dict holds the data for a stop on that trip

    Returns:
        A string representing
    """

    # Shouldn't need this:
    if type(trip) != list:
        raise Exception("Argument must be a list.")

    def getStopID(stoptime):

        if "@" not in stoptime["stop_id"]:
            return stoptime["stop_id"]
        else:
            raise Exception("'stop_id' cannot contain the '@' symbol")
            # "@" is being used to join stop_ids together
            # Could modify this function to substitute another character

    return "@".join(map(getStopID, trip))


if __name__ == "__main__":

    print "exec"

    filename = "data/spokane/stop_times.txt"
    f = open(filename, "r")
    r = csv.DictReader(f)

    trips = groupBy(r, getTripID)
    services = groupBy(trips, getStopSeq)

    f.close()
