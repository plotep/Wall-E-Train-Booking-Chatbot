"""
    Author :            Jamie Grant & Pawel Bielinski
    Files :             wall_e.py
    Last Modified :     23/01/22
    Version :           1.4
    Description :       Knowledge engine for the chatbot.
"""
import itertools

from experta import *
from prediction_module import get_prediction
from nlp import *
from web_scraping import *


def peek(iterable):
    """
    :param iterable: generator
    :return: if generator contains values, return value in the generator
    """
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first, itertools.chain([first], iterable)


class WallE(KnowledgeEngine):

    @DefFacts()
    def _initial_action(self):
        yield Fact(action="greet")

    @Rule(Fact(action='greet'),
          NOT(Fact(book=W())))
    def enter_input(self):
        # initial question that collects necessary facts
        inp = input("How can I help you?")
        facts = match_facts(inp)
        if peek(facts) is None:
            self.declare(Ambiguous())
        else:
            facts = match_facts(inp)
            for fact in facts:
                self.declare(fact)

    # final statement shown when all info is given
    @Rule(AND(DepartTrainStation(MATCH.name), DestinationTrainStation(MATCH.name2), DepartBeforeTime(MATCH.name3),
              DepartDate(MATCH.name4), ReturnYN(True), ReturnDate(MATCH.name5), ReturnTime(MATCH.name6)))
    def print_ticket_info_with_return(self, name, name2, name3, name4, name5, name6):
        train_info = required_info_return(name, name2, name4, name3, name5, name6)
        if train_info is not None:
            for info in train_info:
                print(info)
            self.reset()
            self.run()
        else:
            self.declare(WrongTrainInfo("!"))

    @Rule(AND(DepartTrainStation(MATCH.name), DestinationTrainStation(MATCH.name2), DepartBeforeTime(MATCH.name3),
              DepartDate(MATCH.name4), ReturnYN(False)))
    def print_ticket_info_no_return(self, name, name2, name3, name4):
        train_info = required_info(name, name2, name4, name3)
        if train_info is not None:
            for info in train_info:
                print(info)
            self.reset()
            self.run()
        else:
            self.declare(WrongTrainInfo("!"))

    @Rule(DepartTrainStation(MATCH.name), DestinationTrainStation(MATCH.name2), DepartBeforeTime(MATCH.name3),
          DepartDate(MATCH.name4),NOT(ReturnYN()))
    def check_if_user_wants_return(self):
        inp16 = input("Do you want a return?")
        facts = return_yes_or_no(inp16)
        if facts is not None:
            if facts == "yes":
                self.declare(ReturnYN(True))
            elif facts == "no":
                self.declare(ReturnYN(False))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DestinationTrainStation(), DepartBeforeTime(), DepartDate(), ReturnYN(True),
          ReturnDate(),NOT(ReturnTime()))
    def ask_for_depart_time3(self):
        inp15 = input("What time do you want to return at?")
        facts = find_time_scenario(inp15)
        if facts is not None:
            self.declare(ReturnTime(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DestinationTrainStation(), DepartBeforeTime(), DepartDate(), ReturnYN(True),NOT(ReturnDate()))
    def ask_for_depart_date2(self):
        inp14 = input("What day and month do you want to return at?")
        facts = find_time_scenario(inp14)
        if facts is not None:
            self.declare(ReturnDate(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DestinationTrainStation(), DepartBeforeTime(),NOT(DepartDate()))
    def ask_for_depart_date(self):
        inp13 = input("What day and month do you want to leave at?")
        facts = find_time_scenario(inp13)
        if facts is not None:
            self.declare(DepartDate(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DestinationTrainStation(), DepartDate(),NOT(DepartBeforeTime()))
    def ask_for_depart_time2(self):
        inp12 = input("What time do you want to leave at?")
        facts = find_time_scenario(inp12)
        if facts is not None:
            self.declare(DepartBeforeTime(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DepartBeforeTime(), DepartDate(),NOT(DestinationTrainStation()))
    def ask_for_destination4(self):
        inp11 = input("Which station would you like to go? ")
        facts = find_station(inp11)
        if facts is not None:
            self.declare(DestinationTrainStation(facts))
        else:
            self.declare(Ambiguous())


    @Rule(AND(DepartTrainStation(), DestinationTrainStation()),NOT(DepartBeforeTime()))
    def ask_for_depart_time(self):
        inp10 = input("What time would you like to leave? ")
        facts = find_time_scenario(inp10)
        if facts is not None:
            self.declare(DepartBeforeTime(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DepartBeforeTime(),NOT(DestinationTrainStation()))
    def ask_for_destination3(self):
        inp9 = input("Which station would you like to go? ")
        facts = find_station(inp9)
        if facts is not None:
            self.declare(DestinationTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartTrainStation(), DepartDate(),NOT(DestinationTrainStation()))
    def ask_for_destination2(self):
        inp8 = input("Which station would you like to go? ")
        facts = find_station(inp8)
        if facts is not None:
            self.declare(DestinationTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DestinationTrainStation(), DepartDate(),NOT(DepartTrainStation()))
    def ask_for_depart_station5(self):
        inp7 = input("Which station would you like to set off from? ")
        facts = find_station(inp7)
        if facts is not None:
            self.declare(DepartTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DestinationTrainStation(), DepartBeforeTime(),NOT(DepartTrainStation()))
    def ask_for_depart_station4(self):
        inp6 = input("Which station would you like to set off from? ")
        facts = find_station(inp6)
        if facts is not None:
            self.declare(DepartTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartDate(), DepartBeforeTime(),NOT(DestinationTrainStation()))
    def ask_for_destination(self):
        inp5 = input("Which station would you like to go? ")
        facts = find_station(inp5)
        if facts is not None:
            self.declare(DestinationTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartDate(), NOT(DepartTrainStation()))
    def ask_for_depart_station3(self):
        inp4 = input("Which station would you like to set off from? ")
        facts = find_station(inp4)
        if facts is not None:
            self.declare(DepartTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(DepartBeforeTime(),NOT(DepartTrainStation()))
    def ask_for_depart_station2(self):
        inp3 = input("Which station would you like to set off from? ")
        facts = find_station(inp3)
        if facts is not None:
            self.declare(DepartTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(AND(DestinationTrainStation(),
              NOT(DepartTrainStation(), DepartBeforeTime(), DepartTrainStation(), ReturnYN(), DepartDate(),
                  ReturnDate(), ReturnTime())))
    def ask_for_depart_station(self):
        inp2 = input("Which station would you like to set off from? ")
        facts = find_station(inp2)
        if facts is not None:
            self.declare(DepartTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(AND((DepartTrainStation())),
          NOT(DestinationTrainStation(), DepartBeforeTime(), ReturnYN(), DepartDate(),
              ReturnDate(), ReturnTime()))
    def ask_for_destination(self):
        inp1 = input("Which station would you like to go? ")
        facts = find_station(inp1)
        if facts is not None:
            self.declare(DestinationTrainStation(facts))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),NOT(DelayTime()))
    def ask_for_delay_in_mins(self):
        inp = input("How long is the delay in minutes ? ")
        delay = find_delay_time(inp)
        if delay is not None:
            self.declare(DelayTime(delay))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(),NOT(DelayDestination()))
    def ask_for_journey_dest(self):
        inp = input("Where is your journey going to? ")
        station = find_station(inp)
        if station is not None:
            self.declare(DelayDestination(station))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(),DelayDestination(),NOT(DelayNextStation()))
    def ask_for_next_station(self):
        inp = input("What is your next station? ")
        station = find_station(inp)
        if station is not None:
            self.declare(DelayNextStation(station))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(),DelayDestination(),DelayNextStation(),NOT(DelayNextStationPTA()))
    def ask_for_PTA(self):
        inp = input("What is your PTA ? ")
        station = find_time(inp)
        if station is not None:
            self.declare(DelayNextStationPTA(station))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(),DelayDestination(),DelayNextStation(),DelayNextStationPTA(),NOT(DelayPreviousStationDeparture()))
    def ask_for_previous_station_dep(self):
        inp = input("What is the previous station departure ? ")
        station = find_time(inp)
        if station is not None:
            self.declare(DelayPreviousStationDeparture(station))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(),DelayDestination(),DelayNextStation(),DelayNextStationPTA(),DelayPreviousStationDeparture(),NOT(DelayMonth()))
    def ask_for_month(self):
        inp = input("What is the month ? ")
        station = find_month(inp)
        if station is not None:
            self.declare(DelayMonth(station))
        else:
            self.declare(Ambiguous())

    @Rule(Delay(),DelayTime(MATCH.delayinmins),DelayDestination(MATCH.destination),DelayNextStation(MATCH.nextstation),DelayNextStationPTA(MATCH.nextstationpta),DelayPreviousStationDeparture(MATCH.prevstationdeparture),DelayMonth(MATCH.month))
    def print_delay_time(self,nextstation,destination,nextstationpta,prevstationdeparture,delayinmins,month):
        out = get_prediction(nextstation,destination,nextstationpta,prevstationdeparture,int(delayinmins),int(month))
        if out is not None:
            print("Predicted time : ")
            print(out)
            self.reset()
            self.run()
        else:
            self.declare(WrongTrainInfo())



    @Rule(Ambiguous(), salience=2)
    def ambiguous(self):
        print("Please re-enter your train query - I could not understand you")
        self.retract(len(self.facts) - 1)
        curr_facts = self.facts
        self.reset()
        for facts in curr_facts.values():
            self.declare(facts)
        self.run()

    @Rule(WrongTrainInfo(), salience=3)
    def wrong_train_info(self):
        print("I can't find information of a train with the information you've given me - please check the stations "
              "and dates")
        self.reset()
        self.run()


if __name__ == "__main__":
    engine = WallE()
    engine.reset()
    engine.run()
    # print(get_prediction("UPW","MTN","14:00","13:50",10,1))
