"""
    Author :            Jamie Grant & Pawel Bielinski
    Files :             prediction.py
    Last Modified :     23/01/22
    Version :           1.4
    Description :       Experta facts classes used for the knowledge engine.
"""

from experta import Fact


class WrongTrainInfo(Fact):
    pass


class InputFact(Fact):
    pass


class ReturnYN(Fact):
    pass


class DepartTrainStation(Fact):
    pass


class DestinationTrainStation(Fact):
    pass


class ArriveTrainStation(Fact):
    pass


class DepartBeforeTime(Fact):
    pass


class DepartDate(Fact):
    pass


class ArrivalTime(Fact):
    pass


class ReturnDate(Fact):
    pass


class ReturnTime(Fact):
    pass


class Ambiguous(Fact):
    pass


class Delay(Fact):
    pass


class DelayTime(Fact):
    pass


class DelayDestination(Fact):
    pass

class DelayNextStation(Fact):
    pass


class DelayNextStationPTA(Fact):
    pass


class DelayPreviousStationDeparture(Fact):
    pass


class DelayMonth(Fact):
    pass
