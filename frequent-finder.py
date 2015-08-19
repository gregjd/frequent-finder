import csv
import itertools as it
# import json

filename = "data/spokane/stop_times.txt"
f = open(filename, "r")
r = csv.DictReader(f)


def groupBy(iterable, keyfunc):
    """Like itertools.groupby but the results go directly to a dict."""

    groups = it.groupby(iterable, keyfunc)
    groups_dict = {}
    for k, g in groups:
        groups_dict[k] = list(g)

    return groups_dict


# def groupByTripID(r):
#     ig = it.groupby(r, lambda x: x["trip_id"])
#     myDict = {}
#     for k, g in ig:
#         myDict[k] = list(g)

#     # map(lambda x: x, myDict)

#     return


def getTripID(stoptime):
    """Returns the trip_id from a stop time."""

    return stoptime["trip_id"]


def getStopSeq(trip):
    """Returns the stop sequence for a given trip.

    Stop sequence is given as a string of the stop_ids joined by '@' symbols.
    """

    return "@".join(map(lambda x: x["stop_id"], trip))


g = groupBy(groupBy(r, getTripID), getStopSeq)

# map(lambda x: x["stop_id"], myDict["515748"])

f.close()
