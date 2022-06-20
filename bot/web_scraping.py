"""
    Author :            Jamie Grant & Pawel Bielinski
    Files :             web_scraping.py
    Last Modified :     23/01/22
    Version :           1.4
    Description :       Web scraping from the national rail website, used for when the user has specified all of the
                        required parameters to retrieve the next available ticket near the date and time that the user
                        has specified.
"""
from bs4 import BeautifulSoup
import requests
import json
def required_info(departure_station, destination_station, date, depart_time):
    """
    :param departure_station: departure station TLC string e.g LCN for Lincoln
    :param destination_station:  destination station TLC string e.g LCN for Lincoln
    :param date: depart date string needed in the format 010222 for 01/02/22
    :param depart_time: the depart time in the format 2100 for 21:00
    :return: returns a string of needed information to book the ticket if ticket found, else an error string is returned
    """
    try:
        link = "https://ojp.nationalrail.co.uk/service/timesandfares" + "/" + departure_station + "/" + destination_station + "/" + date + "/" + depart_time + "/" + "dep?excludeslowertrains"
        # print(link)
        result = requests.get(link)
        doc = BeautifulSoup(result.text, "html.parser")
        depart_string = None
        cheapest = doc.find("table", {"id": "oft"})
        # finding table data labeled has cheapest , as this contains the json of the cheapest available ticket
        cheapest = cheapest.find("td", {"class": "fare has-cheapest"})
        cheapest_p = cheapest.parent
        json_loc = cheapest_p.find("script", {"type": "application/json"})
        # the website has a json payload for all available tickets, which means this can be extracted for chatbot
        # purposes
        if json_loc is not None:
            # loading json string
            jsonData = json.loads(json_loc.text)
            fares = jsonData['singleJsonFareBreakdowns']
            fareprice = fares[0]['fullFarePrice']
            journeybreakdown = jsonData['jsonJourneyBreakdown']
            dep_time = journeybreakdown['departureTime']
            arr_time = journeybreakdown['arrivalTime']
            changes = journeybreakdown['changes']
            depart_string = " The train departs at " + dep_time + " and arrives at " + arr_time + "." + " The price of the ticket to the destination is " + "£" + str(fareprice) + "0"
            link_string = "The booking link : " + link
            return depart_string, link_string
    except Exception as e:
        pass


def required_info_return(departure_station, destination_station, date, depart_time, return_date, return_time):
    """

    :param departure_station: departure station TLC string e.g LCN for Lincoln
    :param destination_station: destination station TLC string e.g LCN for Lincoln
    :param date: depart date string needed in the format 010222 for 01/02/22
    :param depart_time:  the depart time in the format 2100 for 21:00
    :param return_date: return date of train in the format 010222 for 01/02/22
    :param return_time: return time of train in the format 2100 for 21:00
    :return: returns a string of needed information to book the ticket if ticket found, else an error string is returned
    """
    try:
        link = "https://ojp.nationalrail.co.uk/service/timesandfares" + "/" + departure_station + "/" + destination_station + "/" + date + "/" + depart_time + "/" + "dep" + "/" + return_date + "/" + return_time + "/dep"
        result = requests.get(link)
        doc = BeautifulSoup(result.text, "html.parser")
        depart_string = None
        return_string = None
        fareprice = ""
        # finding table data labeled has cheapest , as this contains the json of the cheapest available ticket
        cheapest = doc.find("table", {"id": "oft"})
        cheapest = cheapest.find("td", {"class": "fare has-cheapest"})
        cheapest_p = cheapest.parent
        json_loc = cheapest_p.find("script", {"type": "application/json"})
        if json_loc is not None:
            # loading json string
            jsonData = json.loads(json_loc.text)
            fares = jsonData['singleJsonFareBreakdowns']
            # open return case on website
            # if ticket has open return , the total price for the journey is included in this json, otherwise look for price in the return ticket json
            if jsonData['returnJsonFareBreakdowns'] != []:
                retfares = jsonData['returnJsonFareBreakdowns']
                fareprice = retfares[0]['fullFarePrice']
                journeybreakdown = jsonData['jsonJourneyBreakdown']
                dep_time = journeybreakdown['departureTime']
                arr_time = journeybreakdown['arrivalTime']
                #            changes = journeybreakdown['changes']
                depart_string = " The train departs at " + dep_time + " and arrives at " + arr_time + "." + " This is an off-peak return - any trains permitted on the day"
            else:
                fareprice = fares[0]['fullFarePrice']
                journeybreakdown = jsonData['jsonJourneyBreakdown']
                dep_time = journeybreakdown['departureTime']
                arr_time = journeybreakdown['arrivalTime']
    #            changes = journeybreakdown['changes']
                depart_string = " The train departs at " + dep_time + " and arrives at " + arr_time + "." + " The price of the ticket to the destination is " + "£" + str(
                    fareprice) + "0"

        # RETURN DETAILS
        cheapest_return = doc.find("label", {"id": "returnFareLabel"})
        cheapest_return = cheapest_return.parent.parent
        cheapest_return_p = cheapest_return.parent
        json_loc_2 = cheapest_return_p.find("script", {"type": "application/json"})

        # return ticket information, formatted similarly to the previous case
        if json_loc_2 is not None:
            if jsonData['returnJsonFareBreakdowns'] == []:
                jsonData_r = json.loads(json_loc_2.text)
                fares_r = jsonData_r['singleJsonFareBreakdowns']
                fareprice_r = fares_r[0]['fullFarePrice']
                journeybreakdown_r = jsonData_r['jsonJourneyBreakdown']
                dep_time_r = journeybreakdown_r['departureTime']
                arr_time_r = journeybreakdown_r['arrivalTime']
    #            changes_r = journeybreakdown_r['changes']
                return_string = " The return train departs at " + dep_time_r + " and arrives at " + arr_time_r + "." + " The price of the return ticket is " + "£" + str(
                    fareprice_r) + "0 , in total £" + str(fareprice + fareprice_r) + "0 ."
                link_string = "The booking link : " + link
                return depart_string, return_string, link_string
            else:
                jsonData_r = json.loads(json_loc_2.text)
                fares_r = jsonData_r['singleJsonFareBreakdowns']
                journeybreakdown_r = jsonData_r['jsonJourneyBreakdown']
                dep_time_r = journeybreakdown_r['departureTime']
                arr_time_r = journeybreakdown_r['arrivalTime']
                #            changes_r = journeybreakdown_r['changes']
                return_string = " The return train departs at " + dep_time_r + " and arrives at " + arr_time_r + "." + " The price of the return ticket is " + "£" + str(
                    fareprice) + "0 "
                link_string = "The booking link : " + link
                return depart_string, return_string, link_string
    except Exception as e:
        pass

